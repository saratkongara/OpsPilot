from ortools.sat.python.cp_model import CpModel, IntVar
from typing import Dict, Tuple, List
from time import time
import logging

from opspilot.models import Staff, ServiceAssignment, Flight
from opspilot.constraints import Constraint

class StaffAvailabilityConstraint(Constraint):
    """
    Ensure staff are only assigned to services they are available for.
    """
    def __init__(
        self,
        roster: List[Staff],
        service_assignments: List[ServiceAssignment],
        flight_map: Dict[int, Flight]
    ):
        self.roster = roster
        self.service_assignments = service_assignments
        self.flight_map = flight_map
        self.staff_map = {staff.id: staff for staff in roster}
        self.service_assignment_map = {sa.id: sa for sa in service_assignments}

    def apply(self, model: CpModel, assignments: Dict[Tuple[int, int], IntVar]) -> None:
        start_time = time()
        logging.info("Applying StaffAvailabilityConstraint...")

        for (staff_id, service_assignment_id), var in assignments.items():
            staff = self.staff_map[staff_id]
            service_assignment = self.service_assignment_map[service_assignment_id]

            service_start, service_end = service_assignment.get_service_time_minutes(self.flight_map)

            if not staff.is_available_for_service(service_start, service_end):
                logging.info(
                    f"Staff {staff_id} not available for service_assignment {service_assignment_id} "
                    f"(Service time {service_start}-{service_end} mins), setting var to 0"
                )
                model.Add(var == 0)

        logging.info(f"Applied StaffAvailabilityConstraint in {time() - start_time:.2f}s")
