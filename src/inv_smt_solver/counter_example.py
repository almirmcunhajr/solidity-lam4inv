from enum import Enum

class CounterExampleKind(Enum):
    NOT_PROVABLE = 0
    NOT_REACHABLE = 1
    NOT_INDUCTIVE = 2

class CounterExample:
    def __init__(self, assignment: dict[str,str], kind: CounterExampleKind):
        self.kind = kind
        self.assignment = assignment

    def __str__(self):
        return ", ".join([f"{var} = {value}" for var, value in self.assignment.items()])