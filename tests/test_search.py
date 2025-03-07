import pytest
from datetime import datetime, timedelta
from services import search_journeys
from models import FlightEvent
from unittest.mock import AsyncMock, patch


now = datetime.now()

MOCK_FLIGHTS = [
    # Direct Flight
    FlightEvent(
        flight_number="XX1234",
        departure_city="BUE",
        arrival_city="MAD",
        departure_datetime=(now + timedelta(days=2, hours=12)).isoformat() + "Z",
        arrival_datetime=(now + timedelta(days=2, hours=24)).isoformat() + "Z",
    ),
    # Connecting Flights (Valid)
    FlightEvent(
        flight_number="XX2345",
        departure_city="MAD",
        arrival_city="PMI",
        departure_datetime=(now + timedelta(days=3, hours=2)).isoformat() + "Z",
        arrival_datetime=(now + timedelta(days=3, hours=3)).isoformat() + "Z",
    ),
    # Invalid Connection (layover too long)
    FlightEvent(
        flight_number="XX3456",
        departure_city="MAD",
        arrival_city="PMI",
        departure_datetime=(now + timedelta(days=3, hours=7)).isoformat()
        + "Z",  # Layover of 7 hours (invalid)
        arrival_datetime=(now + timedelta(days=3, hours=8)).isoformat() + "Z",
    ),
    # Invalid Journey (exceeds 24 hours)
    FlightEvent(
        flight_number="XX4567",
        departure_city="MAD",
        arrival_city="BCN",
        departure_datetime=(now + timedelta(days=4, hours=13)).isoformat() + "Z",
        arrival_datetime=(now + timedelta(days=4, hours=14)).isoformat() + "Z",
    ),
]


@pytest.mark.asyncio
@patch("services.fetch_flight_events", new_callable=AsyncMock)
async def test_search_journeys_direct(mock_fetch_flight_events):
    """Test finding direct flights."""
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS
    date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    journeys = await search_journeys(date, "BUE", "MAD")

    assert len(journeys) == 1
    assert journeys[0].connections == 0
    assert journeys[0].path[0].flight_number == "XX1234"


@pytest.mark.asyncio
@patch("services.fetch_flight_events", new_callable=AsyncMock)
async def test_search_journeys_with_connection(mock_fetch_flight_events):
    """Test finding valid connecting flights."""
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS
    date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    journeys = await search_journeys(date, "BUE", "PMI")

    assert len(journeys) == 1
    assert journeys[0].connections == 1
    assert journeys[0].path[0].flight_number == "XX1234"
    assert journeys[0].path[1].flight_number == "XX2345"


@pytest.mark.asyncio
@patch("services.fetch_flight_events", new_callable=AsyncMock)
async def test_search_journeys_no_valid_connections(mock_fetch_flight_events):
    """Test that journeys with long layovers or exceeding 24 hours are not included."""
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS
    date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    journeys = await search_journeys(date, "BUE", "BCN")

    assert len(journeys) == 0


@pytest.mark.asyncio
@patch("services.fetch_flight_events", new_callable=AsyncMock)
async def test_search_journeys_no_flights(mock_fetch_flight_events):
    """Test that no flights are found for the given date."""
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS
    date = (now + timedelta(days=5)).strftime("%Y-%m-%d")
    journeys = await search_journeys(date, "BUE", "MAD")

    assert len(journeys) == 0


@pytest.mark.asyncio
@patch("services.fetch_flight_events", new_callable=AsyncMock)
async def test_search_journeys_invalid_origin(mock_fetch_flight_events):
    """Test handling an unknown origin gracefully."""
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS
    date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    journeys = await search_journeys(date, "XYZ", "MAD")

    assert journeys == []


@pytest.mark.asyncio
@patch("services.fetch_flight_events", new_callable=AsyncMock)
async def test_search_journeys_invalid_destination(mock_fetch_flight_events):
    """Test handling an unknown destination gracefully."""
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS
    date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    journeys = await search_journeys(date, "BUE", "XYZ")

    assert journeys == []


@pytest.mark.asyncio
@patch("services.fetch_flight_events", new_callable=AsyncMock)
async def test_search_journeys_no_valid_routes(mock_fetch_flight_events):
    """Test handling a valid origin/destination but no possible journeys."""
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS
    date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    journeys = await search_journeys(date, "BUE", "BCN")

    assert journeys == []


@pytest.mark.asyncio
@patch("services.fetch_flight_events", new_callable=AsyncMock)
async def test_search_journeys_no_valid_routes(mock_fetch_flight_events):
    """Test handling a valid origin/destination but no possible journeys."""
    mock_fetch_flight_events.return_value = MOCK_FLIGHTS
    date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
    journeys = await search_journeys(date, "BE", "CN")

    assert journeys == []
