from pydantic import BaseModel
from typing import Optional

class ScheduleEntry(BaseModel):
    service_assignment_id: int
    service_name: str
    start_time: str  # formatted HH:MM
    end_time: str    # formatted HH:MM
    flight_number: Optional[str] = None
    flight_priority: Optional[int] = None
    service_priority: int
    staff_id: int
    staff_name: str
    location: str

    @property
    def start_min(self) -> int:
        hour, minute = map(int, self.start_time.split(":"))
        return hour * 60 + minute
    
    def __str__(self):
        priority_info = (
            f"Flight Priority: {self.flight_priority}, Service Priority: {self.service_priority}"
            if self.flight_number else f"Service Priority: {self.service_priority}"
        )
        return (
            f"Id: {self.service_assignment_id}"
            f"[{self.start_time} - {self.end_time}] {self.service_name} "
            f"(Flight: {self.flight_number}) " if self.flight_number else f"[{self.start_time} - {self.end_time}] {self.service_name} "
        ) + f"@ {self.location}, Staff: {self.staff_id} - {self.staff_name}, {priority_info}"
