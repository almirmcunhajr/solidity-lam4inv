import re
from typing import Optional
from smt.solver import SatStatus, Solver
from inv_smt_solver.counter_example import CounterExample, CounterExampleKind

class Code2Inv():
    def __init__(self, solver: Solver):
        self.solver = solver

    def _is_ignored_variable(self, variable: str) -> bool:
        pattern = re.compile(r'^(inv-f|post-f|pre-f|trans-f|div0|mod0|.*_.*|.*!)$')
        return bool(pattern.match(variable))

    def check(self, inv: str, template: str) -> Optional[CounterExample]:
        vc_sections = template.split('SPLIT_HERE_asdfghjklzxcvbnmqwertyuiop') 
        vc_sections = [
            vc_sections[0], 
            vc_sections[1] + vc_sections[2],
            vc_sections[1] + vc_sections[3],
            vc_sections[1] + vc_sections[4]
        ]
    
        precondition_formula = vc_sections[0] + inv + vc_sections[1]
        transition_formula = vc_sections[0] + inv + vc_sections[2]
        postcondition_formula = vc_sections[0] + inv + vc_sections[3]
    
        res = self.solver.check(precondition_formula)
        if res == SatStatus.SAT:
            assignments = self.solver.get_assignments()
            filtered_assignments = {
                decl: assignments[decl]
                for decl in assignments if not self._is_ignored_variable(decl)
            }
            return CounterExample(filtered_assignments, CounterExampleKind.NOT_REACHABLE)
        elif res == SatStatus.UNKNOWN:
            raise TimeoutError(inv)

        assert res == SatStatus.UNSAT
    
        res = self.solver.check(transition_formula)
        if res == SatStatus.SAT:
            assignments = self.solver.get_assignments()
            filtered_assignments = {
                decl: assignments[decl]
                for decl in assignments if not self._is_ignored_variable(decl)
            }
            return CounterExample(filtered_assignments, CounterExampleKind.NOT_INDUCTIVE)
        elif res == SatStatus.UNKNOWN:
            raise TimeoutError(inv)

        assert res == SatStatus.UNSAT
    
        res = self.solver.check(postcondition_formula)
        if res == SatStatus.SAT:
            assignments = self.solver.get_assignments()
            filtered_assignments = {
                x: assignments[x]
                for x in assignments if not self._is_ignored_variable(x)
            }
            return CounterExample(filtered_assignments, CounterExampleKind.NOT_PROVABLE)
        elif res == SatStatus.UNKNOWN:
            raise TimeoutError(inv)
        
        assert res == SatStatus.UNSAT

