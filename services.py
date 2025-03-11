from httpx import AsyncClient, RequestError
from asyncio import sleep
from logging import getLogger, basicConfig, INFO
from os import getenv

from exceptions import FlightDataFetchError
from datetime import datetime, timedelta
from typing import List, Dict
from models import FlightEvent, Journey


basicConfig(level=INFO)
logger = getLogger(__name__)

API_URL = getenv("API_URL")
MAX_RETRIES = int(getenv("MAX_RETRIES", 3))
TIMEOUT = float(getenv("TIMEOUT", 5.0))


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

                logger.debug(
                    f"Attempt {attempt}: API responded with {response.status_code}"
                )

        except RequestError as e:
            logger.info(f"Attempt {attempt}: Failed to connect to API: {e}")

        await sleep(2)

    logger.error("Failed to fetch data from API after multiple attempts.")
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
    search_date = datetime.strptime(date, "%Y-%m-%d")

    # Filter flights that operate on the requested date range
    flights = filter_flights_by_date(all_flights, search_date)

    # Build indexes for efficient lookups
    flights_by_departure = build_flights_index_by_departure(flights)

    # Early exit if there are no flights departing from origin or arriving at destination
    if origin not in flights_by_departure:
        logger.warning(f"No available flights departing from '{origin}'.")
        return []
    if destination not in [f.arrival_city for f in flights]:
        logger.warning(f"No available flights arriving at '{destination}'.")
        return []

    # Retrieve direct and connecting journeys using the indexes
    direct_flights = get_direct_flights(
        flights_by_departure.get(origin, []), destination
    )
    connecting_flights = get_connecting_flights(
        flights_by_departure, origin, destination
    )

    valid_journeys = direct_flights + connecting_flights
    if not valid_journeys:
        logger.info(
            f"No journeys available for the route {origin} → {destination} on {date}."
        )
    return valid_journeys


def filter_flights_by_date(
    flights: List[FlightEvent], search_date: datetime
) -> List[FlightEvent]:
    """
    Filters flights that operate on the requested date (from midnight of search_date to before midnight the next day).
    """
    next_date = search_date + timedelta(days=1)
    return [
        flight
        for flight in flights
        if search_date.date() <= flight.departure_datetime.date() <= next_date.date()
    ]


def build_flights_index_by_departure(
    flights: List[FlightEvent],
) -> Dict[str, List[FlightEvent]]:
    """
    Builds an index of flights keyed by departure city.
    """
    index = {}
    for flight in flights:
        index.setdefault(flight.departure_city, []).append(flight)
    return index


def get_direct_flights(
    flights_from_origin: List[FlightEvent], destination: str
) -> List[Journey]:
    """
    Extracts direct flights (without connection) from the given list of flights departing from the origin.
    """
    direct_journeys = []
    for flight in flights_from_origin:
        if flight.arrival_city == destination:
            # Ensure the flight's duration is within 24 hours
            if (flight.arrival_datetime - flight.departure_datetime) <= timedelta(
                hours=24
            ):
                direct_journeys.append(Journey(connections=0, path=[flight]))
    return direct_journeys


def get_connecting_flights(
    flights_by_departure: Dict[str, List[FlightEvent]], origin: str, destination: str
) -> List[Journey]:
    """
    Extracts connecting flights (with one stop) that depart from the origin and arrive at the destination.
    Uses the departure index for efficient lookup.
    """
    connecting_journeys = []
    # Iterate over flights departing from the origin
    for flight1 in flights_by_departure.get(origin, []):
        # For a valid connection, look up flights departing from flight1's arrival city
        for flight2 in flights_by_departure.get(flight1.arrival_city, []):
            if flight2.arrival_city == destination:
                layover = flight2.departure_datetime - flight1.arrival_datetime
                total_journey_time = (
                    flight2.arrival_datetime - flight1.departure_datetime
                )
                if timedelta(hours=0) <= layover <= timedelta(
                    hours=4
                ) and total_journey_time <= timedelta(hours=24):
                    connecting_journeys.append(
                        Journey(connections=1, path=[flight1, flight2])
                    )
    return connecting_journeys
