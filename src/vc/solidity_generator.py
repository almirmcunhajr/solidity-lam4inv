import os
from itertools import chain

from slither.core.solidity_types.elementary_type import Int, Uint
from slither.slither import Slither
from slither.core.declarations import Contract, Function
from slither.core.cfg.node import Constant, Node, NodeType, Phi, TemporaryVariable, Variable
from slither.core.dominators.utils import compute_dominators
from slither.slithir.convert import Unary
from slither.slithir.variables.variable import Variable
from slither.slithir.operations import Assignment, Binary, BinaryType, OperationWithLValue, UnaryType, SolidityCall

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

        tmp_irs = self._get_tmp_irs(function) 
        pre_path, trans_path, post_path = self._get_paths(function, loop_header, loop_latch)

        loop_smt_condition = self._conditional_node_to_smt(loop_header, tmp_irs)
        smt_pre_conditions = self._get_smt_pre_conditions(pre_path, tmp_irs)
        trans_execution_smt_conditions = self._get_trans_execution_smt_conditions(loop_smt_condition, trans_path, tmp_irs)
        smt_post_conditions = self._get_smt_post_conditions(post_path, tmp_irs)

        base_vars, state_vars = self._get_declarations_vars(function, contract)
        
        with open(os.path.join(os.path.dirname(__file__), 'templates/vc.tpl')) as tpl_file:
            tpl_data = tpl_file.read()

        template = Template(tpl_data)
        pre_vc = template.render(
            base_vars=base_vars,
            state_vars=state_vars,
            inv=inv,
            pre_conditions=smt_pre_conditions,
        )
        trans_vc = template.render(
            base_vars=base_vars,
            state_vars=state_vars,
            inv=inv,
            trans_execution_conditions=trans_execution_smt_conditions,
        )
        post_vc = template.render(
            base_vars=base_vars,
            state_vars=state_vars,
            inv=inv,
            loop_condition=loop_smt_condition,
            post_conditions=smt_post_conditions,
        )

        return pre_vc, trans_vc, post_vc

    def _get_tmp_irs(self, function) -> dict[str, OperationWithLValue]:
        tmp_irs = {}
        for node in function.nodes:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue and isinstance(ir.lvalue, TemporaryVariable):
                    tmp_irs[str(ir.lvalue)] = ir
        return tmp_irs

    def _is_tmp_assignment(self, ir: OperationWithLValue) -> bool:
        if ir.lvalue is None:
            return False
        return isinstance(ir.lvalue, TemporaryVariable)

    def _get_smt_post_conditions(self, post_path: list[Node], tmp_irs: dict[str, OperationWithLValue]):
        solidity_call_param = None
        for node in post_path[1:]:
            for ir in node.irs_ssa:
                if isinstance(ir, SolidityCall):
                    solidity_call_param = ir.arguments[0]
        
        conditions = []
        for node in post_path[1:]:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue == solidity_call_param:
                    conditions.append(self._op_to_smt(ir, tmp_irs))
                    continue
                if isinstance(ir, OperationWithLValue) and not isinstance(ir, SolidityCall) and not self._is_tmp_assignment(ir):
                    conditions.append(self._lvalue_op_to_smt(ir, tmp_irs))
                    continue

        return conditions

    def _conditional_node_to_smt(self, node: Node, tmp_irs: dict[str, OperationWithLValue]) -> str:
        if not node.is_conditional():
            raise Exception(f'Node is not conditional {node}')

        conditions_irs = []
        for ir in node.irs_ssa:
            if not isinstance(ir, Phi) and isinstance(ir, OperationWithLValue) and ir.lvalue:
                conditions_irs.append(ir)

        return self._op_to_smt(conditions_irs[-1], tmp_irs)

    def _get_execution_smt_conditions(self, node: Node, tmp_irs: dict[str, OperationWithLValue], execution_smt_conditions: list[list[str]] = [[]]) -> list[list[str]]:
        if not node.is_conditional():
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue and not self._is_tmp_assignment(ir) and not isinstance(ir, Phi):
                    execution_smt_conditions[-1].append(self._lvalue_op_to_smt(ir, tmp_irs))
            if node.sons[0] not in node.dominators:
                return self._get_execution_smt_conditions(node.sons[0], tmp_irs, execution_smt_conditions)
            return execution_smt_conditions
        
        conditions = execution_smt_conditions[-1].copy()
        if node.son_true:
            execution_smt_conditions[-1].append(self._conditional_node_to_smt(node, tmp_irs))
            self._get_execution_smt_conditions(node.son_true, tmp_irs, execution_smt_conditions)
        if node.son_false:
            execution_smt_conditions.append(conditions)
            execution_smt_conditions[-1].append(f'( not {self._conditional_node_to_smt(node, tmp_irs)} )')
            self._get_execution_smt_conditions(node.son_false, tmp_irs, execution_smt_conditions)

        return execution_smt_conditions

    def _get_trans_execution_smt_conditions(self, loop_smt_condition: str, trans_path: list[Node], tmp_irs: dict[str, OperationWithLValue]) -> list[list[str]]:
        execution_smt_conditions = self._get_execution_smt_conditions(trans_path[1], tmp_irs)
        for conditions in execution_smt_conditions:
            conditions.insert(0, loop_smt_condition)

        return execution_smt_conditions

    def _get_smt_pre_conditions(self, pre_path: list[Node], tmp_irs: dict[str, OperationWithLValue]) -> list[str]:
        guards = set()
        pre_conditions = []
        for node in pre_path:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue and not isinstance(ir, Phi):
                    guards.add(f'( = {ir.lvalue} {self._get_base_name(ir.lvalue)} )')
                    pre_conditions.append(self._lvalue_op_to_smt(ir, tmp_irs)) 
        
        pre_conditions = list(guards) + pre_conditions 

        return pre_conditions

    def _lvalue_op_to_smt(self, ir: OperationWithLValue, tmp_irs: dict[str, OperationWithLValue]) -> str:
        return f'( = {ir.lvalue} {self._op_to_smt(ir, tmp_irs)} )'

    def _op_to_smt(self, ir: OperationWithLValue, tmp_irs: dict[str, OperationWithLValue]) -> str:
        if isinstance(ir, Binary):
            reads = [str(ir.read[0]), str(ir.read[1])]
            if isinstance(ir.read[0], TemporaryVariable):
                reads[0] = self._op_to_smt(tmp_irs[str(ir.read[0])], tmp_irs)
            if isinstance(ir.read[1], TemporaryVariable):
                reads[1] = self._op_to_smt(tmp_irs[str(ir.read[1])], tmp_irs)
            return f'( {self.op_map[ir.type]} {reads[0]} {reads[1]} )'
        if isinstance(ir, Unary):
            read = ir.read[0]
            if isinstance(ir.read[0], TemporaryVariable):
                read = self._op_to_smt(tmp_irs[str(ir.read[0])], tmp_irs)
            return f'( {self.op_map[ir.type]} {read} )'
        if isinstance(ir, Assignment):
            if isinstance(ir.read[0], TemporaryVariable):
                return self._op_to_smt(tmp_irs[str(ir.read[0])], tmp_irs)
            return ir.read[0]

        raise Exception(f'Invalid operation {ir}')

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
                    if not isinstance(ir.lvalue, TemporaryVariable):
                        vars.add((str(ir.lvalue), str(ir.lvalue.type)))
                if hasattr(ir, 'read') and ir.read:
                    for var in ir.read:
                        if not isinstance(var, Constant) and not isinstance(var, TemporaryVariable):
                            vars.add((str(var), str(var.type)))
        return sorted(list(vars))

    def _get_loop_state_vars(self, loop_header: Node) -> list[tuple[Variable, Variable]]:
        state_vars = []
        for ir in loop_header.irs_ssa:
            if isinstance(ir, Phi):
                state_vars.append((ir.lvalue, max(ir.read, key=lambda v: str(v))))
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
