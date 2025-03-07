from datetime import datetime, timezone, timedelta

import pytest
import httpx
from httpx import Response

from exceptions import FlightDataFetchError
from services import fetch_flight_events, MAX_RETRIES
from models import FlightEvent
from unittest.mock import AsyncMock, patch

now = datetime.now(timezone.utc)

API_MOCK_DATA = [
    {
        "flight_number": "XX1234",
        "departure_city": "BUE",
        "arrival_city": "MAD",
        "departure_datetime": (now + timedelta(days=2, hours=12)).isoformat(),
        "arrival_datetime": (now + timedelta(days=2, hours=24)).isoformat(),
    }
]


@pytest.mark.asyncio
async def test_fetch_flight_events_success():
    mock_data = [
        {
            "flight_number": "IB1234",
            "departure_city": "MAD",
            "arrival_city": "BUE",
            "departure_datetime": (now + timedelta(days=4, hours=13)).isoformat(),
            "arrival_datetime": (now + timedelta(days=4, hours=14)).isoformat(),
        }
    ]

    mock_response = Response(200, json=mock_data)

    with patch("services.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        result = await fetch_flight_events()

        mock_instance.get.assert_called_once()
        expected_departure = (now + timedelta(days=4, hours=13)).astimezone(
            timezone.utc
        )
        expected_arrival = (now + timedelta(days=4, hours=14)).astimezone(timezone.utc)

        assert len(result) == 1
        assert isinstance(result[0], FlightEvent)
        assert result[0].flight_number == "IB1234"
        assert result[0].departure_city == "MAD"
        assert result[0].arrival_city == "BUE"
        assert result[0].departure_datetime == expected_departure
        assert result[0].arrival_datetime == expected_arrival


@pytest.mark.asyncio
async def test_fetch_flight_events_http_error():
    mock_response = Response(500)

    with patch("services.AsyncClient") as mock_client, patch(
        "services.sleep", AsyncMock()
    ) as mock_sleep:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_instance

        # The function should retry MAX_RETRIES times and then raise an exception
        with pytest.raises(FlightDataFetchError):
            await fetch_flight_events()

        # Check that get was called MAX_RETRIES times
        assert mock_instance.get.call_count == MAX_RETRIES
        # Check that sleep was called MAX_RETRIES
        assert mock_sleep.call_count == MAX_RETRIES


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_fetch_flight_events_permanent_failure(mock_get):
    """Test API failing all retries and raising an exception."""
    mock_get.side_effect = httpx.RequestError("API Unreachable")

    with pytest.raises(
        FlightDataFetchError,
        match="Could not retrieve flight data after multiple attempts.",
    ):
        await fetch_flight_events()
