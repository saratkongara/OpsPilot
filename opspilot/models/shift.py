from pydantic import BaseModel, field_validator
from datetime import datetime, time

class Shift(BaseModel):
    start_time: time
    end_time: time

    @field_validator("start_time", "end_time", mode='before')
    def parse_times(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, "%H:%M").time()
        return v
    
    @property
    def start_minutes(self):
        return self.start_time.hour * 60 + self.start_time.minute

    @property
    def end_minutes(self):
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        if end_minutes < self.start_minutes:
            end_minutes += 24 * 60
        return end_minutes

    @property
    def duration_minutes(self):
        return self.end_minutes - self.start_minutes