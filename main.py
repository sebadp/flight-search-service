from fastapi import FastAPI, Query
from services import search_journeys

app = FastAPI()


@app.get("/journeys/search")
async def search_flights(
    date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    origin: str = Query(..., min_length=3, max_length=3, pattern=r"^[A-Z]{3}$"),
    destination: str = Query(..., min_length=3, max_length=3, pattern=r"^[A-Z]{3}$"),
):
    """
    FastAPI endpoint to search for available journeys.

    Args:
        params (JourneySearchRequest): Validated request parameters.

    Returns:
        JSON response with available journeys.
    """

    journeys = await search_journeys(date, origin, destination)

    if not journeys:
        return {
            "message": f"No journeys available for route {origin} → {destination} on {date}"
        }

    return journeys
