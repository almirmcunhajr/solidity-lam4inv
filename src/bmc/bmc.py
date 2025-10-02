import logging

from abc import ABC, abstractmethod

class InvalidCodeError(Exception):
    pass

class BMC(ABC):
    @abstractmethod
    def verify(self, code: str) -> bool:
        pass
