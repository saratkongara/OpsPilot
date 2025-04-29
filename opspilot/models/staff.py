from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
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

    def is_available_for_service(self, service_start_minutes: int, service_end_minutes: int) -> bool:
        """
        Checks if the staff has at least one shift that fully covers the service duration.
        Service times are provided in minutes from midnight.
        """
        for shift in self.shifts:
            shift_start = shift.start_minutes
            shift_end = shift.end_minutes

            normalized_service_start = service_start_minutes
            normalized_service_end = service_end_minutes

            if service_start_minutes < shift_start:
                normalized_service_start += 24 * 60
            if service_end_minutes < shift_start:
                normalized_service_end += 24 * 60

            if shift_start <= normalized_service_start and shift_end >= normalized_service_end:
                return True

        return False