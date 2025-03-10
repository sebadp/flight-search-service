from asyncio import sleep
from bisect import bisect_left, bisect_right
from collections import defaultdict
from datetime import datetime, timedelta
from logging import getLogger, basicConfig, INFO
from typing import List, Dict, Tuple, Set

from httpx import AsyncClient, RequestError

from exceptions import FlightDataFetchError
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

                logger.debug(
                    f"Attempt {attempt}: API responded with {response.status_code}"
                )

        except RequestError as e:
            logger.info(f"Attempt {attempt}: Failed to connect to API: {e}")

        await sleep(2)

    logger.error("Failed to fetch data from API after multiple attempts.")
    raise FlightDataFetchError()


async def search_journeys(date: str, origin: str, destination: str) -> List[Journey]:
    all_flights = await fetch_flight_events()
    search_date = datetime.strptime(date, "%Y-%m-%d")

    # Filter flights and track arrival cities in a set
    flights, arrival_cities = filter_flights_by_date_and_track_arrivals(
        all_flights, search_date
    )

    # Build nested index: departure → arrival → sorted flights (by departure time)
    flights_index = build_nested_flights_index(flights)

    # Early exit if origin/destination is invalid
    if origin not in flights_index or destination not in arrival_cities:
        return []

    # Find direct flights
    direct_flights = flights_index.get(origin, {}).get(destination, [])
    direct_journeys = [
        Journey(connections=0, path=[flight])
        for flight in direct_flights
        if (flight.arrival_datetime - flight.departure_datetime) <= timedelta(hours=24)
    ]

    # Find connecting flights efficiently
    connecting_journeys = get_connecting_flights_optimized(
        flights_index, origin, destination
    )

    return direct_journeys + connecting_journeys


def filter_flights_by_date_and_track_arrivals(
    flights: List[FlightEvent], search_date: datetime
) -> Tuple[List[FlightEvent], Set[str]]:
    next_date = search_date + timedelta(days=1)
    filtered_flights = []
    arrival_cities = set()
    for flight in flights:
        if search_date.date() <= flight.departure_datetime.date() <= next_date.date():
            filtered_flights.append(flight)
            arrival_cities.add(flight.arrival_city)
    return filtered_flights, arrival_cities


def build_nested_flights_index(
    flights: List[FlightEvent],
) -> Dict[str, Dict[str, List[FlightEvent]]]:
    index = defaultdict(lambda: defaultdict(list))
    for flight in flights:
        # Sort flights by departure time for binary search later
        index[flight.departure_city][flight.arrival_city].append(flight)
    # Sort flights by departure time for each (departure, arrival) pair
    for dep in index:
        for arr in index[dep]:
            index[dep][arr].sort(key=lambda f: f.departure_datetime)
    return index


def get_connecting_flights_optimized(
    index: Dict[str, Dict[str, List[FlightEvent]]], origin: str, destination: str
) -> List[Journey]:
    connecting_journeys = []
    # Get all flights from origin
    origin_flights = index.get(origin, {})
    for arrival_city, flight1_list in origin_flights.items():
        if arrival_city == destination:
            continue  # Skip direct flights (already handled)
        # Get flights from arrival_city to destination
        flight2_list = index.get(arrival_city, {}).get(destination, [])
        for flight1 in flight1_list:
            # Find flight2s with valid layover (0–4 hours)
            min_departure = flight1.arrival_datetime
            max_departure = flight1.arrival_datetime + timedelta(hours=4)

            # Extract departure times for binary search
            departure_times = [f.departure_datetime for f in flight2_list]
            left = bisect_left(departure_times, min_departure)
            right = bisect_right(departure_times, max_departure)

            for flight2 in flight2_list[left:right]:
                total_time = flight2.arrival_datetime - flight1.departure_datetime
                if total_time <= timedelta(hours=24):
                    connecting_journeys.append(
                        Journey(connections=1, path=[flight1, flight2])
                    )
    return connecting_journeys
