from pydantic import BaseModel
from datetime import datetime

class Flight(BaseModel):
    number: str  # e.g., "AA123"
    arrival_time: datetime
    departure_time: datetime
