from abc import ABC, abstractmethod

class Generator(ABC):
    @abstractmethod
    def generate(self, inv: str) -> tuple[str, str, str]:
        pass
