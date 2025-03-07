from datetime import datetime

from fastapi import FastAPI, Query, HTTPException
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
    search_date = datetime.strptime(date, "%Y-%m-%d").date()
    today = datetime.now().date()
    if search_date < today:
        raise HTTPException(
            status_code=400, detail="Search date must be in the future."
        )

    journeys = await search_journeys(date, origin, destination)

    if not journeys:
        return {
            "message": f"No journeys available for route {origin} → {destination} on {date}"
        }

    return journeys
