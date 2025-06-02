from ortools.sat.python.cp_model import CpModel, IntVar
from typing import Dict, Tuple, List
from time import time
import logging

from opspilot.models import Staff, ServiceAssignment, Service, Flight
from opspilot.constraints import Constraint

class ServiceTransitionConstraint(Constraint):
    """
    Prevent staff from being assigned to overlapping service assignments
    that do not allow sufficient travel and buffer time between them.
    Only apply to staff who are eligible for both services.
    """
    def __init__(
        self,
        roster: List[Staff],
        overlap_map: Dict[int, List[int]],
        service_assignment_map: Dict[int, ServiceAssignment],
        service_map: Dict[int, Service],
        flight_map: Dict[int, Flight]
    ):
        self.roster = roster
        self.overlap_map = overlap_map
        self.service_assignment_map = service_assignment_map
        self.service_map = service_map
        self.flight_map = flight_map

    def apply(self, model: CpModel, assignments: Dict[Tuple[int, int], IntVar]) -> None:
        start_time = time()
        logging.info("Applying ServiceTransitionConstraint...")

        for staff in self.roster:
            for sa_id_a, conflicting_ids in self.overlap_map.items():
                service_assignment_a = self.service_assignment_map[sa_id_a]
                service_a = self.service_map[service_assignment_a.service_id]
                service_a_intervals = service_assignment_a.minute_intervals(self.flight_map)

                # Skip if staff cannot perform service A
                if not staff.can_perform_service(service_a, service_a_intervals, service_assignment_a):
                    continue

                for sa_id_b in conflicting_ids:
                    service_assignment_b = self.service_assignment_map[sa_id_b]
                    service_b = self.service_map[service_assignment_b.service_id]
                    service_b_intervals = service_assignment_b.minute_intervals(self.flight_map)

                    # Skip if staff cannot perform service B
                    if not staff.can_perform_service(service_b, service_b_intervals, service_assignment_b):
                        continue

                    var_a = assignments[(staff.id, sa_id_a)]
                    var_b = assignments[(staff.id, sa_id_b)]

                    # Ensure staff is not assigned to both conflicting services
                    model.Add(var_a + var_b <= 1)

        logging.info(f"Applied ServiceTransitionConstraint in {time() - start_time:.2f}s")
