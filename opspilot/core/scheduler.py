from ortools.sat.python import cp_model
from typing import Optional, List, Dict, Tuple
from  opspilot.core.scheduler_result import SchedulerResult
from opspilot.models import Staff, Service, Flight, ServiceAssignment, Settings, AssignmentStrategy, CertificationRequirement
import logging
from time import time

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
        previous_assignments: Optional[Dict[Tuple[int, int], bool]] = None
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

    def add_certification_constraint(self) -> None:
        """Ensure staff only get assigned to services they're certified for."""
        start_time = time()
        logging.info("Adding certification constraints...")
        
        for (staff_id, service_assignment_id), var in self.assignment_vars.items():
            staff = self.staff_map[staff_id]
            service_assignment = self.service_assignment_map[service_assignment_id]
            service = self.service_map[service_assignment.service_id]
            
            if service.certification_requirement == CertificationRequirement.ALL:
                # Staff must have ALL required certifications
                required_certs = set(service.certifications)
                staff_certs = set(staff.certifications)
                if not required_certs.issubset(staff_certs):
                    self.model.Add(var == 0)
            
            elif service.certification_requirement == CertificationRequirement.ANY:
                # Staff must have at least ONE required certification
                has_any = any(
                    cert_id in staff.certifications
                    for cert_id in service.certifications
                )
                if not has_any:
                    self.model.Add(var == 0)
        
        logging.info(f"Added certification constraints in {time() - start_time:.2f}s")

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
        """Ensure staff are only assigned to services they are available for."""
        for (staff_id, service_assignment_id), assignment_var in self.assignment_vars.items():
            staff = next(staff for staff in self.roster if staff.id == staff_id)
            service_assignment = next(sa for sa in self.service_assignments if sa.id == service_assignment_id)

            # If it's flight-related, resolve using relative_start and relative_end
            if service_assignment.flight_number:
                flight = next(flight for flight in self.flights if flight.number == service_assignment.flight_number)
                service_start_minutes, service_end_minutes = flight.get_service_time_minutes(
                    service_assignment.relative_start,
                    service_assignment.relative_end
                )
            else:
                # Non-flight services (like Common Zone), use absolute start_time and end_time
                service_start_minutes = service_assignment.start_minutes
                service_end_minutes = service_assignment.end_minutes

            # Check staff availability
            if not staff.is_available_for_service(service_start_minutes, service_end_minutes):
                logging.debug(
                    f"Staff {staff_id} not available for service_assignment {service_assignment_id} "
                    f"(Service time {service_start_minutes}–{service_end_minutes} mins), setting var {assignment_var} to 0"
                )
                self.model.Add(assignment_var == 0)


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

        # Now, define the objective depending on the strategy
        strategy = self.settings.assignment_strategy
        if strategy == AssignmentStrategy.MINIMIZE_STAFF:
            # Maximize total assignments first, then minimize staff used
            self.model.Maximize(
                1000 * total_assignments - total_staff_used
            )
        elif strategy == AssignmentStrategy.BALANCE_WORKLOAD:
            # Maximize total assignments and maximize staff used
            self.model.Maximize(
                1000 * total_assignments + total_staff_used
            )    

    def run(self) -> SchedulerResult:
        """Run the optimization and store results."""
        logging.info("Starting solver...")
        start_time = time()

        self.create_assignment_variables()
        self.add_certification_constraint()
        self.add_staff_count_constraint()
        self.add_staff_availability_constraint()
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