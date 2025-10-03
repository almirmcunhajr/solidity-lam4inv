import logging
import re
import sys
from typing import Optional

from smt.solver import Solver, SatStatus
from smt.z3_solver import Z3Solver
from inv_smt_solver.counter_example import CounterExample, CounterExampleKind
from vc.generator import Generator
from vc.solidity_generator import SolidityGenerator

class InvSMTSolver:
    def __init__(self, solver: Solver, vc_generator: Generator, logger: logging.Logger):
        self.solver = solver
        self._logger = logger.getChild(self.__class__.__name__)
        self.vc_generator = vc_generator

    def _is_ignored_variable(self, variable: str) -> bool:
        pattern = re.compile(r'^(inv-f|post-f|pre-f|trans-f|div0|mod0|.*_.*|.*!)$')
        return bool(pattern.match(variable))

    def _get_precondition_counter_example(self, inv: str) -> Optional[CounterExample]:
        formula, _, _ = self.vc_generator.generate(inv)
        self._logger.debug("Generated precondition VC")
        self._logger.debug(formula)

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
        self._logger.debug("Generated transition VC")
        self._logger.debug(formula)

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
        self._logger.debug("Generated postcondition VC")
        self._logger.debug(formula)

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

if __name__ == "__main__":
    path = sys.argv[1]
    contract_name = sys.argv[2]
    function_name = sys.argv[3]
    inv = sys.argv[4]

    sol_vc_generator = SolidityGenerator(path, logging.getLogger(), contract_name, function_name)
    smt_solver = Z3Solver(timeout=10)
    inv_smt_solver = InvSMTSolver(smt_solver, sol_vc_generator, logging.getLogger())

    ce = inv_smt_solver.get_counter_example(inv)
    if ce is None:
        print("No counter example found; the invariant may be valid.")
        exit(0)

    match ce.kind:
        case CounterExampleKind.NOT_REACHABLE:
            print("Counter example found: the invariant is not reachable.")
            print(ce)
        case CounterExampleKind.NOT_INDUCTIVE:
            print("Counter example found: the invariant is not inductive.")
            print(ce)
        case CounterExampleKind.NOT_PROVABLE:
            print("Counter example found: the invariant does not imply the postcondition.")
            print(ce)

    exit(1)

