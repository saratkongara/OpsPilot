from collections import defaultdict
from ortools.sat.python import cp_model
from typing import Dict, Tuple
from opspilot.models import ServiceAssignment
from opspilot.constraints import Constraint
from time import time
import logging

class FixedServiceConstraint(Constraint):
    def __init__(self, service_assignment_map: Dict[int, ServiceAssignment]):
        self.service_assignment_map = service_assignment_map

    def apply(self, model: cp_model.CpModel, assignments: Dict[Tuple[int, int], cp_model.IntVar]) -> None:
        """
        Enforces Fixed (F) service assignment rules:
        1. For FlightZone:
        - A staff member can be assigned to at most one Fixed (F) service per flight.

        2. Across all zones (FlightZone + CommonZone):
        - A staff member can be assigned to only one specific Fixed service_id for the entire day (repeated at different times is okay).
        - If assigned to any Fixed (F) service, staff cannot be assigned to any non-Fixed (S/C/M) service for the whole day.
        """

        start_time = time()
        logging.info("Applying SingleServiceConstraint...")

        # Step 1: FlightZone — at most one Fixed per flight
        flight_staff_to_fixed_vars = defaultdict(list)

        for (staff_id, sa_id), var in assignments.items():
            sa = self.service_assignment_map[sa_id]
            if sa.flight_number is not None and sa.service_type == 'F':
                flight_staff_to_fixed_vars[(sa.flight_number, staff_id)].append(var)

        for (flight_number, staff_id), fixed_vars in flight_staff_to_fixed_vars.items():
            model.Add(sum(fixed_vars) <= 1)

        # Step 2: Only one Fixed service_id per staff for the whole day
        staff_to_fixed_services = defaultdict(lambda: defaultdict(list))

        for (staff_id, sa_id), var in assignments.items():
            sa = self.service_assignment_map[sa_id]
            if sa.service_type == 'F':
                staff_to_fixed_services[staff_id][sa.service_id].append(var)

        for staff_id, service_to_vars in staff_to_fixed_services.items():
            service_flags = []
            for service_id, vars_for_service in service_to_vars.items():
                flag = model.NewBoolVar(f"staff_{staff_id}_uses_fixed_{service_id}")
                model.Add(sum(vars_for_service) >= 1).OnlyEnforceIf(flag)
                model.Add(sum(vars_for_service) == 0).OnlyEnforceIf(flag.Not())
                service_flags.append(flag)

            model.Add(sum(service_flags) <= 1)

        # Step 3: If assigned to any Fixed service, block all non-Fixed assignments (whole day)
        for staff_id in set(staff_id for (staff_id, _) in assignments):
            fixed_vars = []
            non_fixed_vars = []

            for (s_id, sa_id), var in assignments.items():
                if s_id != staff_id:
                    continue
                sa = self.service_assignment_map[sa_id]
                if sa.service_type == 'F':
                    fixed_vars.append(var)
                else:
                    non_fixed_vars.append(var)

            if fixed_vars and non_fixed_vars:
                fixed_selected = model.NewBoolVar(f"staff_{staff_id}_assigned_fixed")
                model.Add(sum(fixed_vars) >= 1).OnlyEnforceIf(fixed_selected)
                model.Add(sum(fixed_vars) == 0).OnlyEnforceIf(fixed_selected.Not())

                for nf_var in non_fixed_vars:
                    model.Add(nf_var == 0).OnlyEnforceIf(fixed_selected)

        logging.info(f"Applied SingleServiceConstraint in {time() - start_time:.2f}s")
