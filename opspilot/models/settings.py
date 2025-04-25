from pydantic import BaseModel, Field
from opspilot.models.enums import OptimizationStrategy

class Settings(BaseModel):
    """
    Configuration for scheduler behavior.

    Attributes:
        overlap_tolerance_buffer: Maximum allowed overlap time (minutes) between 
                                  consecutive assignments considering travel time.
        default_travel_time: Fallback travel time (minutes) when no bay-specific 
                             time is specified.
        optimization_strategy: Strategy for optimizing staff assignments.   
    """
    overlap_tolerance_buffer: int = Field(default=15, ge=0, description="Maximum allowed overlap time in minutes")
    default_travel_time: int = Field(default=5, gt=0, description="Default travel time in minutes")
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.MINIMIZE_STAFF