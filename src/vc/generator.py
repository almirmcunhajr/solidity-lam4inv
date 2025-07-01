from typing import Optional
import textwrap
from itertools import chain
from slither.slither import Slither
from slither.core.declarations import Contract, Function
from slither.core.cfg.node import Constant, Node, Variable
from slither.core.dominators.utils import compute_dominators
from slither.slithir.convert import Unary
from slither.slithir.variables.variable import Variable
from slither.slithir.operations import (
    Assignment,
    Binary,
    BinaryType,
    OperationWithLValue,
    UnaryType,
    Phi,
    lvalue,
)
from slither.slithir.operations.operation import Operation
from utils.slither import preorder_traversal

class Generator:
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

    def __init__(self, file_path: str):
        self.slither = Slither(file_path, disable_plugins=["solc-ast-exporter"])

    def _get_contract(self, contract_name: str) -> Optional[Contract]:
        for contract in self.slither.contracts:
            if contract.name == contract_name:
                return contract

    def generate(self, contract_name: str, function_name: str, loop_index: int, inv: str) -> tuple[str, str, str]:
        contract = self._get_contract(contract_name)
        if contract is None:
            raise ContractNotFound(contract_name)

        function = contract.get_function_from_full_name(function_name)
        if function is None:
            raise FunctionNotFound(function_name)

        loops = self._get_loop_nodes(function)
        if loop_index not in range(len(loops)):
            raise LoopNotFound(loop_index)
        cond_node, end_node = loops[loop_index]

        pre_path, trans_path, post_path = self._get_paths(function, cond_node, end_node)

        ssa_vars = self._get_ssa_vars(function)
        loop_vars, entry_ssa_map, exit_ssa_map = self._get_loop_ssa_maps(trans_path, function, contract)

        smt_declarations = self._declare_smt_variables(ssa_vars)
        smt_inv_fun_definition = self._define_smt_inv_fun(loop_vars, inv)
        smt_pre_fun_definition = self._define_smt_semantic_fun('pre-f', pre_path)
        smt_trans_fun_definition = self._define_smt_semantic_fun('trans-f', trans_path)
        smt_post_fun_definition = self._define_smt_semantic_fun('post-f', post_path)

        entry_args = ' '.join(entry_ssa_map[v] for v in loop_vars)
        exit_args = ' '.join(exit_ssa_map[v] for v in loop_vars)

        pre_assert = f'(assert (=> (pre-f) (inv-f {entry_args})))'
        trans_assert = f'(assert (=> (and (inv-f {entry_args}) (trans-f)) (inv-f {exit_args})))'
        post_assert = f'(assert (=> (inv-f {exit_args}) (post-f)))'

        vc_base = [smt_declarations, smt_inv_fun_definition]
        pre_vc = '\n'.join(vc_base + [smt_pre_fun_definition, pre_assert])
        trans_vc = '\n'.join(vc_base + [smt_trans_fun_definition, trans_assert])
        post_vc = '\n'.join(vc_base + [smt_post_fun_definition, post_assert])

        return pre_vc, trans_vc, post_vc

    def _get_loop_nodes(self, function: Function) -> list[tuple[Node, Node]]:
        loops = []
        compute_dominators(function.nodes)
        for v in function.nodes:
            for u in v.sons:
                if u in v.dominators:
                    loops.append((u, v))
        return loops

    def _get_paths(self, function: Function, loop_cond_node: Node, loop_end_node: Node) -> tuple[list[Node], list[Node], list[Node]]:
        # The pre-path consists of all nodes that dominates the loop header
        pre_path = set()
        curr = loop_cond_node
        while hasattr(curr, "immediate_dominator") and curr.immediate_dominator is not None:
            curr = curr.immediate_dominator
            pre_path.add(curr)
        pre_path = sorted(list(pre_path), key=lambda n: n.node_id)

        # Get all nodes in the loop body using backward traversal
        trans_path = set(preorder_traversal(loop_end_node, backward=True))

        # The post-path is everything else
        post_path = {n for n in function.nodes if n not in pre_path and n not in trans_path}
        
        pre_path = sorted(list(pre_path), key=lambda n: n.node_id)
        trans_path = sorted(list(trans_path), key=lambda n: n.node_id)
        post_path = sorted(list(post_path), key=lambda n: n.node_id)

        return pre_path, trans_path, post_path

    def _get_ssa_vars(self, function: Function):
        ssa_vars = set()
        for node in function.nodes:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue and not isinstance(ir.lvalue, Constant):
                    ssa_vars.add(self._var_to_smt(ir.lvalue))
                if hasattr(ir, 'read') and ir.read:
                    for var in ir.read:
                        if not isinstance(var, Constant):
                            ssa_vars.add(self._var_to_smt(var))
        return sorted(list(ssa_vars))

    def _var_to_smt(self, var: Variable) -> str:
        if isinstance(var, Constant):
            return str(var.value)
        return str(var)

    def _get_loop_ssa_maps(
        self,
        trans_path: list[Node],
        function: Function,
        contract: Contract,
    ) -> tuple[list[str], dict[str, str], dict[str, str]]:
        """Return loop variable names and their entry/exit SSA mappings using Phi nodes."""

        loop_var_names: set[str] = {
            v.name for v in chain(function.parameters, function.returns) if v.name
        }
        loop_var_names.update({v.name for v in contract.state_variables if v.name})

        entry_ssa_map: dict[str, str] = {}
        exit_ssa_map: dict[str, str] = {}

        # Collect all SSA names assigned within the loop body
        assigned_in_loop: set[str] = set()
        for node in trans_path:
            for ir in getattr(node, "irs_ssa", []):
                if isinstance(ir, OperationWithLValue) and ir.lvalue:
                    assigned_in_loop.add(self._var_to_smt(ir.lvalue))

        # Inspect Phi nodes in the function to build the maps
        for node in function.nodes:
            for ir in getattr(node, "irs_ssa", []):
                if isinstance(ir, Phi) and ir.lvalue:
                    base_name = self._get_base_name(ir.lvalue)
                    if not base_name:
                        raise NoneTypeVarName()

                    loop_var_names.add(base_name)

                    reads = list(getattr(ir, "read", []) or [])
                    entry_var = None
                    exit_var = None
                    for var in reads:
                        smt_name = self._var_to_smt(var)
                        if smt_name in assigned_in_loop and exit_var is None:
                            exit_var = smt_name
                        else:
                            entry_var = smt_name

                    # Fallbacks if we failed to classify the reads
                    if entry_var is None and reads:
                        entry_var = self._var_to_smt(reads[0])
                    if exit_var is None and len(reads) > 1:
                        exit_var = self._var_to_smt(reads[-1])
                    if exit_var is None:
                        exit_var = self._var_to_smt(ir.lvalue)

                    entry_ssa_map[base_name] = entry_var if entry_var else self._var_to_smt(ir.lvalue)
                    exit_ssa_map[base_name] = exit_var

        # Ensure all loop variables have a mapping
        for var in loop_var_names:
            entry_ssa_map.setdefault(var, var)
            exit_ssa_map.setdefault(var, var)

        return sorted(list(loop_var_names)), entry_ssa_map, exit_ssa_map

    def _define_smt_semantic_fun(self, name: str, path: list[Node]) -> str:
        smt_exprs = self._path_to_smt_exprs(path)
        body = '\n'.join([e for e in smt_exprs if e])
        return f'''
(define-fun {name} () Bool
 (and
{textwrap.indent(body, '    ')}
 )
)
'''

    def _path_to_smt_exprs(self, path: list[Node]) -> list[str]:
        return [self._ir_to_smt(ir) for node in path for ir in node.irs_ssa]

    def _ir_to_smt(self, ir: Operation) -> str:
        if isinstance(ir, Binary):
            return self._binary_to_smt(ir)
        if isinstance(ir, Unary):
            return self._unary_to_smt(ir)
        if isinstance(ir, Assignment):
            return self._assignment_to_smt(ir)
        return ""

    def _binary_to_smt(self, ir: Binary) -> str:
        if ir.type not in self.op_map:
            raise InvalidOpType()                    
        if not isinstance(ir.variable_left, (Variable, Constant)):
            raise InvalidRvalueType()
        if not isinstance(ir.variable_right, (Variable, Constant)):
            raise InvalidRvalueType()
        op = self.op_map[ir.type]
        left = self._var_to_smt(ir.variable_left)
        right = self._var_to_smt(ir.variable_right)
        if isinstance(ir, OperationWithLValue) and ir.lvalue:
            lvalue = self._var_to_smt(ir.lvalue)
            return f'(= {lvalue} ({op} {left} {right}))'
        return f'({op} {left} {right})'

    def _unary_to_smt(self, ir: Unary) -> str:
        if ir.type not in self.op_map:
            raise InvalidOpType()
        if not isinstance(ir.rvalue, (Variable, Constant)):
            raise InvalidRvalueType()
        op = self.op_map[ir.type]
        rvalue = self._var_to_smt(ir.rvalue)
        if isinstance(ir, OperationWithLValue) and ir.lvalue:
            lvalue = self._var_to_smt(ir.lvalue)
            return f'(= {lvalue} ({op} {rvalue}))'
        return f'({op} {rvalue})'

    def _assignment_to_smt(self, ir: Assignment) -> str:
        if not isinstance(ir.rvalue, (Variable, Constant)):
            raise InvalidRvalueType()
        if not ir.lvalue:
            raise InvalidOpType()
        lvalue = self._var_to_smt(ir.lvalue)
        rvalue = self._var_to_smt(ir.rvalue)
        return f'(= {lvalue} {rvalue})'

    def _get_base_name(self, var: Variable) -> str|None:
        if isinstance(var, Constant):
            return str(var.value)
        if hasattr(var, 'non_ssa_version') and var.non_ssa_version:
            return var.non_ssa_version.name
        if var.name:
            return var.name.split('_ssa')[0]
        return None
    
    def _declare_smt_variables(self, ssa_vars: list[str]) -> str:
        smt = ['(set-logic LIA)']
        for var in ssa_vars:
            smt.append(f'(declare-const {var} Int)')
        return '\n'.join(smt)

    def _define_smt_inv_fun(self, loop_vars: list[str], inv: str) -> str:
        params = ' '.join([f'({var} Int)' for var in loop_vars])
        return f'''
(define-fun inv-f ({params}) Bool
{textwrap.indent(inv, '  ')}
)
'''

class ContractNotFound(Exception):
    def __init__(self, contract_name: str):
        super().__init__(f'Contract "{contract_name}" not found')
    
class FunctionNotFound(Exception):
    def __init__(self, function_name: str):
        super().__init__(f'Function "{function_name}" not found')

class LoopNotFound(Exception):
    def __init__(self, loop_index: int):
        super().__init__(f'Loop {loop_index} not found')

class NoneTypeVarName(Exception):
    def __init__(self, *args: object):
        super().__init__(*args)
   
class InvalidOpType(Exception):
    def __init__(self):
        super().__init__(f'Invalid operation type')

class InvalidRvalueType(Exception):
    def __init__(self) -> None:
        super().__init__('Invalid RVALUE type')
