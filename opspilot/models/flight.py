from pydantic import BaseModel, field_validator
from datetime import datetime, time
from opspilot.utils import TimeRangeUtils
from typing import List, Tuple

class Flight(BaseModel):
    number: str  # e.g., "AA123"
    arrival_time: time # Time of arrival eg: "14:30"
    departure_time: time # Time of departure eg: "16:30"

    @field_validator("arrival_time", "departure_time", mode='before')
    def parse_times(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%H:%M").time()
        return v
    
    def get_service_minute_intervals(self, relative_start: str, relative_end: str) -> List[Tuple[int, int]]:
        """
        Convert relative service start and end (like "A+30", "D-15") to minute intervals since midnight.
        Handles wraparound correctly.
        """
        def resolve_base_time(relative: str) -> time:
            if relative.startswith("A"):
                return self.arrival_time
            elif relative.startswith("D"):
                return self.departure_time
            raise ValueError(f"Invalid relative time: {relative}")

        def parse_relative_time(relative: str) -> int:
            base_time = resolve_base_time(relative)
            base_minutes = base_time.hour * 60 + base_time.minute

            if "+" in relative:
                offset = int(relative.split("+")[1])
            elif "-" in relative:
                offset = -int(relative.split("-")[1])
            else:
                offset = 0

            return base_minutes + offset

        start_minutes = parse_relative_time(relative_start)
        end_minutes = parse_relative_time(relative_end)

        return TimeRangeUtils.to_minute_ranges_from_minutes(start_minutes, end_minutes)
