from pydantic import BaseModel

class TravelTime(BaseModel):
    origin_location_id: int
    destination_location_id: int
    travel_minutes: int
