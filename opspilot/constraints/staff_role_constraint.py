from ortools.sat.python.cp_model import CpModel, IntVar
from typing import Dict, Tuple
from time import time
import logging

from opspilot.models import Staff, ServiceAssignment
from opspilot.constraints import Constraint

class StaffRoleConstraint(Constraint):
    """
    Ensure staff are only assigned to services if their role_code matches one of the role_priorities.
    """
    def __init__(
        self,
        staff_map: Dict[int, Staff],
        service_assignment_map: Dict[int, ServiceAssignment]
    ):
        self.staff_map = staff_map
        self.service_assignment_map = service_assignment_map

    def apply(self, model: CpModel, assignments: Dict[Tuple[int, int], IntVar]) -> None:
        start_time = time()
        logging.info("Applying StaffRoleConstraint...")

        for (staff_id, service_assignment_id), var in assignments.items():
            staff = self.staff_map[staff_id]
            service_assignment = self.service_assignment_map[service_assignment_id]

            # If role_priorities is empty, any staff role is acceptable
            if not service_assignment.priority_roles:
                continue

            # If role_priorities is not empty, staff must have a role_code
            if staff.role_code is None:
                model.Add(var == 0)  # Disallow assignment if staff has no role and roles are specified
                continue

            role_matched = False
            for role_codes in service_assignment.priority_roles:
                if staff.role_code in role_codes:
                    role_matched = True
                    break
            
            if not role_matched:
                model.Add(var == 0)

        logging.info(f"Applied StaffRoleConstraint in {time() - start_time:.2f}s")
