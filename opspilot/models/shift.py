from pydantic import BaseModel
from datetime import datetime

class Shift(BaseModel):
    start_time: datetime
    end_time: datetime