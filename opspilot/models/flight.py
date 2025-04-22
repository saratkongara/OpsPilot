from pydantic import BaseModel, field_validator
from datetime import datetime, time

class Flight(BaseModel):
    number: str  # e.g., "AA123"
    arrival_time: time
    departure_time: time

    @field_validator("arrival_time", "departure_time", mode='before')
    def parse_times(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%H:%M").time()
        return v