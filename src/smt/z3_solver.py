import z3

from smt.solver import Solver, SatStatus, InvalidSMTLIB2FormulaError
from utils.utils import run_with_timeout

class Z3Solver(Solver):
    def __init__(self, timeout: int):
        self.solver = z3.Solver()
        self.solver.set(auto_config=False)
        self.timeout = timeout
        if self.timeout >= 0:
            self.solver.set('timeout', self.timeout*1000)

    def check(self, formula: str) -> SatStatus:
        self.solver.reset()
        try:
            decl = z3.parse_smt2_string(formula)
        except z3.Z3Exception:
            raise InvalidSMTLIB2FormulaError(formula)
        
        self.solver.add(decl)
        try:
            res = run_with_timeout(self.solver.check, timeout=self.timeout)
        except TimeoutError:
            return SatStatus.UNKNOWN
        
        if res == z3.sat:
            return SatStatus.SAT
        elif res == z3.unsat:
            return SatStatus.UNSAT
        else:
            return SatStatus.UNKNOWN

    def get_assignments(self) -> dict[str,str]:
        model = self.solver.model()
        assignments = {}
        for decl in model:
            if decl.arity() > 0:
                continue
            assignments[str(decl)] = str(model[decl])
        return assignments
