from abc import ABC, abstractmethod
from typing import Dict, Tuple
from ortools.sat.python.cp_model import CpModel, IntVar

class Constraint(ABC):
    """
    Base class for all constraints in the scheduling system.
    """
    @abstractmethod
    def apply(self, model: CpModel, assignments: Dict[Tuple[int, int], IntVar]):
        pass
