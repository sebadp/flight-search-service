import os

from fastapi import APIRouter, Query, Request

from .limiter import limiter
from services import search_journeys

router = APIRouter(prefix="/journeys", tags=["journeys"])


@router.get("/search")
@limiter.limit("2/second")
async def search_flights(
    request: Request,
    date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    origin: str = Query(
        ..., alias="from", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$"
    ),
    destination: str = Query(
        ..., alias="to", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$"
    ),
):
    """
    FastAPI endpoint to search for available journeys.

    Args:
        date (str): The travel date in 'YYYY-MM-DD' format.
        origin (str): The IATA code of the departure city.
        destination (str): The IATA code of the arrival city.

    Returns:
        JSON response with available journeys.
    """

    journeys = await search_journeys(date, origin, destination)

    if not journeys:
        return {
            "message": f"No journeys available for route {origin} → {destination} on {date}"
        }

    return journeys
