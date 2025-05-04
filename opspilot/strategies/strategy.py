from abc import ABC, abstractmethod
from typing import Dict, Tuple
from ortools.sat.python.cp_model import CpModel, IntVar

class Strategy(ABC):
    """
    Base class for all objectives in the scheduling system.
    """
    @abstractmethod
    def apply(self, model: CpModel, assignment_vars: Dict[Tuple[int, int], IntVar]):
        pass