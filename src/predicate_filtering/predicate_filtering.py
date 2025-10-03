import logging 

from code_handler.code_handler import CodeHandler
from code_handler.formula_handler import FormulaForm, FormulaHandler
from bmc.bmc import BMC

class PredicateFiltering:
    def __init__(self, code_handler: CodeHandler, formula_handler: FormulaHandler, bmc: BMC, logger: logging.Logger):
        self.bmc = bmc
        self.code_handler = code_handler
        self.formula_handler = formula_handler
        self._logger = logger.getChild(self.__class__.__name__)

    def _verify(self, formula: str) -> bool:
        code = self.code_handler.add_invariant_assertions(formula)
        self._logger.debug(f"Verifying code:\n{code}")
        return self.bmc.verify(code)

    def filter(self, formula: str) -> list[str]:
        form = self.formula_handler.get_form(formula)
        predicates = self.formula_handler.extract_predicates(formula)

        filtered_predicates = []
        if form == FormulaForm.DNF:
            if self._verify(formula):
                valid_predicates = [predicate for predicate in predicates if not self._verify(self.formula_handler.negate_formula(predicate))]
                filtered_predicates.append(self.formula_handler.join_formulas(valid_predicates, FormulaForm.DNF))
        else:
            filtered_predicates.extend([predicate for predicate in predicates if self._verify(predicate)])
        
        return filtered_predicates
