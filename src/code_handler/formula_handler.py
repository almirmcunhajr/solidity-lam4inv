from abc import ABC, abstractmethod
from enum import Enum

class FormulaForm(Enum):
    DNF = 1
    CNF = 2

class InvalidCodeFormulaError(Exception):
    pass

class FormulaHandler(ABC):
    @abstractmethod
    def extract_formula(self, expression: str) -> str:
        pass

    @abstractmethod
    def negate_formula(self, formula: str) -> str:
        pass

    @abstractmethod
    def join_formulas(self, formulas: list[str], form: FormulaForm) -> str:
        pass

    @abstractmethod
    def to_smt_lib2(self, formula: str) -> str:
        pass

    @abstractmethod
    def get_form(self, formula: str) -> FormulaForm|None:
        pass

    @abstractmethod
    def extract_predicates(self, formula: str) -> list[str]:
        pass
