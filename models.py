from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import List

from pydantic_core.core_schema import ValidationInfo


class FlightEvent(BaseModel):
    flight_number: str = Field(..., description="Flight number")
    departure_city: str = Field(
        ..., min_length=3, max_length=3, description="IATA code of departure city"
    )
    arrival_city: str = Field(
        ..., min_length=3, max_length=3, description="IATA code of arrival city"
    )
    departure_datetime: datetime = Field(..., description="UTC departure time")
    arrival_datetime: datetime = Field(..., description="UTC arrival time")

    @field_validator("arrival_datetime")
    @classmethod
    def check_arrival_after_departure(
        cls, arrival_datetime: datetime, info: ValidationInfo
    ):
        """Ensure arrival time is after departure time."""
        departure_datetime = info.data["departure_datetime"]
        if departure_datetime and arrival_datetime <= departure_datetime:
            raise ValueError("Arrival time must be after departure time.")
        return arrival_datetime

    model_config = ConfigDict(populate_by_name=True)


class Journey(BaseModel):
    connections: int = Field(
        ..., ge=0, le=1, description="Number of connections (max 1)"
    )
    path: List[FlightEvent] = Field(
        ..., description="List of flight events forming the journey"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "connections": 0,
                "path": [
                    {
                        "flight_number": "XX1234",
                        "from_city": "BUE",
                        "to_city": "MAD",
                        "departure_time": "2024-09-12T12:00:00Z",
                        "arrival_time": "2024-09-13T00:00:00Z",
                    }
                ],
            }
        }
    )
