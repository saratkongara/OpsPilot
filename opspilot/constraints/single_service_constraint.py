from ortools.sat.python.cp_model import CpModel, IntVar
from typing import Dict, Tuple
from collections import defaultdict
from opspilot.models import ServiceAssignment
from opspilot.constraints import Constraint
from time import time
import logging

class SingleServiceConstraint(Constraint):
    """
    Enforces Single (S) service assignment rules, but only for FlightZone services:
    1. A staff member can be assigned to at most one 'S' type service per flight.
    2. If assigned to an 'S' service, they cannot be assigned to any other service on the same flight.

    These constraints are skipped for CommonZone services (service_assignment.flight_number is None).
    As CommonZone services can only be either Single or Fixed, the service transition constraint will make sure
    that a staff member is not assigned to multiple CommonZone services (at same or different location) at the same time.
    """

    def __init__(self, service_assignment_map: Dict[int, ServiceAssignment]):
        self.service_assignment_map = service_assignment_map

    def apply(self, model: CpModel, assignments: Dict[Tuple[int, int], IntVar]) -> None:
        start_time = time()
        logging.info("Applying SingleServiceConstraint...")

        # Group service assignments by (flight_number, staff_id)
        flight_staff_to_vars = defaultdict(lambda: {"S": [], "other": []})

        for (staff_id, service_assignment_id), var in assignments.items():
            service_assignment = self.service_assignment_map[service_assignment_id]
            flight_number = service_assignment.flight_number
            service_type = service_assignment.service_type

            # Only apply constraints for FlightZone services
            if flight_number is None:
                continue

            if service_type == 'S':
                flight_staff_to_vars[(flight_number, staff_id)]["S"].append(var)
            else:
                flight_staff_to_vars[(flight_number, staff_id)]["other"].append(var)

        for (flight_number, staff_id), grouped in flight_staff_to_vars.items():
            s_vars = grouped["S"]
            other_vars = grouped["other"]

            if not s_vars:
                continue

            # Constraint 1: At most one 'S' service per flight
            model.Add(sum(s_vars) <= 1)

            if not other_vars:
                continue

            # Constraint 2: If assigned to an 'S' service, cannot be assigned to other services on the same flight
            has_s = model.NewBoolVar(f's_assigned_{flight_number}_{staff_id}')
            model.Add(sum(s_vars) == 1).OnlyEnforceIf(has_s)
            model.Add(sum(s_vars) == 0).OnlyEnforceIf(has_s.Not())

            model.Add(sum(other_vars) == 0).OnlyEnforceIf(has_s)

        logging.info(f"Applied SingleServiceConstraint in {time() - start_time:.2f}s")
