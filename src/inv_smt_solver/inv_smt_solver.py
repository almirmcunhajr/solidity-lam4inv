import logging
import re
from typing import Optional

from smt.solver import Solver, SatStatus
from inv_smt_solver.counter_example import CounterExample, CounterExampleKind
from vc.generator import Generator

class InvSMTSolver:
    def __init__(self, solver: Solver, vc_generator: Generator):
        self.solver = solver
        self.logger = logging.getLogger(__name__)
        self.vc_generator = vc_generator

    def _is_ignored_variable(self, variable: str) -> bool:
        pattern = re.compile(r'^(inv-f|post-f|pre-f|trans-f|div0|mod0|.*_.*|.*!)$')
        return bool(pattern.match(variable))

    def _get_precondition_counter_example(self, inv: str) -> Optional[CounterExample]:
        formula, _, _ = self.vc_generator.generate(inv)
        res = self.solver.check(formula)
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
            
    def _get_transition_counter_example(self, inv: str) -> Optional[CounterExample]:
        _, formula, _ = self.vc_generator.generate(inv)
        res = self.solver.check(formula)
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

    def _get_postcondition_counter_example(self, inv: str) -> Optional[CounterExample]:
        _, _, formula = self.vc_generator.generate(inv)
        res = self.solver.check(formula)
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

    def get_counter_example(self, inv: str) -> Optional[CounterExample]:
        precondition_ce = self._get_precondition_counter_example(inv)
        if precondition_ce:
            return precondition_ce
        
        transition_ce = self._get_transition_counter_example(inv)
        if transition_ce:
            return transition_ce
        
        postcondition_ce = self._get_postcondition_counter_example(inv)
        if postcondition_ce:
            return postcondition_ce
