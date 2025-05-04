import json
from typing import Dict, List, Optional, Set
from opspilot.models import ServiceAssignment, Staff, Flight, Service

class AllocationPlan:
    def __init__(
        self,
        service_assignments: List['ServiceAssignment'],
        service_map: Dict[int, 'Service'],
        staff_map: Dict[int, 'Staff'],
        flight_map: Dict[str, 'Flight']
    ):
        """
        Initialize the allocation plan.
        Only positive assignments (True values) are stored.
        """
        self.allocations = {}  # Format: {service_assignment_id: set(staff_ids)}
        self.service_assignment_map = {sa.id: sa for sa in service_assignments}
        self.service_map = service_map
        self.staff_map = staff_map
        self.flight_map = flight_map
        # Build reverse mapping for flight-based lookups
        self._flight_to_assignments = self._build_flight_assignments_map()

    def _build_flight_assignments_map(self) -> Dict[str, Set[int]]:
        """Create a mapping from flight numbers to service assignment IDs"""
        flight_assignments = {}
        for sa in self.service_assignment_map.values():
            if sa.flight_number:
                if sa.flight_number not in flight_assignments:
                    flight_assignments[sa.flight_number] = set()
                flight_assignments[sa.flight_number].add(sa.id)
        return flight_assignments

    def serialize(self) -> str:
        """
        Serialize the allocation plan to JSON.
        """
        return json.dumps(
            {str(k): list(v) for k, v in self.allocations.items()},
            indent=4
        )

    def deserialize(self, json_string: str) -> None:
        """
        Deserialize from JSON, converting lists back to sets.
        """
        self.allocations = {
            int(k): set(v) for k, v in json.loads(json_string).items()
        }
        # Rebuild flight assignments map after deserialization
        self._flight_to_assignments = self._build_flight_assignments_map()

    def add_allocation(self, service_assignment_id: int, staff_id: int) -> None:
        """
        Add a positive allocation (staff assigned to service assignment).
        """
        if service_assignment_id not in self.allocations:
            self.allocations[service_assignment_id] = set()
        self.allocations[service_assignment_id].add(staff_id)

    def get_allocation(self, service_assignment_id: int, staff_id: int) -> bool:
        """
        Check if a staff member is assigned to a service assignment.
        """
        return staff_id in self.allocations.get(service_assignment_id, set())

    def remove_allocation(self, service_assignment_id: int, staff_id: int) -> None:
        """
        Remove an allocation (staff no longer assigned to service assignment).
        """
        if service_assignment_id in self.allocations:
            self.allocations[service_assignment_id].discard(staff_id)
            if not self.allocations[service_assignment_id]:
                del self.allocations[service_assignment_id]

    def remove_staff(self, staff_id: int) -> None:
        """
        Remove all allocations for a specific staff member across all service assignments.
        More efficient implementation that scans all assignments once.
        """
        service_assignments_to_clean = []
        
        for sa_id, staff_ids in self.allocations.items():
            if staff_id in staff_ids:
                staff_ids.discard(staff_id)
                if not staff_ids:
                    service_assignments_to_clean.append(sa_id)
        
        # Clean up empty service assignments
        for sa_id in service_assignments_to_clean:
            del self.allocations[sa_id]

    def remove_flight(self, flight_number: str) -> None:
        """
        Remove all allocations for service assignments associated with a specific flight.
        Uses pre-built flight-to-assignments mapping for O(1) lookup.
        """
        if flight_number not in self._flight_to_assignments:
            return
            
        for sa_id in self._flight_to_assignments[flight_number]:
            if sa_id in self.allocations:
                del self.allocations[sa_id]
        
        # Remove from flight mapping as well
        del self._flight_to_assignments[flight_number]

    

