from pydantic import BaseModel, Field, model_validator, field_validator
from typing import List, Dict, Tuple, Optional
from opspilot.models import ServiceType, EquipmentType, Flight
from datetime import datetime, time
from opspilot.utils import TimeRangeUtils

class ServiceAssignment(BaseModel):
    id: int
    service_id: int   # Id of the service to be assigned
    department_id: int  # ID of the department this service assignment belongs to
    priority: float   # Combined priority for this specific service assignment (flight_priority.service_priority). First flight priority followed by service priority. Lower number is higher priority
    staff_count: int  # Number of staff required for this service assignment
    location_id: int  # Location where the service will be performed
    priority_roles: List[List[str]] = Field(default_factory=list)  # List of Lists of priority roles for this service assignment
    
    # Optional fields only for flight zone services
    flight_number: Optional[str] = None  # Flight number (e.g., "AA123")
    relative_start: Optional[str] = None  # Start time relative to flight arrival or departure time (e.g., "A+10")
    relative_end: Optional[str] = None # End time relative to flight arrival or departure time (e.g., "D-5")

    # Optional fields for common zone services
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    # Service type and multi-tasking properties
    service_type: ServiceType  # Defines if the service is single, multi-task, or fixed
    multi_task_limit: Optional[int] = None  # Limit for cross-utilizing staff in multi-task services
    exclude_services: List[int] = Field(default_factory=list)  # Services that cannot be multi-tasked with this assignment

    # Equipment requirements
    needs_equipment: bool = False  # Indicates if the service requires equipment
    equipment_type: Optional[EquipmentType] = None # Type of equipment required for the service
    equipment_id: Optional[int] = None  # Id of the equipment to be used (if any)

    @field_validator("start_time", "end_time", mode='before')
    def parse_times(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return datetime.strptime(v, "%H:%M").time()
        return v
    
    def minute_intervals(self, flight_map: Dict[str, Flight]) -> List[Tuple[int, int]]:
        """
        Returns the minute intervals for this service assignment.
        
        - If flight_number is set, resolves intervals using flight_map and relative times.
        - Else returns intervals for common zone service using start_time and end_time.
        - Raises ValueError if no valid time info is found.
        """
        if self.flight_number:
            flight = flight_map.get(self.flight_number)
            if not flight:
                raise ValueError(f"Flight {self.flight_number} not found in flight_map")

            return flight.get_service_minute_intervals(self.relative_start, self.relative_end)

        if self.start_time and self.end_time:
            start_str = self.start_time.strftime("%H:%M")
            end_str = self.end_time.strftime("%H:%M")
            return TimeRangeUtils.to_minute_ranges(start_str, end_str)

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
    def validate_equipment_requirements(self):
        if self.needs_equipment:
            if self.equipment_type is None:
                raise ValueError("equipment_type must be provided when needs_equipment is True")
            if self.equipment_id is None:
                raise ValueError("equipment_id must be provided when needs_equipment is True")
        else:
            if self.equipment_type is not None:
                raise ValueError("equipment_type must be None when needs_equipment is False")
            if self.equipment_id is not None:
                raise ValueError("equipment_id must be None when needs_equipment is False")
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

    def __repr__(self):
        return (
            f"<ServiceAssignment(id={self.id}, service_id={self.service_id}, service_type={self.service_type}, "
            f"flight_number={self.flight_number}, location_id={self.location_id}, "
            f"start_time={self.start_time}, end_time={self.end_time}, "
            f"priority={self.priority})>, staff_count={self.staff_count}, "
        )

