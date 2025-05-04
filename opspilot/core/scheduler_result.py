from enum import Enum

class SchedulerResult(str, Enum):
    FOUND = "Found"
    NOT_FOUND = "Not Found"
