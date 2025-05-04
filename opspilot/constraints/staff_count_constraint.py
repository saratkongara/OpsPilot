from ortools.sat.python.cp_model import CpModel, IntVar
from typing import Dict, Tuple, List
from time import time
import logging

from opspilot.models import ServiceAssignment
from opspilot.constraints import Constraint

class StaffCountConstraint(Constraint):
    """
    Ensure each service assignment gets at most the required number of staff.
    """
    def __init__(
        self,
        service_assignments: List[ServiceAssignment]
    ):
        self.service_assignments = service_assignments

    def apply(self, model: CpModel, assignments: Dict[Tuple[int, int], IntVar]) -> None:
        start_time = time()
        logging.info("Applying StaffCountConstraint...")

        for service_assignment in self.service_assignments:
            assignment_vars = [
                var for (_, sa_id), var in assignments.items()
                if sa_id == service_assignment.id
            ]

            model.Add(sum(assignment_vars) <= service_assignment.staff_count)

        logging.info(f"Applied StaffCountConstraint in {time() - start_time:.2f}s")
