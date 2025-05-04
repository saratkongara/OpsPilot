from ortools.sat.python import cp_model
from typing import Optional, List, Dict, Tuple
from  opspilot.core.scheduler_result import SchedulerResult
from opspilot.models import Staff, Service, Flight, ServiceAssignment, TravelTime, Settings, AssignmentStrategy, ServiceType
from opspilot.services import OverlapDetectionService
from opspilot.constraints import StaffCertificationConstraint, StaffEligibilityConstraint, StaffCountConstraint, StaffAvailabilityConstraint
from opspilot.constraints import ServiceTransitionConstraint, SingleServiceConstraint, FixedServiceConstraint, MultiTaskServiceConstraint
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
                var_name = f"staff_{staff.id}_service_assignment_{service_assignment.id}"
                self.assignment_vars[(staff.id, service_assignment.id)] = self.model.NewBoolVar(var_name)
                
                # Apply previous assignment as hint if available
                if (staff.id, service_assignment.id) in self.previous_assignments:
                    self.model.AddHint(
                        self.assignment_vars[(staff.id, service_assignment.id)],
                        int(self.previous_assignments[(staff.id, service_assignment.id)])
                    )
        
        logging.info(f"Created {len(self.assignment_vars)} assignment variables in {time() - start_time:.2f}s")


    def set_objective(self) -> None:
        """
        Set the optimization objective based on the strategy:
        - MINIMIZE_STAFF: Use the fewest number of staff while covering all service assignments.
        - BALANCE_WORKLOAD: Distribute assignments based on staff priorities and traits.
        """
        strategy = self.settings.assignment_strategy

        if strategy == AssignmentStrategy.MINIMIZE_STAFF:
            self._set_minimize_staff_objective()
        elif strategy == AssignmentStrategy.BALANCE_WORKLOAD:
            self._set_balance_workload_objective()
        else:
            raise ValueError(f"Unknown assignment strategy: {strategy}")

    def _set_minimize_staff_objective(self):
        """
        Objective:
        - Maximize total assignments made (most important)
        - Prefer assignments with lower priority values (i.e., A-10 is better than D+5)
        - Use the minimum number of distinct staff

        This strategy is suitable when reducing total active staff is important — e.g., for lean scheduling.
        """

        # Create a binary variable for whether each staff is used at least once
        staff_used = {
            staff.id: self.model.NewBoolVar(f"staff_used_{staff.id}")
            for staff in self.roster
        }

        # staff_used[staff_id] = 1 if the staff is assigned to any service
        for staff in self.roster:
            staff_assignments = [
                var for (staff_id, _), var in self.assignment_vars.items()
                if staff_id == staff.id
            ]
            self.model.AddMaxEquality(staff_used[staff.id], staff_assignments)

        # Total number of distinct staff used
        total_staff_used = self.model.NewIntVar(0, len(self.roster), "total_staff_used")
        self.model.Add(total_staff_used == sum(staff_used.values()))

        # Total number of assignments actually made
        assignment_var_list = list(self.assignment_vars.values())
        total_assignments = self.model.NewIntVar(0, len(assignment_var_list), "total_assignments")
        self.model.Add(total_assignments == sum(assignment_var_list))

        # Compute a total score from service assignment priorities
        # Lower priority values are better, so we negate the score
        priority_score = sum(
            -int(self.service_assignment_map[sa_id].priority * 1000) * var
            for (_, sa_id), var in self.assignment_vars.items()
        )

        # Maximize assignments first, then priority score, then minimize staff used
        self.model.Maximize(
            1_000_000_000 * total_assignments +  # Primary: complete as many assignments as possible
            1_000 * priority_score -            # Secondary: favor lower-priority services
            total_staff_used                    # Tertiary: minimize how many staff are activated
        )

    def _set_balance_workload_objective(self):
        """
        Objective:
        - Maximize total assignments made (most important)
        - Favor staff whose priority_service matches the assignment
        - Favor staff with lower rank_level (assumed more junior)
        - Favor staff with fewer certifications (to preserve multi-skilled staff for harder tasks)
        - Slightly prefer involving more staff to balance load

        This strategy aims to balance the workload fairly across staff, incorporating traits and preferences.
        """

        # Binary indicator for whether a staff member is used
        staff_used = {
            staff.id: self.model.NewBoolVar(f"staff_used_{staff.id}")
            for staff in self.roster
        }

        # staff_used[staff_id] = 1 if any assignment is made
        for staff in self.roster:
            staff_assignments = [
                var for (staff_id, _), var in self.assignment_vars.items()
                if staff_id == staff.id
            ]
            self.model.AddMaxEquality(staff_used[staff.id], staff_assignments)

        # Total staff used
        total_staff_used = self.model.NewIntVar(0, len(self.roster), "total_staff_used")
        self.model.Add(total_staff_used == sum(staff_used.values()))

        # Total assignments made
        assignment_var_list = list(self.assignment_vars.values())
        total_assignments = self.model.NewIntVar(0, len(assignment_var_list), "total_assignments")
        self.model.Add(total_assignments == sum(assignment_var_list))

        # Per-assignment score considering staff traits and service properties
        objective_terms = []
        for (staff_id, sa_id), var in self.assignment_vars.items():
            sa = self.service_assignment_map[sa_id]
            staff = self.staff_map[staff_id]

            # Lower priority value = higher preference
            priority_score = -int(sa.priority * 1000)

            # Big bonus for assigning staff to their preferred service
            priority_match_bonus = 1 if staff.priority_service_id == sa.service_id else 0

            # Lower rank_level is better
            rank_score = -1 * (staff.rank_level or 0)

            # Fewer certifications is better (preserve multi-skilled staff)
            cert_score = -len(staff.certifications)

            # Combine weights (tunable)
            combined_score = (
                10_000_000 * priority_match_bonus +
                10_000 * priority_score +
                1_000 * rank_score +
                10 * cert_score
            )

            objective_terms.append(combined_score * var)

        # Maximize assignments first, then distribute based on preferences and traits,
        # and finally slightly prefer involving more staff (to balance workload)
        self.model.Maximize(
            1_000_000_000 * total_assignments +  # Primary: maximize service coverage
            sum(objective_terms) +               # Secondary: score based on preferences and traits
            total_staff_used                     # Tertiary: prefer spreading load across staff
        )

    def apply_constraints(self) -> None:
        """Apply all constraints to the model."""
        start_time = time()
        logging.info("Applying constraints...")

        for constraint in self.constraints:
            constraint.apply(self.model, self.assignment_vars)

        logging.info(f"Applied constraints in {time() - start_time:.2f}s")

    def run(self) -> SchedulerResult:
        """Run the optimization and store results."""
        logging.info("Starting solver...")
        start_time = time()

        self.create_assignment_variables()
        self.apply_constraints()
        
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