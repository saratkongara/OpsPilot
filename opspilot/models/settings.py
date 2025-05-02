from pydantic import BaseModel, Field
from opspilot.models.enums import AssignmentStrategy

class Settings(BaseModel):
    """
    Configuration for scheduler behavior.

    Attributes:
        overlap_buffer_minutes: Maximum allowed overlap time (minutes) between 
                                consecutive assignments considering travel time.
        default_travel_time: Fallback travel time (minutes) when 
                             no location-to-location travel time is specified.
        assignment_strategy: Strategy for optimizing staff assignments.
    """
    overlap_buffer_minutes: int = Field(default=15, ge=0, description="Maximum allowed overlap time in minutes")
    default_travel_time: int = Field(default=10, gt=0, description="Default travel time in minutes")
    assignment_strategy: AssignmentStrategy = AssignmentStrategy.BALANCE_WORKLOAD