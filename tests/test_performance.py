from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch
from models import FlightEvent


@pytest.fixture
def client():
    """Provides a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def huge_flight_dataset():
    # Fixed reference date for deterministic testing
    REF_DATE = datetime(2024, 1, 15, 0, 0)  # Arbitrary fixed date

    def generate_flight(
        flight_number, dep_city, arr_city, minutes_offset, duration_hours
    ):
        departure = REF_DATE + timedelta(minutes=minutes_offset)
        return FlightEvent(
            flight_number=flight_number,
            departure_city=dep_city,
            arrival_city=arr_city,
            departure_datetime=departure.isoformat() + "Z",
            arrival_datetime=(departure + timedelta(hours=duration_hours)).isoformat()
            + "Z",
        )

    flights = []
    ORIGIN = "ORG"
    DESTINATION = "DST"
    HUB = "HUB"

    # Direct flights (all within valid date range)
    for i in range(5000):
        flights.append(
            generate_flight(
                flight_number=f"DIR{i}",
                dep_city=ORIGIN,
                arr_city=DESTINATION,
                minutes_offset=i,  # Within same day
                duration_hours=2,
            )
        )

    # Connecting flights (valid layovers)
    for i in range(10000):
        # First leg (ORG → HUB)
        flight_a = generate_flight(
            flight_number=f"CONN_A{i}",
            dep_city=ORIGIN,
            arr_city=HUB,
            minutes_offset=i,
            duration_hours=2,
        )

        # Second leg (HUB → DST) with EXACTLY 2h10m layover
        flight_b = generate_flight(
            flight_number=f"CONN_B{i}",
            dep_city=HUB,
            arr_city=DESTINATION,
            minutes_offset=i + 130,  # 2h10m after flight_a arrives
            duration_hours=1.5,
        )

        flights.extend([flight_a, flight_b])

    return {"flights": flights, "expected_direct": 2880, "expected_connecting": 636185}


@pytest.mark.skip(reason="Performance test; run manually when needed")
@patch("services.fetch_flight_events", new_callable=AsyncMock)
def test_search_huge_dataset_performance(
    mock_fetch_flight_events, client, huge_flight_dataset
):
    """
    Test the performance of searching a huge dataset of flights. 639065 journeys are expected.
    :param mock_fetch_flight_events:
    :param client:
    :param huge_flight_dataset:
    :return:
    [100%]Elapsed time: 15.605517 seconds for 639065 journeys
    """
    mock_fetch_flight_events.return_value = huge_flight_dataset["flights"]
    test_date = "2024-01-15"  # Matches the fixed reference date
    t0 = datetime.now()
    response = client.get(
        "/journeys/search", params={"date": test_date, "from": "ORG", "to": "DST"}
    )
    elapsed = (datetime.now() - t0).total_seconds()
    assert response.status_code == 200
    data = response.json()

    direct_count = len([j for j in data if j["connections"] == 0])
    connecting_count = len([j for j in data if j["connections"] == 1])
    assert direct_count == huge_flight_dataset["expected_direct"]
    assert connecting_count == huge_flight_dataset["expected_connecting"]
    print(f"Elapsed time: {elapsed} seconds for {len(data)} journeys")
