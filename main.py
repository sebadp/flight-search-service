from logging import getLogger

from fastapi import FastAPI, Query
from fastapi_cache import FastAPICache

from cache import set_cache_response, get_cached_response, lifespan, generate_cache_key
from services import search_journeys


app = FastAPI(lifespan=lifespan)
logger = getLogger(__name__)


@app.get("/journeys/search")
async def search_flights(
    date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    origin: str = Query(
        ..., alias="from", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$"
    ),
    destination: str = Query(
        ..., alias="to", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$"
    ),
):
    """
    FastAPI endpoint to search for available journeys. It uses a cache with REDIS to store the results.

    Args:
        date (str): The travel date in 'YYYY-MM-DD' format.
        origin (str): The IATA code of the departure city.
        destination (str): The IATA code of the arrival city.

    Returns:
        JSON response with available journeys.
    """
    cache_key = generate_cache_key(date=date, origin=origin, destination=destination)
    redis = FastAPICache.get_backend().redis

    cached_response = await get_cached_response(redis_client=redis, cache_key=cache_key)
    if cached_response is not None:
        logger.debug(
            f"Retrieved cached response for {origin} → {destination} on {date}"
        )
        return cached_response
    logger.debug(f"No cached response found for {origin} → {destination} on {date}")
    journeys = await search_journeys(date=date, origin=origin, destination=destination)
    if journeys:
        journeys_serialized = [journey.model_dump() for journey in journeys]
        await set_cache_response(
            redis=redis, cache_key=cache_key, values=journeys_serialized, expiration=600
        )
        return journeys_serialized
    else:
        response = {
            "message": f"No journeys available for route {origin} → {destination} on {date}"
        }
        await set_cache_response(redis, cache_key, response)
        return response
