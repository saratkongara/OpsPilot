from typing import Dict, Tuple, List
from ortools.sat.python.cp_model import CpModel, IntVar
from opspilot.models import Staff, ServiceAssignment
from opspilot.strategies import Strategy

class MinimizeStaffStrategy(Strategy):
    def __init__(
            self, 
            roster: List[Staff], 
            service_assignment_map: Dict[int, ServiceAssignment], 
    ):
        self.roster = roster
        self.service_assignment_map = service_assignment_map

    def apply(self, model: CpModel, assignment_vars: Dict[Tuple[int, int], IntVar]):
        """
        Objective:
        - Maximize total assignments made (most important)
        - Prefer assignments with lower priority values (i.e., A-10 is better than D+5)
        - Use the minimum number of distinct staff

        This strategy is suitable when reducing total active staff is important — e.g., for lean scheduling.
        """

        # Create a binary variable for whether each staff is used at least once
        staff_used = {
            staff.id: model.NewBoolVar(f"staff_used_{staff.id}")
            for staff in self.roster
        }

        # staff_used[staff_id] = 1 if the staff is assigned to any service
        for staff in self.roster:
            staff_assignments = [
                var for (staff_id, _), var in assignment_vars.items()
                if staff_id == staff.id
            ]
            model.AddMaxEquality(staff_used[staff.id], staff_assignments)

        # Total number of distinct staff used
        total_staff_used = model.NewIntVar(0, len(self.roster), "total_staff_used")
        model.Add(total_staff_used == sum(staff_used.values()))

        # Total number of assignments actually made
        assignment_var_list = list(assignment_vars.values())
        total_assignments = model.NewIntVar(0, len(assignment_var_list), "total_assignments")
        model.Add(total_assignments == sum(assignment_var_list))

        # Compute a total score from service assignment priorities
        # Lower priority values are better, so we negate the score
        priority_score = sum(
            -int(self.service_assignment_map[sa_id].priority * 1000) * var
            for (_, sa_id), var in assignment_vars.items()
        )

        # Maximize assignments first, then priority score, then minimize staff used
        model.Maximize(
            1_000_000_000 * total_assignments +  # Primary: complete as many assignments as possible
            1_000 * priority_score -            # Secondary: favor lower-priority services
            total_staff_used                    # Tertiary: minimize how many staff are activated
        )
