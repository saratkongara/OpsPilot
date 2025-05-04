from typing import Dict, Tuple, List
from ortools.sat.python.cp_model import CpModel, IntVar
from opspilot.models import Staff, ServiceAssignment
from opspilot.strategies import Strategy

class BalanceWorkloadStrategy(Strategy):
    def __init__(
            self, 
            roster: List[Staff], 
            service_assignment_map: Dict[int, ServiceAssignment],
            staff_map: Dict[int, Staff], 
    ):
        self.roster = roster
        self.service_assignment_map = service_assignment_map
        self.staff_map = staff_map

    def apply(self, model: CpModel, assignment_vars: Dict[Tuple[int, int], IntVar]):
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
            staff.id: model.NewBoolVar(f"staff_used_{staff.id}")
            for staff in self.roster
        }

        # staff_used[staff_id] = 1 if any assignment is made
        for staff in self.roster:
            staff_assignments = [
                var for (staff_id, _), var in assignment_vars.items()
                if staff_id == staff.id
            ]
            model.AddMaxEquality(staff_used[staff.id], staff_assignments)

        # Total staff used
        total_staff_used = model.NewIntVar(0, len(self.roster), "total_staff_used")
        model.Add(total_staff_used == sum(staff_used.values()))

        # Total assignments made
        assignment_var_list = list(assignment_vars.values())
        total_assignments = model.NewIntVar(0, len(assignment_var_list), "total_assignments")
        model.Add(total_assignments == sum(assignment_var_list))

        # Per-assignment score considering staff traits and service properties
        objective_terms = []
        for (staff_id, sa_id), var in assignment_vars.items():
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
        model.Maximize(
            1_000_000_000 * total_assignments +  # Primary: maximize service coverage
            sum(objective_terms) +               # Secondary: score based on preferences and traits
            total_staff_used                     # Tertiary: prefer spreading load across staff
        )
