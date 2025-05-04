from ortools.sat.python.cp_model import CpModel, IntVar
from typing import Dict, Tuple
from time import time
import logging

from opspilot.models import Staff, ServiceAssignment
from opspilot.constraints import Constraint

class StaffEligibilityConstraint(Constraint):
    """
    Ensure staff are only assigned to services they are eligible for based on service type.
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
        logging.info("Applying StaffEligibilityConstraint...")

        for (staff_id, service_assignment_id), var in assignments.items():
            staff = self.staff_map[staff_id]
            service_assignment = self.service_assignment_map[service_assignment_id]

            if not staff.is_eligible_for_service(service_assignment):
                model.Add(var == 0)

        logging.info(f"Applied StaffEligibilityConstraint in {time() - start_time:.2f}s")
