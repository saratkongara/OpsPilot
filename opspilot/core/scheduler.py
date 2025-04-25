from ortools.sat.python import cp_model
from typing import Optional, List, Dict, Tuple
from  opspilot.core.scheduler_result import SchedulerResult
from opspilot.models import Staff, Service, ServiceAssignment, Settings, OptimizationStrategy, CertificationRequirement
import logging
from time import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class Scheduler:
    def __init__(
        self,
        roster: List[Staff],
        service_assignments: List[ServiceAssignment],
        services: List[Service],
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
        self.service_assignments = service_assignments
        self.services = services
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

    def add_certification_constraints(self) -> None:
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

    def add_staff_count_constraints(self) -> None:
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

    def set_objective(self) -> None:
        """
        Set the optimization objective based on the strategy defined in settings:
        - MINIMIZE_STAFF: Use the fewest number of staff while covering all service assignments.
        - BALANCE_WORKLOAD: Distribute assignments evenly across all staff.
        """

        strategy = self.settings.optimization_strategy
        logging.info(f"Setting optimization objective for strategy: {strategy}")
        
        if strategy == OptimizationStrategy.MINIMIZE_STAFF:
            staff_used_vars = {}
            
            for staff in self.roster:     
                # Get all possible assignments for this staff
                staff_assignment_vars = [
                    self.assignment_vars[(staff.id, sa.id)]
                    for sa in self.service_assignments
                    # if sa.can_assign(staff) # certification/availability check
                ]
                
                if staff_assignment_vars:
                    used = self.model.NewBoolVar(f"used_{staff.id}")
                    self.model.AddMaxEquality(used, staff_assignment_vars)
                    staff_used_vars[staff.id] = used
            
            # Primary objective
            self.model.Minimize(sum(staff_used_vars.values()))
        elif strategy == OptimizationStrategy.BALANCE_WORKLOAD:
            # Track total assignments per staff member
            staff_assignment_counts = []
            
            for staff in self.roster:
                # Get all possible assignments for this staff
                staff_assignment_vars = [
                    self.assignment_vars[(staff.id, sa.id)]
                    for sa in self.service_assignments
                    # if sa.can_assign(staff) # certification/availability check
                ]
                
                if staff_assignment_vars:
                    count = self.model.NewIntVar(0, len(self.service_assignments), f"staff_{staff.id}_assignment_count")
                    self.model.Add(count == sum(staff_assignment_vars))
                    staff_assignment_counts.append(count)
            
            if staff_assignment_counts:
                # Minimize the maximum assignments any single staff gets
                max_assignments = self.model.NewIntVar(0, len(self.service_assignments), "max_assignments")
                self.model.AddMaxEquality(max_assignments, staff_assignment_counts)
                self.model.Minimize(max_assignments)

    def run(self) -> SchedulerResult:
        """Run the optimization and store results."""
        logging.info("Starting solver...")
        start_time = time()

        self.create_assignment_variables()
        self.add_certification_constraints()  # Start with just certifications
        self.add_staff_count_constraints()  # Will add later
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