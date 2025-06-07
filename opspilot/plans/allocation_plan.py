import json
from typing import Dict, List, Set
from opspilot.models import ServiceAssignment, Staff, Flight, Service, Location
from .schedule_entry import ScheduleEntry
from collections import defaultdict

class AllocationPlan:
    def __init__(
        self,
        service_assignment_map: Dict[int, 'ServiceAssignment'],
        service_map: Dict[int, 'Service'],
        staff_map: Dict[int, 'Staff'],
        flight_map: Dict[str, 'Flight'],
    ):
        """
        Initialize the allocation plan.
        Only positive assignments (True values) are stored.
        """
        self.allocations = {}  # Format: {service_assignment_id: set(staff_ids)}
        self.service_assignment_map = service_assignment_map
        self.service_map = service_map
        self.staff_map = staff_map
        self.flight_map = flight_map

        # Build reverse mapping for flight-based lookups
        self._flight_to_assignments = self._build_flight_assignments_map()

    def _build_flight_assignments_map(self) -> Dict[str, Set[int]]:
        """Create a mapping from flight numbers to service assignment IDs"""
        flight_assignments = defaultdict(set)
        for sa in self.service_assignment_map.values():
            if sa.flight_number:
                # Only include service assignments with a flight number
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

    def _format_minutes_to_time_str(self, minutes: int) -> str:
        """Convert minutes since midnight into HH:MM format."""
        hours, mins = divmod(minutes, 60)
        hours = hours % 24  # Handle wraparound over 24h
        return f"{hours:02}:{mins:02}"

    def staff_schedule(self) -> Dict[int, List[ScheduleEntry]]:
        schedule = defaultdict(list)

        for sa_id, staff_ids in self.allocations.items():
            sa = self.service_assignment_map[sa_id]
            service = self.service_map[sa.service_id]

            if sa.flight_number:
                flight = self.flight_map[sa.flight_number]
                start_min, end_min = flight.get_service_time_minutes(sa.relative_start, sa.relative_end)
            else:
                start_min = sa.start_time.hour * 60 + sa.start_time.minute
                end_min = sa.end_time.hour * 60 + sa.end_time.minute

            for staff_id in staff_ids:
                staff = self.staff_map[staff_id]

                entry = ScheduleEntry(
                    service_assignment_id=sa_id,
                    staff_id=staff_id,
                    staff_name=staff.name,
                    service_name=service.name,
                    start_time=self._format_minutes_to_time_str(start_min),
                    end_time=self._format_minutes_to_time_str(end_min),
                    flight_number=sa.flight_number,
                    location_id=sa.location_id,
                    flight_priority=int(sa.priority),
                    service_priority=int((sa.priority * 10) % 10) if sa.flight_number else int(sa.priority),
                )

                schedule[staff_id].append(entry)

        for entries in schedule.values():
            entries.sort(key=lambda x: x.start_min)

        return schedule

    def flight_zone_services_schedule(self) -> Dict[str, List[ScheduleEntry]]:
        schedule = defaultdict(list)

        for sa_id, staff_ids in self.allocations.items():
            sa = self.service_assignment_map[sa_id]
            if not sa.flight_number:
                continue

            flight = self.flight_map[sa.flight_number]
            service = self.service_map[sa.service_id]
            start_min, end_min = flight.get_service_time_minutes(sa.relative_start, sa.relative_end)

            for staff_id in staff_ids:
                staff = self.staff_map[staff_id]

                entry = ScheduleEntry(
                    service_assignment_id=sa_id,
                    staff_id=staff_id,
                    staff_name=staff.name,
                    service_name=service.name,
                    start_time=self._format_minutes_to_time_str(start_min),
                    end_time=self._format_minutes_to_time_str(end_min),
                    flight_number=sa.flight_number,
                    location_id=sa.location_id,
                    flight_priority=int(sa.priority),
                    service_priority=int((sa.priority * 10) % 10),
                )

                schedule[sa.flight_number].append(entry)

        for entries in schedule.values():
            entries.sort(key=lambda x: x.start_min)

        return schedule

    def common_zone_services_schedule(self) -> Dict[int, List[ScheduleEntry]]:
        schedule = defaultdict(list)

        for sa_id, staff_ids in self.allocations.items():
            sa = self.service_assignment_map[sa_id]
            if sa.flight_number:
                continue

            service = self.service_map[sa.service_id]
            start_min = sa.start_time.hour * 60 + sa.start_time.minute
            end_min = sa.end_time.hour * 60 + sa.end_time.minute

            for staff_id in staff_ids:
                staff = self.staff_map[staff_id]

                entry = ScheduleEntry(
                    service_assignment_id=sa_id,
                    staff_id=staff_id,
                    staff_name=staff.name,
                    service_name=service.name,
                    start_time=self._format_minutes_to_time_str(start_min),
                    end_time=self._format_minutes_to_time_str(end_min),
                    flight_number=None,
                    location_id=sa.location_id,
                    flight_priority=None,
                    service_priority=int(sa.priority),
                )

                schedule[sa_id].append(entry)

        for entries in schedule.values():
            entries.sort(key=lambda x: x.start_min)

        return schedule


