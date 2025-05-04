from ortools.sat.python.cp_model import CpModel, IntVar
from typing import Dict, Tuple
from time import time
import logging

from opspilot.models import Staff, ServiceAssignment, Service
from opspilot.constraints import Constraint

class StaffCertificationConstraint(Constraint):
    """
    Ensure staff are only assigned to services they are certified for.
    """
    def __init__(
        self,
        staff_map: Dict[int, Staff],
        service_assignment_map: Dict[int, ServiceAssignment],
        service_map: Dict[int, Service]
    ):
        self.staff_map = staff_map
        self.service_assignment_map = service_assignment_map
        self.service_map = service_map

    def apply(self, model: CpModel, assignments: Dict[Tuple[int, int], IntVar]) -> None:
        start_time = time()
        logging.info("Applying StaffCertificationConstraint...")

        for (staff_id, service_assignment_id), var in assignments.items():
            staff = self.staff_map[staff_id]
            service_assignment = self.service_assignment_map[service_assignment_id]
            service = self.service_map[service_assignment.service_id]

            if not staff.is_certified_for_service(service):
                model.Add(var == 0)

        logging.info(f"Applied StaffCertificationConstraint in {time() - start_time:.2f}s")
