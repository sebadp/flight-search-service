from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, patch
from models import FlightEvent

# Generate future dynamic test dates
TODAY = datetime.now().date()
FUTURE_DATE_1 = (TODAY + timedelta(days=2)).strftime("%Y-%m-%d")
FUTURE_DATE_2 = (TODAY + timedelta(days=3)).strftime("%Y-%m-%d")
PAST_DATE = (TODAY - timedelta(days=1)).strftime("%Y-%m-%d")

now = datetime.now()

MOCK_FLIGHTS = [
    FlightEvent(
        flight_number="XX1234",
        departure_city="BUE",
        arrival_city="MAD",
        departure_datetime=(now + timedelta(days=2, hours=12)).isoformat() + "Z",
        arrival_datetime=(now + timedelta(days=2, hours=24)).isoformat() + "Z",
    ),
    FlightEvent(
        flight_number="XX2345",
        departure_city="MAD",
        arrival_city="PMI",
        departure_datetime=(now + timedelta(days=3, hours=2)).isoformat() + "Z",
        arrival_datetime=(now + timedelta(days=3, hours=3)).isoformat() + "Z",
    ),
    FlightEvent(
        flight_number="XX3456",
        departure_city="BUE",
        arrival_city="MIA",
        departure_datetime=(now + timedelta(days=2, hours=14)).isoformat() + "Z",
        arrival_datetime=(now + timedelta(days=2, hours=22)).isoformat() + "Z",
    ),
    FlightEvent(
        flight_number="XX4567",
        departure_city="MIA",
        arrival_city="JFK",
        departure_datetime=(now + timedelta(days=3, hours=1)).isoformat() + "Z",
        arrival_datetime=(now + timedelta(days=3, hours=5)).isoformat() + "Z",
    ),
    FlightEvent(
        flight_number="XX5678",
        departure_city="MAD",
        arrival_city="PMI",
        departure_datetime=(now + timedelta(days=3, hours=8)).isoformat() + "Z",
        arrival_datetime=(now + timedelta(days=3, hours=9)).isoformat() + "Z",
    ),
    FlightEvent(
        flight_number="XX6789",
        departure_city="BUE",
        arrival_city="LON",
        departure_datetime=(now + timedelta(days=2, hours=10)).isoformat() + "Z",
        arrival_datetime=(now + timedelta(days=4, hours=12)).isoformat() + "Z",
    ),
]


@pytest.fixture
def client():
    """Provides a FastAPI test client."""
    return TestClient(app)


@patch("services.fetch_flight_events", new_callable=AsyncMock)
def test_api_no_matches(mock_fetch_flight_events, client):
    mock_fetch_flight_events.return_value = []
    date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    response = client.get(
        "/journeys/search", params={"date": date, "origin": "BUE", "destination": "SFO"}
    )
    assert response.status_code == 200
    assert (
        response.json()["message"]
        == f"No journeys available for route BUE → SFO on {date}"
    )


@patch("services.fetch_flight_events", new_callable=AsyncMock)
def test_api_search_valid_direct_flight(mock_fetch_flight_events, client):
    """Test searching for a valid direct flight."""
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS

    response = client.get(
        "/journeys/search",
        params={"date": FUTURE_DATE_1, "origin": "BUE", "destination": "MAD"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["connections"] == 0
    assert data[0]["path"][0]["flight_number"] == "XX1234"


@patch("services.fetch_flight_events", new_callable=AsyncMock)
def test_api_search_multiple_direct_flights(mock_fetch_flight_events, client):
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS
    response = client.get(
        "/journeys/search",
        params={
            "date": (now + timedelta(days=2)).strftime("%Y-%m-%d"),
            "origin": "BUE",
            "destination": "MIA",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["connections"] == 0
    assert data[0]["path"][0]["flight_number"] == "XX3456"


@patch("services.fetch_flight_events", new_callable=AsyncMock)
def test_api_search_valid_connection(mock_fetch_flight_events, client):
    """Test searching for a valid connecting flight."""
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS

    response = client.get(
        "/journeys/search",
        params={"date": FUTURE_DATE_1, "origin": "BUE", "destination": "PMI"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["connections"] == 1
    assert data[0]["path"][0]["flight_number"] == "XX1234"
    assert data[0]["path"][1]["flight_number"] == "XX2345"


@patch("services.fetch_flight_events", new_callable=AsyncMock)
def test_api_long_wait_time(mock_fetch_flight_events, client):
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS

    response = client.get(
        "/journeys/search",
        params={
            "date": (now + timedelta(days=2)).strftime("%Y-%m-%d"),
            "origin": "BUE",
            "destination": "PMI",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Verify that the journey with the invalid 6-hour connection is NOT included
    for journey in data:
        for flight in journey["path"]:
            assert flight["flight_number"] != "XX5678"  # This should be filtered out


@patch("services.fetch_flight_events", new_callable=AsyncMock)
def test_api_total_duration_exceeds_24_hours(mock_fetch_flight_events, client):
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS
    date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    response = client.get(
        "/journeys/search", params={"date": date, "origin": "BUE", "destination": "LON"}
    )

    assert response.status_code == 200
    assert (
        response.json()["message"]
        == f"No journeys available for route BUE → LON on {date}"
    )  # The only match exceeds 24 hours, so no valid journeys


def test_api_invalid_date_format(client):
    """Test API rejects an invalid date format."""
    response = client.get(
        "/journeys/search",
        params={"date": "12-09-2024", "origin": "BUE", "destination": "MAD"},
    )

    assert response.status_code == 422
    assert "String should match pattern" in response.text


def test_api_invalid_origin_iata_code(client):
    """Test API rejects an invalid IATA code."""
    response = client.get(
        "/journeys/search",
        params={"date": FUTURE_DATE_1, "origin": "BUEE", "destination": "MAD"},
    )

    assert response.status_code == 422
    assert "String should have at most 3 characters" in response.text


def test_api_invalid_destination_iata_code(client):
    """Test API rejects an invalid IATA code."""
    response = client.get(
        "/journeys/search",
        params={"date": FUTURE_DATE_1, "origin": "BUE", "destination": "AD"},
    )

    assert response.status_code == 422
    assert "String should have at least 3 characters" in response.text


def test_api_invalid_arrival_time():
    """Test that arrival time cannot be before departure time."""
    with pytest.raises(ValueError, match="Arrival time must be after departure time."):
        FlightEvent(
            flight_number="XX9999",
            departure_city="BUE",
            arrival_city="MAD",
            departure_datetime=(
                datetime.now() + timedelta(days=2, hours=14)
            ).isoformat()
            + "Z",
            arrival_datetime=(datetime.now() + timedelta(days=2, hours=13)).isoformat()
            + "Z",
        )


def test_api_missing_arrival_city(client):
    response = client.get(
        "/journeys/search",
        params={
            "date": (now + timedelta(days=2)).strftime("%Y-%m-%d"),
            "origin": "BUE",
        },
    )
    assert response.status_code == 422


def test_api_missing_departure_city(client):
    response = client.get(
        "/journeys/search",
        params={
            "date": (now + timedelta(days=2)).strftime("%Y-%m-%d"),
            "destination": "MAD",
        },
    )
    assert response.status_code == 422


def test_api_past_date(client):
    """Test API rejects a past date."""
    response = client.get(
        "/journeys/search",
        params={"date": PAST_DATE, "origin": "BUE", "destination": "MAD"},
    )

    assert response.status_code == 400
    assert "Search date must be in the future" in response.text
