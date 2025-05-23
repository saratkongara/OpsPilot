from pydantic import BaseModel, Field, model_validator, field_validator
from typing import List, Dict, Optional
from opspilot.models import ServiceType, EquipmentType, Flight
from datetime import datetime, time

class ServiceAssignment(BaseModel):
    id: int
    service_id: int   # Id of the service to be assigned
    priority: float   # Combined priority for this specific service assignment (flight_priority.service_priority). First flight priority followed by service priority. Lower number is higher priority
    staff_count: int  # Number of staff required for this service assignment
    location_id: int  # Location where the service will be performed

    # Optional fields only for flight zone services
    flight_number: Optional[str] = None  # Flight number (e.g., "AA123")
    relative_start: Optional[str] = None  # Start time relative to flight arrival or departure time (e.g., "A+10")
    relative_end: Optional[str] = None # End time relative to flight arrival or departure time (e.g., "D-5")

    # Optional fields for common zone services
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    service_type: ServiceType  # Defines if the service is single, multi-task, or fixed
    multi_task_limit: Optional[int] = None  # Limit for cross-utilizing staff in multi-task services
    exclude_services: List[int] = Field(default_factory=list)  # Services that cannot be multi-tasked with this assignment

    needs_equipment: bool = False  # Indicates if the service requires equipment
    equipment_type: Optional[EquipmentType] # Type of equipment required for the service
    equipment_id: Optional[int] = None  # Id of the equipment to be used (if any)

    @field_validator("start_time", "end_time", mode='before')
    def parse_times(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return datetime.strptime(v, "%H:%M").time()
        return v
    
    @property
    def start_minutes(self):
        if not self.start_time:
            return None
        return self.start_time.hour * 60 + self.start_time.minute

    @property
    def end_minutes(self):
        if not self.end_time:
            return None
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        if end_minutes < (self.start_minutes or 0):
            end_minutes += 24 * 60
        return end_minutes

    @model_validator(mode='after')
    def validate_time_specification(self):
        has_absolute = (self.start_time is not None) and (self.end_time is not None)
        has_relative = (self.flight_number is not None) and (self.relative_start is not None) and (self.relative_end is not None)

        if has_absolute and has_relative:
            raise ValueError("Cannot specify both absolute and relative times")
        if not (has_absolute or has_relative):
            raise ValueError("Must specify either absolute or relative times")
        return self
    
    @model_validator(mode="after")
    def validate_service_assignment(self):
        # Validate multi_task_limit
        if self.service_type == ServiceType.MULTI_TASK:
            if self.multi_task_limit is None:
                raise ValueError("multi_task_limit must be provided for MultiTask service type")
        
            # Multi task can only be used for flight zone services
            if self.flight_number is None:
                raise ValueError("service_type can be MULTI_TASK only for flight zone services")
        else:
            if self.multi_task_limit is not None:
                raise ValueError("multi_task_limit can only be set for MultiTask service type")

        # Validate exclude_services
        if self.service_type == ServiceType.MULTI_TASK:
            pass  # OK
        else:
            if self.exclude_services:
                raise ValueError("exclude_services can only be set for MultiTask service type")

        return self

    def get_service_time_minutes(self, flight_map: Dict[str, Flight]) -> tuple[int, int]:
        """
        Returns (start_minutes, end_minutes) for this service assignment.
        Resolves either relative or absolute time based on flight zone or common zone service.
        """
        if self.flight_number:
            flight = flight_map.get(self.flight_number, None)

            if flight is None:
                raise ValueError(f"Flight {self.flight_number} not found in flight map")
            
            return flight.get_service_time_minutes(self.relative_start, self.relative_end)
        if self.start_minutes is not None and self.end_minutes is not None:
            return self.start_minutes, self.end_minutes
        
        raise ValueError(f"Invalid time configuration for service assignment {self.id}")
    
    def __repr__(self):
        return (
            f"<ServiceAssignment(id={self.id}, service_id={self.service_id}, service_type={self.service_type}, "
            f"flight_number={self.flight_number}, location_id={self.location_id}, "
            f"start_time={self.start_time}, end_time={self.end_time}, "
            f"priority={self.priority})>, staff_count={self.staff_count}, "
        )
