from ortools.sat.python import cp_model
from typing import Optional, List, Dict, Tuple
from opspilot.core.scheduler_result import SchedulerResult
from opspilot.models import Staff, Service, Flight, ServiceAssignment, TravelTime, Settings, AssignmentStrategy, Location
from opspilot.services import OverlapDetectionService
from opspilot.constraints import StaffCertificationConstraint, StaffEligibilityConstraint, StaffCountConstraint, StaffAvailabilityConstraint, StaffRoleConstraint
from opspilot.constraints import ServiceTransitionConstraint, SingleServiceConstraint, FixedServiceConstraint, MultiTaskServiceConstraint
from opspilot.strategies import MinimizeStaffStrategy, BalanceWorkloadStrategy
from opspilot.plans import AllocationPlan
from time import time
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
        hints: Optional[AllocationPlan] = None
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
        self.hints = hints
        
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
        self.travel_time_map = {(travel_time.origin_location_id, travel_time.destination_location_id): travel_time.travel_minutes for travel_time in travel_times}
        
        # Initialize overlap detector
        overlap_detector = OverlapDetectionService(
            service_assignments=self.service_assignments,
            flight_map=self.flight_map,
            travel_time_map=self.travel_time_map,
            settings=self.settings
        )

        self.overlap_map = overlap_detector.detect_overlaps()
        
        # Create constraints
        self.constraints = [
            StaffCertificationConstraint(
                staff_map=self.staff_map,
                service_assignment_map=self.service_assignment_map,
                service_map=self.service_map,
            ),
            StaffEligibilityConstraint(
                staff_map=self.staff_map,
                service_assignment_map=self.service_assignment_map,
            ),
            StaffCountConstraint(service_assignments=self.service_assignments),
            StaffAvailabilityConstraint(
                roster=self.roster,
                service_assignments=self.service_assignments,
                flight_map=self.flight_map
            ),
            StaffRoleConstraint(
                staff_map=self.staff_map,
                service_assignment_map=self.service_assignment_map,
            ),
            ServiceTransitionConstraint(
                roster=self.roster,
                overlap_map=self.overlap_map,
                service_assignment_map=self.service_assignment_map,
                service_map=self.service_map,
                flight_map=self.flight_map
            ),
            SingleServiceConstraint(
                service_assignment_map=self.service_assignment_map,
            ),
            FixedServiceConstraint(
                service_assignment_map=self.service_assignment_map,
            ),
            MultiTaskServiceConstraint(
                service_assignments=self.service_assignments,
                roster=self.roster,
                service_map=self.service_map,
            ),
        ]
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
                key = (staff.id, service_assignment.id)
                var_name = f"staff_{staff.id}_service_assignment_{service_assignment.id}"
                self.assignment_vars[key] = self.model.NewBoolVar(var_name)
                
                # Apply hints if provided
                if self.hints:
                    hint = self.hints.get_allocation(service_assignment.id, staff.id)
                    if hint:
                        logging.debug(f"Applying hint: {hint} for key: {key}")
                        self.model.AddHint(self.assignment_vars[key], 1)
        
        logging.info(f"Created {len(self.assignment_vars)} assignment variables in {time() - start_time:.2f}s")

    def apply_constraints(self) -> None:
        """Apply all constraints to the model."""
        start_time = time()
        logging.info("Applying constraints...")

        for constraint in self.constraints:
            constraint.apply(self.model, self.assignment_vars)

        logging.info(f"Applied constraints in {time() - start_time:.2f}s")

    def set_objective(self) -> None:
        """
        Set the optimization objective based on the strategy:
        - MINIMIZE_STAFF: Use the fewest number of staff while covering all service assignments.
        - BALANCE_WORKLOAD: Distribute assignments based on staff priorities and traits.
        """

        start_time = time()
        logging.info("Applying assignment strategy...")

        assignment_strategy = self.settings.assignment_strategy

        if assignment_strategy == AssignmentStrategy.MINIMIZE_STAFF:
            strategy = MinimizeStaffStrategy(
                roster=self.roster,
                service_assignment_map=self.service_assignment_map,)
        elif assignment_strategy == AssignmentStrategy.BALANCE_WORKLOAD:
            strategy = BalanceWorkloadStrategy(
                roster=self.roster,
                service_assignment_map=self.service_assignment_map,
                staff_map=self.staff_map,
            )  
        else:
            raise ValueError(f"Unknown assignment strategy: {strategy}")
        
        strategy.apply(self.model, self.assignment_vars)
        logging.info(f"Assignment strategy set to {assignment_strategy.name} in {time() - start_time:.2f}s")

    def run(self) -> SchedulerResult:
        """Run the optimization and store results."""
        self.create_assignment_variables()
        self.apply_constraints()
        self.set_objective()
        
        logging.info("Starting solver...")
        start_time = time()

        status = self.solver.Solve(self.model)
        self.solve_time = time() - start_time

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            self.solution_status = SchedulerResult.FOUND
        else:
            # cp_model.INFEASIBLE
            self.solution_status = SchedulerResult.NOT_FOUND
        
        if self.solution_status == SchedulerResult.FOUND:
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
    
    def get_assigned_staff(self, service_assignment_id: int) -> List[int]:
        """
        Get a list of staff IDs assigned to the given service assignment.
        
        Args:
            service_assignment_id: ID of the service assignment
        
        Returns:
            List of staff IDs who are assigned to this service assignment.
        """
        return [
            staff_id
            for (staff_id, sa_id), assigned in self.solution.items()
            if sa_id == service_assignment_id and assigned
        ]

    def get_allocation_plan(self, location_map: Dict[int, 'Location'],) -> AllocationPlan:
        """
        Convert the current solution into an AllocationPlan object.
        
        Returns:
            AllocationPlan containing all assignments from the current solution
        """
        # Initialize the allocation plan with all required components
        allocation_plan = AllocationPlan(
            service_assignment_map=self.service_assignment_map,
            service_map=self.service_map,
            staff_map=self.staff_map,
            flight_map=self.flight_map,
            location_map=location_map,
        )
        
        # If no solution exists, return empty plan
        if self.solution_status != SchedulerResult.FOUND:
            return allocation_plan
        
        # Populate the allocation plan with assignments from the solution
        for (staff_id, service_assignment_id), assigned in self.solution.items():
            if assigned:  # Only add positive assignments
                allocation_plan.add_allocation(
                    service_assignment_id=service_assignment_id,
                    staff_id=staff_id
                )
        
        return allocation_plan