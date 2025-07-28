import os
from itertools import chain

from slither.core.solidity_types.elementary_type import Int, Uint
from slither.slither import Slither
from slither.core.declarations import Contract, Function
from slither.core.cfg.node import Constant, Node, Phi, Variable
from slither.core.dominators.utils import compute_dominators
from slither.slithir.convert import Unary
from slither.slithir.variables.variable import Variable
from slither.slithir.operations import Binary, BinaryType, OperationWithLValue, UnaryType, SolidityCall

from jinja2 import Template

from vc.generator import Generator

class SolidityGenerator(Generator):
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

    _type_map = {
        "bool": "Bool"
    }

    def __init__(self, file_path: str):
        self.slither = Slither(file_path, disable_plugins=["solc-ast-exporter"])

        for t in Int+Uint:
            self._type_map[t] = "Int"

    def generate(self, inv: str) -> tuple[str, str, str]:
        if len(self.slither.contracts) == 0:
            raise ContractNotFound()
        contract = self.slither.contracts[0]

        if len(contract.functions) == 0:
            raise FunctionNotFound()
        function = contract.functions[0]

        compute_dominators(function.nodes)

        loops = self._get_loop_nodes(function)
        if len(loops) == 0:
            raise LoopNotFound()
        loop_header, loop_latch = loops[0]

        pre_path, trans_path, post_path = self._get_paths(function, loop_header, loop_latch)

        loop_state_vars = self._get_loop_state_vars(loop_header)
        
        loop_conditions = self._get_loop_conditions(loop_header)
        guard_conditions = self._get_guard_conditions(loop_state_vars)
        pre_conditions = self._get_pre_conditions(pre_path)
        trans_unchaged_state_conditions = self._get_trans_unchaged_state_conditions(loop_state_vars)
        trans_execution_conditions = self._get_trans_execution_conditions(loop_state_vars, loop_conditions, trans_path)
        post_conditions = self._get_post_conditions(post_path)

        base_vars, state_vars = self._get_declarations_vars(function, contract)
        
        with open(os.path.join(os.path.dirname(__file__), 'templates/vc.tpl')) as tpl_file:
            tpl_data = tpl_file.read()

        base_parameters_def = ' '.join([f'({var[0]} {var[1]})' for var in base_vars])
        state_parameters_def = ' '.join([f'({var[0]} {var[1]})' for var in state_vars])
        base_parameters = ' '.join([var[0] for var in base_vars])
        state_parameters = ' '.join([var[0] for var in state_vars])

        template = Template(tpl_data)
        pre_vc = template.render(
            base_vars=base_vars,
            state_vars=state_vars,
            base_parameters_def=base_parameters_def,
            state_parameters_def=state_parameters_def,
            base_parameters=base_parameters,
            state_parameters=state_parameters,
            inv=inv,
            pre_conditions=pre_conditions,
        )
        trans_vc = template.render(
            base_vars=base_vars,
            state_vars=state_vars,
            base_parameters_def=base_parameters_def,
            state_parameters_def=state_parameters_def,
            base_parameters=base_parameters,
            state_parameters=state_parameters,
            inv=inv,
            trans_unchaged_state_conditions=trans_unchaged_state_conditions,
            trans_execution_conditions=trans_execution_conditions,
        )
        post_vc = template.render(
            base_vars=base_vars,
            state_vars=state_vars,
            base_parameters_def=base_parameters_def,
            state_parameters_def=state_parameters_def,
            base_parameters=base_parameters,
            state_parameters=state_parameters,
            inv=inv,
            loop_conditions=loop_conditions,
            guard_conditions=guard_conditions,
            post_conditions=post_conditions,
        )

        return pre_vc, trans_vc, post_vc

    def _get_post_conditions(self, post_path: list[Node]):
        solidity_call_param = None
        for node in post_path[1:]:
            for ir in node.irs_ssa:
                if isinstance(ir, SolidityCall):
                    solidity_call_param = ir.arguments[0]
        
        conditions = []
        for node in post_path[1:]:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue == solidity_call_param:
                    conditions.append(self._op_to_smt(ir))
                    continue
                if isinstance(ir, OperationWithLValue) and not isinstance(ir, SolidityCall):
                    conditions.append(self._lvalue_op_to_smt(ir))
                    continue

        return conditions

    def _get_trans_unchaged_state_conditions(self, loop_state_vars: list[tuple[Variable, Variable]]) -> list[str]:
        conditions = []
        for curr_var, _ in loop_state_vars:
            conditions.append(f'( = {curr_var} {self._get_base_name(curr_var)} )')
            conditions.append(f'( = {curr_var} {self._get_base_name(curr_var)}! )')
        return conditions

    def _get_loop_conditions(self, loop_header: Node) -> list[str]:
        conditions_irs = []
        for ir in loop_header.irs_ssa:
            if not isinstance(ir, Phi) and isinstance(ir, OperationWithLValue) and ir.lvalue:
                conditions_irs.append(ir)

        conditions = []
        for ir in conditions_irs[:-1]:
            conditions.append(self._lvalue_op_to_smt(ir))
        last_condition_ir = conditions_irs[-1]
        conditions.append(self._op_to_smt(last_condition_ir))

        return conditions

    def _get_guard_conditions(self, loop_state_vars: list[tuple[Variable, Variable]]) -> list[str]:
        conditions = []
        for curr_var, _ in loop_state_vars:
            conditions.append(f'( = {curr_var} {self._get_base_name(curr_var)} )')
        return conditions
    
    def _get_trans_execution_conditions(self, loop_state_vars: list[tuple[Variable, Variable]], loop_conditions: list[str], trans_path: list[Node]) -> list[str]:
        conditions = self._get_guard_conditions(loop_state_vars)
        conditions.extend(loop_conditions)

        for node in trans_path[1:]:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue:
                    conditions.append(self._lvalue_op_to_smt(ir))

        for _, intermediate_var in loop_state_vars:
            conditions.append(f'( = {intermediate_var} {self._get_base_name(intermediate_var)}! )')
        
        return conditions

    def _get_pre_conditions(self, pre_path: list[Node]) -> list[str]:
        guards = set()
        pre_conditions = []
        for node in pre_path:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue:
                    guards.add(f'( = {ir.lvalue} {self._get_base_name(ir.lvalue)} )')
                    pre_conditions.append(self._lvalue_op_to_smt(ir)) 
        
        pre_conditions = list(guards) + pre_conditions 

        return pre_conditions

    def _lvalue_op_to_smt(self, ir: OperationWithLValue) -> str:
        return f'( = {ir.lvalue} {self._op_to_smt(ir)} )'

    def _op_to_smt(self, ir) -> str:
        if isinstance(ir, Binary):
            return f'( {self.op_map[ir.type]} {ir.read[0]} {ir.read[1]} )'
        if isinstance(ir, Unary):
            return f'( {self.op_map[ir.type]} {ir.read[0]} )'
        return f'{ir.read[0]}'

    def _get_base_name(self, var: Variable) -> str:
        return str(var).split('_')[0]


    def _get_declarations_vars(self, function: Function, contract: Contract) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        state_vars = [(var[0], self._type_map[var[1]]) for var in self._get_lvalue_ops_vars(function.nodes)]
        base_vars = [(str(var), self._type_map[str(var.type)]) for var in chain(function.variables, contract.variables)]

        return base_vars, state_vars

    def _get_lvalue_ops_vars(self, nodes: list[Node]) -> list[tuple[str, str]]:
        vars = set()
        for node in nodes:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and isinstance(ir, Variable) and not isinstance(ir.lvalue, Constant) and ir.lvalue:
                    vars.add((str(ir.lvalue), str(ir.type)))
                if hasattr(ir, 'read') and ir.read:
                    for var in ir.read:
                        if not isinstance(var, Constant):
                            vars.add((str(var), str(var.type)))
        return sorted(list(vars))
        
    def _get_loop_state_vars(self, loop_header: Node) -> list[tuple[Variable, Variable]]:
        state_vars = []
        for ir in loop_header.irs_ssa:
            if isinstance(ir, Phi):
                state_vars.append((ir.lvalue, ir.read[-1]))
        return state_vars

    def _get_loop_nodes(self, function: Function) -> list[tuple[Node, Node]]:
        # For every edge (v -> u) in the CFG, if u dominates v, then (v -> u) is a back edge, and u is a loop header
        loops = []
        for v in function.nodes:
            for u in v.sons:
                if u in v.dominators:
                    loops.append((u, v))
        return loops

    def _get_paths(self, function: Function, loop_header: Node, loop_latch: Node) -> tuple[list[Node], list[Node], list[Node]]:
        # The pre-path consists of all nodes that dominates the loop header
        pre_path = set()
        curr = loop_header
        while hasattr(curr, "immediate_dominator") and curr.immediate_dominator is not None:
            curr = curr.immediate_dominator
            pre_path.add(curr)
        pre_path = sorted(list(pre_path), key=lambda n: n.node_id)

        # Get all nodes in the loop body using backward traversal
        trans_path = set()
        stack = [loop_latch]
        while stack:
            node = stack.pop()
            if node in trans_path or node in pre_path:
                continue
            trans_path.add(node)
            if node == loop_header:
                continue
            stack.extend(node.fathers)

        # The post-path is everything else
        post_path = {n for n in function.nodes if n not in pre_path and n not in trans_path}
        
        pre_path = sorted(list(pre_path), key=lambda n: n.node_id)
        trans_path = sorted(list(trans_path), key=lambda n: n.node_id)
        post_path = sorted(list(post_path), key=lambda n: n.node_id)

        return pre_path, trans_path, post_path

class ContractNotFound(Exception):
    def __init__(self):
        super().__init__(f'No contract found')
    
class FunctionNotFound(Exception):
    def __init__(self):
        super().__init__(f'No function found')

class LoopNotFound(Exception):
    def __init__(self):
        super().__init__(f'No loop found')

if __name__ == '__main__':
    test_file_name = "test.sol"
    
    generator = SolidityGenerator(test_file_name)
    pre_vc, trans_vc, post_vc = generator.generate('test')

    print(pre_vc)
    print(trans_vc)
    print(post_vc)
