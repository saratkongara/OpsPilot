from pydantic import BaseModel
from typing import List, Optional, Tuple, Dict
from .enums import CertificationRequirement, ServiceType
from .shift import Shift
from .service import Service
from .service_assignment import ServiceAssignment
from .flight import Flight
from opspilot.utils import TimeRangeUtils


class Staff(BaseModel):
    id: int
    name: str
    shifts: List[Shift]
    certifications: List[int]
    eligible_for_services: List[ServiceType]
    priority_service_id: Optional[int] = None       # Strong preference for assignment
    rank_level: Optional[int] = 0                   # Lower number is higher priority
    role_code: Optional[str] = None                 # Role code for staff (e.g., "TL", "CSA")
    
    def is_available_for_service(self, service_intervals: List[Tuple[int, int]]) -> bool:
        """
        Checks if shifts of the staff fully cover all intervals of the given service.
        Each service interval must be fully contained within some shift interval.
        """
        # Aggregate all shift intervals
        all_shift_intervals = []
        for shift in self.shifts:
            all_shift_intervals.extend(shift.minute_intervals)

        # Check if all service intervals are fully covered by any shift interval
        return TimeRangeUtils.are_fully_covered(service_intervals, all_shift_intervals)
    
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

    def can_perform_service(self, service: Service, service_intervals: List[Tuple[int, int]], service_assignment: ServiceAssignment) -> bool:
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
        return (self.is_available_for_service(service_intervals) and
                self.is_certified_for_service(service) and
                self.is_eligible_for_service(service_assignment))

    def has_time_available(self, assigned_service_assignments: List[ServiceAssignment], flight_map: Dict[str, Flight]) -> bool:
        """
        Checks if the staff has time available to perform additional services.

        Args:
            assigned_service_assignments: List of service assignments already assigned to the staff.
            flight_map: A dictionary mapping flight numbers to Flight objects.

        Returns:
            bool: True if the staff has time available, False otherwise.
        """
        # Aggregate all assigned service intervals
        assigned_intervals = []
        for service_assignment in assigned_service_assignments:
            assigned_intervals.extend(service_assignment.minute_intervals(flight_map))

        # Aggregate all shift intervals
        all_shift_intervals = []
        for shift in self.shifts:
            all_shift_intervals.extend(shift.minute_intervals)

        # Check if there is any time available in the shifts after accounting for assigned intervals
        return TimeRangeUtils.has_available_time(all_shift_intervals, assigned_intervals)
