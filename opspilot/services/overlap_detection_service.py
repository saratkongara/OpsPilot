from collections import defaultdict
from typing import List, Dict, Tuple
from opspilot.models import ServiceAssignment, Flight, Location, Settings
from opspilot.utils import TimeRangeUtils
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
        location_map: Map of location_id to Location object for resolving locations
        travel_time_map: Mapping of (origin_location_id, destination_location_id) to travel time in minutes
        settings: Scheduling configuration including overlap buffer and default travel time
    """
    
    def __init__(
        self,
        service_assignments: List[ServiceAssignment],
        flight_map: Dict[str, Flight],
        location_map: Dict[int, Location],
        travel_time_map: Dict[Tuple[int, int], int],
        settings: Settings
    ):
        self.service_assignments = service_assignments
        self.flight_map = flight_map
        self.location_map = location_map
        self.travel_time_map = travel_time_map
        self.buffer_minutes = settings.overlap_buffer_minutes
        self.default_travel_time = settings.default_travel_time

    def detect_overlaps(self) -> Dict[int, List[int]]:
        logging.debug("Detecting overlaps between service assignments...")

        # Sort assignments by the first minute of their interval
        sorted_assignments = sorted(
            self.service_assignments,
            key=lambda sa: sa.minute_intervals(self.flight_map)[0][0]
        )

        overlap_map = defaultdict(list)

        for i, sa_a in enumerate(sorted_assignments):
            a_intervals = sa_a.minute_intervals(self.flight_map)

            for j in range(i + 1, len(sorted_assignments)):
                sa_b = sorted_assignments[j]

                # Skip same-flight comparisons for Flight Zone services
                if sa_a.flight_number and sa_b.flight_number:
                    if sa_a.flight_number == sa_b.flight_number:
                        continue

                b_intervals = sa_b.minute_intervals(self.flight_map)

                # Get travel time from A to B (with default fallback)
                source_location = self.location_map.get(sa_a.location_id, None)
                destination_location = self.location_map.get(sa_b.location_id, None)

                if not source_location or not destination_location:
                    travel_minutes = self.default_travel_time
                elif source_location.parent_id and destination_location.parent_id:
                    travel_minutes = self.travel_time_map.get(
                        (source_location.parent_id, destination_location.parent_id),
                        self.default_travel_time
                    )
                else:
                    travel_minutes = self.travel_time_map.get(
                        (source_location.id, destination_location.id),
                        self.default_travel_time
                    )

                # Apply buffer (overlap tolerance)
                buffer = self.buffer_minutes
                min_gap = max(travel_minutes - buffer, 0)

                # Adjust A's intervals with min_gap as extension
                adjusted_a_intervals = [(start, end + min_gap) for start, end in a_intervals]

                # Detect if any of A’s adjusted intervals overlap with any of B’s
                if TimeRangeUtils.has_overlap(adjusted_a_intervals, b_intervals):
                    overlap_map[sa_a.id].append(sa_b.id)
                    logging.info(f"Overlap detected: {sa_a.id} overlaps with {sa_b.id}")

        return dict(overlap_map)
