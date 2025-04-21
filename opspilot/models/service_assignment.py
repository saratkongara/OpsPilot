from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from opspilot.models.enums import ServiceType, EquipmentType
from datetime import datetime

class ServiceAssignment(BaseModel):
    id: int
    service_id: int   # Id of the service to be assigned
    priority: float   # Combined priority for this specific service assignment (flight_priority.service_priority). First flight priority followed by service priority
    staff_count: int  # Number of staff required for this service assignment
    location_id: Optional[int]  # Location where the service will be performed

    # Optional fields only for flight-related services
    flight_number: Optional[str] = None  # Flight number (e.g., "AA123")
    relative_start: Optional[str] = None  # Start time relative to flight arrival or departure time (e.g., "A+10")
    relative_end: Optional[str] = None # End time relative to flight arrival or departure time (e.g., "D-5")

    start_time: datetime
    end_time: datetime

    service_type: ServiceType  # Defines if the service is single, multi-task, fixed or equipment
    multi_task_limit: Optional[int] = None  # Limit for cross-utilizing staff in multi-task services
    exclude_services: List[int] = Field(default_factory=list)  # Services that cannot be multi-tasked with this assignment

    needs_equipment: bool = False  # Indicates if the service requires equipment
    equipment_type: Optional[EquipmentType] # Type of equipment required for the service
    equipment_id: Optional[int] = None  # Id of the equipment to be used (if any)

    @field_validator('multi_task_limit', always=True)
    def validate_multi_task_limit(cls, value, values):
        # Ensure multi_task_limit and exclude_services are only set for MultiTask service types
        if values.get('service_type') == ServiceType.MULTI_TASK:
            if value is None:
                raise ValueError('multi_task_limit must be provided for MultiTask service type')
        else:
            if value is not None:
                raise ValueError('multi_task_limit can only be set for MultiTask service type')
        return value

    @field_validator('exclude_services', always=True)
    def validate_exclude_services(cls, value, values):
        # Ensure exclude_services is only set for MultiTask service types
        if values.get('service_type') == ServiceType.MULTI_TASK:
            return value
        elif value:
            raise ValueError('exclude_services can only be set for MultiTask service type')
        return value

    def __repr__(self):
        return (
            f"<ServiceAssignment(id={self.id}, service_id={self.service_id}, service_type={self.service_type}, "
            f"flight_number={self.flight_number}, location_id={self.location_id}, "
            f"start_time={self.start_time}, end_time={self.end_time}, "
            f"priority={self.priority})>, staff_count={self.staff_count}, "
        )
