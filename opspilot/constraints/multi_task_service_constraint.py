from collections import defaultdict
from ortools.sat.python import cp_model
from typing import Dict, Tuple, List
from opspilot.models import ServiceAssignment, ServiceType, Staff, Service
from opspilot.constraints import Constraint
import logging
from time import time


class MultiTaskServiceConstraint(Constraint):
    def __init__(
        self,
        service_assignments: List[ServiceAssignment],
        roster: List[Staff],
        service_map: Dict[int, Service],
    ):
        self.service_assignments = service_assignments
        self.roster = roster
        self.service_map = service_map

    def apply(self, model: cp_model.CpModel, assignments: Dict[Tuple[int, int], cp_model.IntVar]) -> None:
        """
        Enforces:
        - Staff cannot be assigned to mutually exclusive multi-task services on the same flight.
        - The number of multi-task services per staff on a flight is bounded by multi_task_limit.
        """
        start_time = time()
        logging.info("Applying MultiTaskServiceConstraints...")

        # Group multi-task service assignments by flight number
        flight_service_map = defaultdict(list)
        for sa in self.service_assignments:
            if sa.service_type == ServiceType.MULTI_TASK and sa.flight_number:
                flight_service_map[sa.flight_number].append(sa)

        for staff in self.roster:
            for flight_number, flight_services in flight_service_map.items():
                # All multi-task service assignments on this flight that this staff might be assigned to
                staff_services = [
                    sa for sa in flight_services
                    if (staff.id, sa.id) in assignments
                    and staff.is_certified_for_service(self.service_map[sa.service_id])
                    and staff.is_eligible_for_service(sa)
                ]

                if not staff_services:
                    continue
            
                staff_vars = {
                    sa.id: assignments[(staff.id, sa.id)] for sa in staff_services
                }

                self._apply_exclude_services_constraint(model, staff_services, staff_vars, staff.id, flight_number)
                self._apply_multi_task_limit_constraint(model, staff_services, staff_vars, staff.id, flight_number)

        logging.info(f"Applied MultiTaskServiceConstraints in {time() - start_time:.2f}s")

    def _apply_exclude_services_constraint(
        self,
        model: cp_model.CpModel,
        staff_services: List[ServiceAssignment],
        staff_vars: Dict[int, cp_model.IntVar],
        staff_id: int,
        flight_number: str,
    ):
        """
        Ensure a staff is not assigned to two services that exclude each other on the same flight.
        """
        for i in range(len(staff_services)):
            sa1 = staff_services[i]
            for j in range(i + 1, len(staff_services)):
                sa2 = staff_services[j]
                if sa2.service_id in sa1.exclude_services or sa1.service_id in sa2.exclude_services:
                    var1 = staff_vars[sa1.id]
                    var2 = staff_vars[sa2.id]
                    logging.debug(f"[Exclude] Staff {staff_id} - Flight {flight_number} - SA {sa1.id} ↔ SA {sa2.id}")
                    model.Add(var1 + var2 <= 1)

    def _apply_multi_task_limit_constraint(
        self,
        model: cp_model.CpModel,
        staff_services: List[ServiceAssignment],
        staff_vars: Dict[int, cp_model.IntVar],
        staff_id: int,
        flight_number: str,
    ):
        """
        Ensure the number of multi-task services assigned to a staff on a single flight does not exceed the limit.
        """
        for sa in staff_services:
            limit = sa.multi_task_limit
            if limit is None:
                continue

            compatible_vars = [
                staff_vars[other_sa.id]
                for other_sa in staff_services
                if other_sa.id != sa.id
                and sa.service_id not in other_sa.exclude_services
                and other_sa.service_id not in sa.exclude_services
            ]
            total = staff_vars[sa.id] + sum(compatible_vars)
            logging.debug(f"[Limit] Staff {staff_id} - Flight {flight_number} - SA {sa.id} → Limit {limit}")
            model.Add(total <= limit)
