import re
import tempfile
from typing import Optional

from slither.core.cfg.node import OperationWithLValue
from slither.core.declarations import Contract

from code_handler.formula_handler import FormulaHandler, FormulaForm, InvalidCodeFormulaError

from slither.slither import Slither
from slither.slithir.operations import BinaryType, UnaryType, Binary, Unary

class SoliditySMTLIB2Translator:
    op_map = {
        BinaryType.ADDITION: '+',
        BinaryType.SUBTRACTION: '-',
        BinaryType.MULTIPLICATION: '*',
        BinaryType.DIVISION: 'div',
        BinaryType.MODULO: 'mod',
        BinaryType.LESS: '<',
        BinaryType.GREATER: '>',
        BinaryType.LESS_EQUAL: '<=',
        BinaryType.GREATER_EQUAL: '>=',
        BinaryType.EQUAL: '=',
        BinaryType.NOT_EQUAL: 'distinct',
        BinaryType.ANDAND: 'and',
        BinaryType.OROR: 'or',
        UnaryType.BANG: 'not'
    }

    def _op_to_smt(self, ir) -> str:
        if isinstance(ir, Binary):
            return f'( {self.op_map[ir.type]} {ir.read[0]} {ir.read[1]} )'
        if isinstance(ir, Unary):
            return f'( {self.op_map[ir.type]} {ir.read[0]} )'
        return f'{ir.read[0]}'


    def _get_contract(self, slither: Slither, contract_name: str) -> Optional[Contract]:
        for contract in slither.contracts:
            if contract.name == contract_name:
                return contract

    def translate_expression(self, expression: str) -> str:
        expression = self._rewrite_ternary(expression)
        try:
            code = f"""
pragma solidity ^0.8.0;

contract Contract {{
    {self._get_variables_declarations(expression)}

    constructor() {{
        bool _res = {expression};
    }}
}}
            """
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.sol') as tmp:
                tmp.write(code)
                tmp.seek(0)
            slither = Slither(tmp.name, disable_plugins=["solc-ast-exporter"])
            contract = self._get_contract(slither, 'Contract')
            if contract is None:
                return ""
            function = contract.get_function_from_full_name('constructor()')
            if function is None:
                return ""

            irs = []
            for node in function.nodes:
                for ir in node.irs[:-1]:
                    if isinstance(ir, OperationWithLValue) and ir.lvalue:
                        irs.append(ir)
            
            formula = '\n'.join([f'( = {ir.lvalue} {self._op_to_smt(ir)} )' for ir in irs[:-1]])
            if len(irs) > 1:
                return f"""( and
    {formula}
    {self._op_to_smt(irs[-1])}
)
            """
            return self._op_to_smt(irs[0])
        except Exception as e:
            raise InvalidCodeFormulaError(str(e))
        
    def _get_variables_declarations(self, expression: str) -> str:
        keywords = {'true', 'false'}
        pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
        variables = [
                token for token in re.findall(pattern, expression)
                if token not in keywords
        ]
        return ''.join([f'uint256 {var};' for var in variables])
        
    def _rewrite_ternary(self, expression: str) -> str:
        pattern = r'([^?]+)\s*\?\s*([^:]+)\s*:\s*(.+)'
        repl = r'((\1) && (\2)) || (!(\1) && (\3))' # https://en.wikipedia.org/wiki/Conditioned_disjunction
        return re.sub(pattern, repl, expression)

class SolidityFormulaHandler(FormulaHandler):
    def __init__(self):
        self.smtlib2_translator = SoliditySMTLIB2Translator()

    def extract_formula(self, expression: str) -> str:
        match = re.search(r'assert\s*\((.*)\)', expression)
        if not match:
            raise InvalidCodeFormulaError(f'Solidity assertion "{expression}" does not match the expected format')
        
        formula = match.group(1).strip()
        return formula
    
    def negate_formula(self, formula: str) -> str:
        return f"!({formula})"

    def join_formulas(self, formulas: list[str], form: FormulaForm) -> str:
        if form == FormulaForm.DNF:
            return ' || '.join(f'({formula})' for formula in formulas)
        if form == FormulaForm.CNF:
            return ' && '.join(f'({formula})' for formula in formulas)
        
    def _is_balanced_parentheses(self, expr: str) -> bool:
        balance = 0
        for char in expr:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
                if balance < 0:
                    return False
        return balance == 0
    
    def to_smt_lib2(self, formula: str) -> str:
        return self.smtlib2_translator.translate_expression(formula)

    def get_form(self, formula: str) -> FormulaForm|None:
        smtlib2_formula = self.to_smt_lib2(formula)
        and_index = smtlib2_formula.find('and')
        or_index = smtlib2_formula.find('or')
        if and_index == -1 and or_index == -1:
            return
        if and_index == -1:
            return FormulaForm.DNF
        if or_index == -1:
            return FormulaForm.CNF
        return FormulaForm.CNF if and_index < or_index else FormulaForm.DNF

    def extract_predicates(self, formula: str) -> list[str]:
        form = self.get_form(formula)
        operator = '||' if form == FormulaForm.DNF else '&&'
        predicates = []
        bracket_count = 0
        start = 0
        for i in range(len(formula)):
            if formula[i] == '(':
                bracket_count += 1
            elif formula[i] == ')':
                bracket_count -= 1
            elif bracket_count == 0 and formula[i:i + len(operator)] == operator:
                predicates.append(formula[start:i].strip())
                start = i + len(operator)
        predicates.append(formula[start:].strip())
        return predicates

if __name__ == '__main__':
    translator = SoliditySMTLIB2Translator()
    formula = translator.translate_expression('x >= y')
    print(formula)
