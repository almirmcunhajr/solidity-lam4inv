from abc import ABC, abstractmethod
from enum import Enum

class SatStatus(Enum):
    SAT = 1
    UNSAT = 2
    UNKNOWN = 3

class Solver(ABC):
    @abstractmethod
    def check(self, formula: str) -> SatStatus:
        pass
    
    @abstractmethod
    def get_assignments(self) -> dict[str,str]:
        pass

class InvalidSMTLIB2FormulaError(Exception):
    pass
