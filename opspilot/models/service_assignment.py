from pydantic import BaseModel, field_validator
from typing import List, Optional
from opspilot.models.enums import ServiceType

class ServiceAssignment(BaseModel):
    id: int
    service_id: int
    location_id: int  # Location where the service will be performed
    priority: int  # Priority for this specific service assignment
    staff_count: int  # Number of staff required for this service assignment
    start: str  # Start time relative to flight or location (e.g., "A+10")
    end: str    # End time relative to flight or location (e.g., "D-5")
    service_type: ServiceType  # Defines if the service is single, multi-task, or fixed
    multi_task_limit: Optional[int] = None  # Limit for cross-utilizing staff in multi-task services
    exclude_services: List[int] = []  # Services that cannot be cross-utilized (only applies to MultiTask services)

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
            f"<ServiceAssignment(id={self.id}, service_id={self.service_id}, "
            f"location_id={self.location_id}, staff_count={self.staff_count}, "
            f"service_type={self.service_type}, priority={self.priority})>"
        )
