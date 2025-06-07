from typing import Dict, Tuple, List
from ortools.sat.python.cp_model import CpModel, IntVar
from opspilot.models import Staff, ServiceAssignment
from opspilot.strategies import Strategy

class MultiDepartmentStrategy(Strategy):
    def __init__(
            self, 
            roster: List[Staff], 
            service_assignment_map: Dict[int, ServiceAssignment],
            staff_map: Dict[int, Staff],
            department_factor: int = 10  # Higher factor gives more weight to same-department assignments
    ):
        self.roster = roster
        self.service_assignment_map = service_assignment_map
        self.staff_map = staff_map
        self.department_factor = department_factor

    def apply(self, model: CpModel, assignment_vars: Dict[Tuple[int, int], IntVar]):
        """
        Objective: 
        - Maximize total assignments made, prioritizing same-department assignments.
        - Still consider priority and role matching as in TurnaroundWorkloadStrategy.
        - Apply a department factor that boosts the score for same-department assignments.
        """
        objective_terms = []

        for (staff_id, service_assignment_id), var in assignment_vars.items():
            service_assignment = self.service_assignment_map[service_assignment_id]
            staff = self.staff_map[staff_id]

            # Base priority score: lower original priority number means higher score
            base_priority_score = 100 - service_assignment.priority

            # Role factor: higher if staff's role is in an earlier priority list
            role_factor = 1  # Default factor
            
            if service_assignment.priority_roles and staff.role_code:
                for i, role_list in enumerate(service_assignment.priority_roles):
                    if staff.role_code in role_list:
                        role_factor = len(service_assignment.priority_roles) - i
                        break  # Found the highest priority match for the role

            # Department factor: higher if staff is from the same department as the service assignment
            department_score = self.department_factor if staff.department_id == service_assignment.department_id else 1

            # Combine scores for the objective term
            # The higher the combined score, the more preferred the assignment
            combined_score = base_priority_score * role_factor * department_score
            objective_terms.append(var * int(combined_score))  # CP-SAT solver expects integer coefficients

        # Set the objective to maximize the weighted sum of assignments
        model.Maximize(sum(objective_terms))
        return
