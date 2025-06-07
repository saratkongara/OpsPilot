from pydantic import BaseModel
from .staff import Staff
from .service_assignment import ServiceAssignment
from .travel_time import TravelTime
from typing import List, Optional
from opspilot.plans import AllocationPlan

class Department(BaseModel):
    id: int
    name: str
    roster: List[Staff]
    service_assignments: List[ServiceAssignment]
    travel_times: Optional[List[TravelTime]] = []
    allocation_plan: Optional[AllocationPlan] = None
    pending_assignments: Optional[List[ServiceAssignment]] = None
    available_staff: Optional[List[Staff]] = None
    