from pydantic import BaseModel
from .staff import Staff
from .service_assignment import ServiceAssignment
from .travel_time import TravelTime
from typing import List, Optional

class Department(BaseModel):
    id: int
    name: str
    roster: List[Staff]
    service_assignments: List[ServiceAssignment]
    travel_times: Optional[List[TravelTime]] = []