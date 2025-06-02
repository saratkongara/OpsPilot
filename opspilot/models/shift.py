from pydantic import BaseModel, field_validator
from datetime import datetime, time
from typing import List, Tuple
from opspilot.utils import TimeRangeUtils

class Shift(BaseModel):
    start_time: time
    end_time: time

    @field_validator("start_time", "end_time", mode='before')
    def parse_times(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%H:%M").time()
        return v

    @property
    def minute_intervals(self) -> List[Tuple[int, int]]:
        start_str = self.start_time.strftime("%H:%M")
        end_str = self.end_time.strftime("%H:%M")
        return TimeRangeUtils.to_minute_ranges(start_str, end_str)