from pydantic import BaseModel
from typing import List, Optional
from opspilot.models.shift import Shift
from opspilot.models.enums import ServiceType

class Staff(BaseModel):
    id: int
    name: str
    shifts: List[Shift]
    certifications: List[int]
    eligible_for_services: List[ServiceType]
    priority_service_id: Optional[int] = None       # Strong preference for assignment
    rank_level: Optional[int] = 0                   # Lower is higher priority
