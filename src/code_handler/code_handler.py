from abc import ABC, abstractmethod
from enum import Enum

class Language(Enum):
    C = "C"
    Solidity = "Solidity"

class CodeHandler(ABC):
    @abstractmethod
    def get_code(self) -> str:
        pass

    @abstractmethod
    def get_language(self) -> Language:
        pass

    @abstractmethod
    def get_format(self) -> str:
        pass

    @abstractmethod
    def get_assert_format(self) -> str:
        pass

    @abstractmethod
    def get_assert_pattern(self) -> str:
        pass

    @abstractmethod
    def add_invariant_assertions(self, formula: str) -> str:
        pass

    @abstractmethod
    def get_preconditions(self) -> list[str]:
        pass
