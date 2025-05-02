from pydantic import BaseModel
from typing import List, Optional
from opspilot.models import Shift, Service, CertificationRequirement, ServiceType, ServiceAssignment

class Staff(BaseModel):
    id: int
    name: str
    shifts: List[Shift]
    certifications: List[int]
    eligible_for_services: List[ServiceType]
    priority_service_id: Optional[int] = None       # Strong preference for assignment
    rank_level: Optional[int] = 0                   # Lower is higher priority

    def is_available_for_service(self, service_start_minutes: int, service_end_minutes: int) -> bool:
        """
        Checks if the staff has at least one shift that fully covers the service duration.
        Service times are provided in minutes from midnight.
        """
        for shift in self.shifts:
            shift_start = shift.start_minutes
            shift_end = shift.end_minutes

            normalized_service_start = service_start_minutes
            normalized_service_end = service_end_minutes

            if service_start_minutes < shift_start:
                normalized_service_start += 24 * 60
            if service_end_minutes < shift_start:
                normalized_service_end += 24 * 60

            if shift_start <= normalized_service_start and shift_end >= normalized_service_end:
                return True

        return False
    
    def is_certified_for_service(self, service: Service) -> bool:
        """
        Checks if the staff meets the certification requirements to perform the given service.
        """
        required = set(service.certifications)
        staff_certs = set(self.certifications)

        if service.certification_requirement == CertificationRequirement.ALL:
            return required.issubset(staff_certs)

        elif service.certification_requirement == CertificationRequirement.ANY:
            return bool(required & staff_certs)  # At least one in common

        return False  # Fallback if service requirement is unknown
    
    def is_eligible_for_service(self, service_assignment: ServiceAssignment) -> bool:
        """
        Checks if the staff member is eligible to perform a given service assignment.
        Eligibility is determined by:
        1. Eligibility based on the service type (SINGLE, MULTI_TASK, FIXED)
        
        Args:
            service_assignment: The service assignment to check eligibility for
        
        Returns:
            bool: True if staff is eligible, False otherwise
        """
        if service_assignment.service_type not in self.eligible_for_services:
            return False
        
        return True

    def can_perform_service(self, service: Service, service_start_minutes: int, service_end_minutes: int, service_assignment: ServiceAssignment) -> bool:
        """
        Checks if the staff can perform a given service based on availability, certification and eligibility.
        Args:
            service: The service to check
            service_start_minutes: Service start time in minutes from midnight
            service_end_minutes: Service end time in minutes from midnight
            service_assignment: The service assignment to check eligibility for
        Returns:
            bool: True if staff can perform the service, False otherwise
        """
        return (self.is_available_for_service(service_start_minutes, service_end_minutes) and
                self.is_certified_for_service(service) and
                self.is_eligible_for_service(service_assignment))
