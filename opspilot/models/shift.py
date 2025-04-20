from pydantic import BaseModel
from datetime import time

class Shift(BaseModel):
    start: time
    end: time
