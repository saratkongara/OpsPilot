from collections import defaultdict
from typing import List, Dict, Tuple
from opspilot.models import ServiceAssignment, Flight, Settings
import logging

class OverlapDetectionService:
    """
    Detects overlapping service assignments considering:
    - Service start and end windows
    - Location travel times
    - Allowed overlap tolerance buffer
    
    Attributes:
        service_assignments: List of service assignments to analyze
        flight_map: Map of flight number to flight to help resolve flight timing
        travel_time_map: Mapping of (origin_location_id, destination_location_id) to travel time in minutes
        settings: Scheduling configuration including overlap buffer and default travel time
    """
    
    def __init__(
        self,
        service_assignments: List[ServiceAssignment],
        flight_map: Dict[str, Flight],
        travel_time_map: Dict[Tuple[int, int], int],
        settings: Settings
    ):
        self.service_assignments = service_assignments
        self.flight_map = flight_map
        self.travel_time_map = travel_time_map
        self.buffer_minutes = settings.overlap_buffer_minutes
        self.default_travel_time = settings.default_travel_time

    def detect_overlaps(self) -> Dict[int, List[int]]:
        """
        Build a mapping of service assignment IDs to a list of overlapping subsequent assignment IDs.
        
        Returns:
            Dict mapping service_assignment.id -> list of conflicting future service_assignment.id values
        """
        logging.debug("Detecting overlaps between service assignments...")

        # Sort service assignments chronologically by their resolved start times
        sorted_assignments = sorted(
            self.service_assignments,
            key=lambda sa: sa.get_service_time_minutes(self.flight_map)[0]
        )

        overlap_map = defaultdict(list)

        for i, sa_a in enumerate(sorted_assignments):
            _, a_end = sa_a.get_service_time_minutes(self.flight_map)

            for j in range(i + 1, len(sorted_assignments)):
                sa_b = sorted_assignments[j]
                b_start, _ = sa_b.get_service_time_minutes(self.flight_map)

                # Skip same-flight comparisons for Flight Zone services
                if sa_a.flight_number and sa_b.flight_number:
                    if sa_a.flight_number == sa_b.flight_number:
                        continue

                # Determine travel time between locations
                travel_minutes = self.travel_time_map.get(
                    (sa_a.location_id, sa_b.location_id),
                    self.default_travel_time
                )

                # Calculate the earliest permissible start time for sa_b
                minimum_required_gap = max(travel_minutes - self.buffer_minutes, 0)
                adjusted_a_end = a_end + minimum_required_gap

                # Conflict if adjusted end of A overlaps start of B
                if adjusted_a_end > b_start:
                    overlap_map[sa_a.id].append(sa_b.id)
                    logging.info(f"Overlap detected: {sa_a.id} overlaps with {sa_b.id}")
        
        return dict(overlap_map)
