from httpx import AsyncClient, RequestError
from asyncio import sleep
from logging import getLogger, basicConfig, INFO

from exceptions import FlightDataFetchError
from datetime import datetime, timedelta
from typing import List
from models import FlightEvent, Journey


basicConfig(level=INFO)
logger = getLogger(__name__)

API_URL = "https://mock.apidog.com/m1/814105-793312-default/flight-events"
MAX_RETRIES = 3
TIMEOUT = 5.0


async def fetch_flight_events() -> List[FlightEvent]:
    """
    Fetches flight events from the external API with retry mechanism.

    Returns:
        List[FlightEvent]: A list of flight events if successful.

    Raises:
        Exception: If the API is unreachable after multiple attempts.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with AsyncClient(timeout=TIMEOUT) as client:
                response = await client.get(API_URL)

                if response.status_code == 200:
                    flight_data = response.json()
                    return [FlightEvent(**event) for event in flight_data]

                logger.warning(
                    f"Attempt {attempt}: API responded with {response.status_code}"
                )

        except RequestError as e:
            logger.error(f"Attempt {attempt}: Failed to connect to API: {e}")

        await sleep(2)

    logger.critical("Failed to fetch data from API after multiple attempts.")
    raise FlightDataFetchError()


async def search_journeys(date: str, origin: str, destination: str) -> List[Journey]:
    """
    Searches for valid journeys (direct or with one connection) from an origin to a destination.

    Args:
        date (str): The travel date in 'YYYY-MM-DD' format.
        origin (str): The IATA code of the departure city.
        destination (str): The IATA code of the arrival city.

    Returns:
        List[Journey]: A list of valid journeys matching the criteria.
    """

    all_flights = await fetch_flight_events()

    # Extract unique locations from flight data
    known_origins = {flight.departure_city for flight in all_flights}
    known_destinations = {flight.arrival_city for flight in all_flights}

    # Check if origin and destination exist in available flights
    if origin not in known_origins:
        logger.warning(f"No available flights departing from '{origin}'.")
        return []

    if destination not in known_destinations:
        logger.warning(f"No available flights arriving at '{destination}'.")
        return []

    # Convert date string to datetime object (UTC midnight)
    search_date = datetime.strptime(date, "%Y-%m-%d")

    # Filter flights that operate on the requested date
    flights = [
        flight
        for flight in all_flights
        if search_date.date()
        <= flight.departure_datetime.date()
        <= (search_date + timedelta(days=1)).date()
    ]

    direct_flights = []
    connecting_flights = []

    # Search for direct flights
    for flight in flights:
        if flight.departure_city == origin and flight.arrival_city == destination:
            if (flight.arrival_datetime - flight.departure_datetime) <= timedelta(
                hours=24
            ):  # Flight duration within 24 hours
                direct_flights.append(Journey(connections=0, path=[flight]))

    # Search for connecting flights
    for flight1 in flights:
        if flight1.departure_city == origin:
            for flight2 in flights:
                if (
                    flight1.arrival_city
                    == flight2.departure_city  # Connection city matches
                    and flight2.arrival_city == destination  # Final destination matches
                    and timedelta(hours=0)
                    <= (flight2.departure_datetime - flight1.arrival_datetime)
                    <= timedelta(hours=4)  # Valid layover time
                    and (flight2.arrival_datetime - flight1.departure_datetime)
                    <= timedelta(hours=24)
                    # Total journey within 24 hours
                ):
                    connecting_flights.append(
                        Journey(connections=1, path=[flight1, flight2])
                    )

    valid_journeys = direct_flights + connecting_flights
    if not valid_journeys:
        logger.info(
            f"No journeys available for the route {origin} → {destination} on {date}."
        )
    return valid_journeys
