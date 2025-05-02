from ortools.sat.python import cp_model
from typing import Optional, List, Dict, Tuple
from  opspilot.core.scheduler_result import SchedulerResult
from opspilot.models import Staff, Service, Flight, ServiceAssignment, TravelTime, Settings, AssignmentStrategy, ServiceType
from opspilot.services import OverlapDetectionService
from time import time
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class Scheduler:
    def __init__(
        self,
        roster: List[Staff],
        services: List[Service],
        flights: List[Flight],
        service_assignments: List[ServiceAssignment],
        settings: Settings,
        travel_times: Optional[List[TravelTime]] = [],
        previous_assignments: Optional[Dict[Tuple[int, int], bool]] = []
    ):
        """
        Initialize the scheduler with input data.
        
        Args:
            roster: List of available staff members
            service_assignments: List of service assignments that need staff
            services: List of services with their certification requirements
            settings: Configuration parameters for scheduling
            previous_assignments: Optional previous assignments for continuity (staff_id -> service_assignment_id -> assigned)
        """
        self.roster = roster
        self.services = services
        self.flights = flights
        self.service_assignments = service_assignments
        self.settings = settings
        self.previous_assignments = previous_assignments or {}
        
        # OR-Tools model
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
        # Decision variables: (staff_id, service_assignment_id) -> BoolVar
        self.assignment_vars: Dict[Tuple[int, int], cp_model.IntVar] = {}
        
        # Lookup maps
        self.staff_map = {staff.id: staff for staff in roster}
        self.service_assignment_map = {service_assignment.id: service_assignment for service_assignment in service_assignments}
        self.service_map = {service.id: service for service in services}
        self.flight_map = {flight.number: flight for flight in flights}
        self.travel_time_map = {(travel_time.from_location_id, travel_time.to_location_id): travel_time.travel_minutes for travel_time in travel_times}
        
        # Initialize overlap detector
        overlap_detector = OverlapDetectionService(
            service_assignments=self.service_assignments,
            flight_map=self.flight_map,
            travel_time_map=self.travel_time_map,
            settings=self.settings
        )

        self.overlap_map = overlap_detector.detect_overlaps()
        
        # Results and metrics
        self.solution: Dict[Tuple[int, int], bool] = {}
        self.solution_status: Optional[SchedulerResult] = None
        self.solve_time: float = 0.0
        self.objective_value: float = 0.0

    def create_assignment_variables(self) -> None:
        """Create decision variables for all possible staff-service assignment combinations."""
        start_time = time()
        logging.info("Creating assignment variables...")
        
        for staff in self.roster:
            for service_assignment in self.service_assignments:
                var_name = f"staff_{staff.id}_service_assignment_{service_assignment.id}"
                self.assignment_vars[(staff.id, service_assignment.id)] = self.model.NewBoolVar(var_name)
                
                # Apply previous assignment as hint if available
                if (staff.id, service_assignment.id) in self.previous_assignments:
                    self.model.AddHint(
                        self.assignment_vars[(staff.id, service_assignment.id)],
                        int(self.previous_assignments[(staff.id, service_assignment.id)])
                    )
        
        logging.info(f"Created {len(self.assignment_vars)} assignment variables in {time() - start_time:.2f}s")

    def add_staff_certification_constraint(self) -> None:
        """Ensure staff only get assigned to services they're certified for."""
        start_time = time()
        logging.info("Adding certification constraints...")

        for (staff_id, service_assignment_id), var in self.assignment_vars.items():
            staff = self.staff_map[staff_id]
            service_assignment = self.service_assignment_map[service_assignment_id]
            service = self.service_map[service_assignment.service_id]

            if not staff.is_certified_for_service(service):
                self.model.Add(var == 0)

        logging.info(f"Added certification constraints in {time() - start_time:.2f}s")

    def add_staff_eligibility_constraint(self) -> None:
        """Ensure staff are only assigned to services they are eligible for based on service type."""
        start_time = time()
        logging.info("Adding eligibility constraints...")

        for (staff_id, service_assignment_id), var in self.assignment_vars.items():
            staff = self.staff_map[staff_id]
            service_assignment = self.service_assignment_map[service_assignment_id]

            if not staff.is_eligible_for_service(service_assignment):
                self.model.Add(var == 0)

        logging.info(f"Added eligibility constraints in {time() - start_time:.2f}s")

    def add_staff_count_constraint(self) -> None:
        """Ensure each service assignment gets the required number of staff."""
        start_time = time()
        logging.info("Adding staff count constraints...")
        
        for service_assignment in self.service_assignments:
            # Sum of all assignments for this service
            assignment_vars = [
                var for (_, service_assignment_id), var in self.assignment_vars.items()
                if service_assignment_id == service_assignment.id
            ]
            
            # Must have at most the required number of staff
            self.model.Add(sum(assignment_vars) <= service_assignment.staff_count)

        logging.info(f"Added staff count constraints in {time() - start_time:.2f}s")

    def add_staff_availability_constraint(self) -> None:
        """Ensure staff are only assigned to services they are available for."""
        for (staff_id, service_assignment_id), assignment_var in self.assignment_vars.items():
            staff = next(staff for staff in self.roster if staff.id == staff_id)
            service_assignment = next(sa for sa in self.service_assignments if sa.id == service_assignment_id)

            service_start_minutes, service_end_minutes = service_assignment.get_service_time_minutes(self.flight_map)

            if not staff.is_available_for_service(service_start_minutes, service_end_minutes):
                logging.info(
                    f"Staff {staff_id} not available for service_assignment {service_assignment_id} "
                    f"(Service time {service_start_minutes}–{service_end_minutes} mins), setting var {assignment_var} to 0"
                )
                self.model.Add(assignment_var == 0)


    def add_service_transition_constraint(self) -> None:
        """
        Prevent staff from being assigned to overlapping service assignments
        that do not allow sufficient travel and buffer time between them.
        """
        start_time = time()
        logging.info("Adding service transition (overlap) constraints...")

        # For each staff, ensure they are not assigned to overlapping services
        for staff in self.roster:
            for sa_id_a, conflicting_ids in self.overlap_map.items():
                for sa_id_b in conflicting_ids:
                    var_a = self.assignment_vars[(staff.id, sa_id_a)]
                    var_b = self.assignment_vars[(staff.id, sa_id_b)]

                    # Staff cannot be assigned to both conflicting services
                    self.model.Add(var_a + var_b <= 1)

        logging.info(f"Added service transition constraints in {time() - start_time:.2f}s")

    def add_single_service_constraints(self):
        """
        Enforces Single (S) service assignment rules, but only for FlightZone services:
        1. A staff member can be assigned to at most one 'S' type service per flight.
        2. If assigned to an 'S' service, they cannot be assigned to any other service on the same flight.

        These constraints are skipped for CommonZone services (service_assignment.flight_number is None).
        As CommonZone services can only be either Single or Fixed, the service transition constraint will make sure
        that a staff member is not assigned to multiple CommonZone services (at same or different location) at the same time.
        """

        # Group service assignments by (flight_number, staff_id)
        flight_staff_to_vars = defaultdict(lambda: {"S": [], "other": []})

        for (staff_id, service_assignment_id), var in self.assignment_vars.items():
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
            self.model.Add(sum(s_vars) <= 1)

            if not other_vars:
                continue

            # Constraint 2: If assigned to an 'S' service, cannot be assigned to other services on the same flight
            has_s = self.model.NewBoolVar(f's_assigned_{flight_number}_{staff_id}')
            self.model.Add(sum(s_vars) == 1).OnlyEnforceIf(has_s)
            self.model.Add(sum(s_vars) == 0).OnlyEnforceIf(has_s.Not())

            self.model.Add(sum(other_vars) == 0).OnlyEnforceIf(has_s)

    def add_fixed_service_constraints(self):
        """
        Enforces Fixed (F) service assignment rules:
        1. For FlightZone:
        - A staff member can be assigned to at most one Fixed (F) service per flight.

        2. Across all zones (FlightZone + CommonZone):
        - A staff member can be assigned to only one specific Fixed service_id for the entire day (repeated at different times is okay).
        - If assigned to any Fixed (F) service, staff cannot be assigned to any non-Fixed (S/C/M) service for the whole day.
        """

        # Step 1: FlightZone — at most one Fixed per flight
        flight_staff_to_fixed_vars = defaultdict(list)

        for (staff_id, sa_id), var in self.assignment_vars.items():
            sa = self.service_assignment_map[sa_id]
            if sa.flight_number is not None and sa.service_type == 'F':
                flight_staff_to_fixed_vars[(sa.flight_number, staff_id)].append(var)

        for (flight_number, staff_id), fixed_vars in flight_staff_to_fixed_vars.items():
            self.model.Add(sum(fixed_vars) <= 1)

        # Step 2: Only one Fixed service_id per staff for the whole day
        staff_to_fixed_services = defaultdict(lambda: defaultdict(list))

        for (staff_id, sa_id), var in self.assignment_vars.items():
            sa = self.service_assignment_map[sa_id]
            if sa.service_type == 'F':
                staff_to_fixed_services[staff_id][sa.service_id].append(var)

        for staff_id, service_to_vars in staff_to_fixed_services.items():
            service_flags = []
            for service_id, vars_for_service in service_to_vars.items():
                flag = self.model.NewBoolVar(f"staff_{staff_id}_uses_fixed_{service_id}")
                self.model.Add(sum(vars_for_service) >= 1).OnlyEnforceIf(flag)
                self.model.Add(sum(vars_for_service) == 0).OnlyEnforceIf(flag.Not())
                service_flags.append(flag)

            self.model.Add(sum(service_flags) <= 1)

        # Step 3: If assigned to any Fixed service, block all non-Fixed assignments (whole day)
        for staff_id in set(staff_id for (staff_id, _) in self.assignment_vars):
            fixed_vars = []
            non_fixed_vars = []

            for (s_id, sa_id), var in self.assignment_vars.items():
                if s_id != staff_id:
                    continue
                sa = self.service_assignment_map[sa_id]
                if sa.service_type == 'F':
                    fixed_vars.append(var)
                else:
                    non_fixed_vars.append(var)

            if fixed_vars and non_fixed_vars:
                fixed_selected = self.model.NewBoolVar(f"staff_{staff_id}_assigned_fixed")
                self.model.Add(sum(fixed_vars) >= 1).OnlyEnforceIf(fixed_selected)
                self.model.Add(sum(fixed_vars) == 0).OnlyEnforceIf(fixed_selected.Not())

                for nf_var in non_fixed_vars:
                    self.model.Add(nf_var == 0).OnlyEnforceIf(fixed_selected)

    def add_multi_task_service_constraints(self):
        """
        Enforces:
        - Staff cannot be assigned to mutually exclusive multi-task services on the same flight.
        - The number of multi-task services per staff on a flight is bounded by multi_task_limit.
        """
        logging.debug("Adding multi-task service constraints...")

        # Group multi-task service assignments by flight number
        flight_service_map = defaultdict(list)
        for sa in self.service_assignments:
            if sa.service_type == ServiceType.MULTI_TASK and sa.flight_number:
                flight_service_map[sa.flight_number].append(sa)

        for staff in self.roster:
            for flight_number, flight_services in flight_service_map.items():
                # All multi-task service assignments on this flight that this staff might be assigned to
                staff_services = [
                    sa for sa in flight_services if (staff.id, sa.id) in self.assignment_vars
                ]
                staff_vars = {
                    sa.id: self.assignment_vars[(staff.id, sa.id)] for sa in staff_services
                }

                self._apply_exclude_services_constraint(staff_services, staff_vars, staff.id, flight_number)
                self._apply_multi_task_limit_constraint(staff_services, staff_vars, staff.id, flight_number)

    def _apply_exclude_services_constraint(self, staff_services, staff_vars, staff_id, flight_number):
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
                    self.model.Add(var1 + var2 <= 1)

    def _apply_multi_task_limit_constraint(self, staff_services, staff_vars, staff_id, flight_number):
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
            self.model.Add(total <= limit)

    def set_objective(self) -> None:
        """
        Set the optimization objective based on the strategy defined in settings:
        - MINIMIZE_STAFF: Use the fewest number of staff while covering all service assignments.
        - BALANCE_WORKLOAD: Distribute assignments evenly across all staff.
        """

        # Create a binary variable: whether a staff is used (i.e., assigned at least once)
        staff_used = {
            staff.id: self.model.NewBoolVar(f"staff_used_{staff.id}")
            for staff in self.roster
        }

        # Ensure that staff_used is 1 if any assignment is made
        for staff in self.roster:
            staff_assignments = [
                var for (staff_id, _), var in self.assignment_vars.items()
                if staff_id == staff.id
            ]

            # If staff has any assignment, staff_used[staff_id] == 1
            self.model.AddMaxEquality(staff_used[staff.id], staff_assignments)
                
        # Total number of staff used
        total_staff_used = self.model.NewIntVar(0, len(self.roster), "total_staff_used")
        self.model.Add(total_staff_used == sum(staff_used.values()))

        # Total number of assignments made
        assignment_var_list = list(self.assignment_vars.values())
        total_assignments = self.model.NewIntVar(0, len(assignment_var_list), "total_assignments")
        self.model.Add(total_assignments == sum(assignment_var_list))

        # Priority score: lower priority values (like 22.3 > 44.12) are better → negative weighting
        priority_score = sum(
            -int(self.service_assignment_map[service_assignment_id].priority * 1000) * var
            for (_, service_assignment_id), var in self.assignment_vars.items()
        )

        # Strategy-driven objective
        strategy = self.settings.assignment_strategy

        if strategy == AssignmentStrategy.MINIMIZE_STAFF:
            self.model.Maximize(
                1_000_000_000 * total_assignments +   # Maximize total assignments (most important)
                1_000 * priority_score -              # Favor lower priority values
                total_staff_used                      # Then minimize staff used
            )
        elif strategy == AssignmentStrategy.BALANCE_WORKLOAD:
            self.model.Maximize(
                1_000_000_000 * total_assignments +   # Maximize total assignments (most important)
                1_000 * priority_score +              # Favor lower priority values
                total_staff_used                      # Then maximize staff used
            )  
          
        # Now, define the objective depending on the strategy
        # strategy = self.settings.assignment_strategy
        # if strategy == AssignmentStrategy.MINIMIZE_STAFF:
        #     # Maximize total assignments first, then minimize staff used
        #     self.model.Maximize(
        #         1000 * total_assignments - total_staff_used
        #     )
        # elif strategy == AssignmentStrategy.BALANCE_WORKLOAD:
        #     # Maximize total assignments and maximize staff used
        #     self.model.Maximize(
        #         1000 * total_assignments + total_staff_used
        #     )    

    def run(self) -> SchedulerResult:
        """Run the optimization and store results."""
        logging.info("Starting solver...")
        start_time = time()

        self.create_assignment_variables()
        self.add_staff_certification_constraint()
        self.add_staff_eligibility_constraint()
        self.add_staff_count_constraint()
        self.add_staff_availability_constraint()
        self.add_service_transition_constraint()
        self.add_single_service_constraints()
        self.add_fixed_service_constraints()
        self.add_multi_task_service_constraints()
        self.set_objective()
        
        status = self.solver.Solve(self.model)
        self.solve_time = time() - start_time

        if status == cp_model.OPTIMAL:
            self.solution_status = SchedulerResult.OPTIMAL
        elif status == cp_model.FEASIBLE:
            self.solution_status = SchedulerResult.FEASIBLE
        elif status == cp_model.INFEASIBLE:
            self.solution_status = SchedulerResult.INFEASIBLE
        else:
            self.solution_status = SchedulerResult.UNKNOWN
        
        if self.solution_status in (SchedulerResult.OPTIMAL, SchedulerResult.FEASIBLE):
            self._store_solution()
            self.objective_value = self.solver.ObjectiveValue()

        logging.info(
                f"Solver finished with status: {self.solution_status} "
                f"in {self.solve_time:.2f}s "
                f"(objective: {self.objective_value})"
            )
        return self.solution_status

    def _store_solution(self) -> None:
        """Extract and store the solution from the solver."""
        self.solution = {
            (staff_id, service_assignment_id): bool(self.solver.Value(var))
            for (staff_id, service_assignment_id), var in self.assignment_vars.items()
        }

    def get_assignments(self) -> Dict[int, List[int]]:
        """
        Get assignments in staff-centric format.
        Returns: {staff_id: [list of assigned service_assignment_ids]}
        """
        assignments = {staff.id: [] for staff in self.roster}
        
        for (staff_id, service_assignment_id), assigned in self.solution.items():
            if assigned:
                assignments[staff_id].append(service_assignment_id)
        
        return assignments

    def get_service_coverage(self) -> Dict[int, int]:
        """
        Get how many staff are assigned to each service assignment.
        Returns: {service_assignment_id: assigned_staff_count}
        """
        coverage = {service_assignment.id: 0 for service_assignment in self.service_assignments}
        
        for (staff_id, service_assignment_id), assigned in self.solution.items():
            if assigned:
                coverage[service_assignment_id] += 1
        
        return coverage