from typing import Optional
from itertools import chain
from slither.slither import Slither
from slither.core.declarations import Contract, Function
from slither.core.cfg.node import Constant, Node, Variable
from slither.core.dominators.utils import compute_dominators
from slither.slithir.variables.variable import Variable
from slither.slithir.operations import OperationWithLValue
from utils.slither import preorder_traversal

class Generator:
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

        pre_vc = '\n'.join([smt_declarations])
        trans_vc = '\n'.join([smt_declarations])
        post_vc = '\n'.join([smt_declarations])

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

    def _get_loop_ssa_maps(self, trans_path: list[Node], function: Function, contract: Contract) -> tuple[list[str], dict[str,str], dict[str,str]]:
        loop_var_names: set[str] = {v.name for v in chain(function.parameters, function.returns) if v.name}
        loop_var_names.update({v.name for v in contract.state_variables if v.name})
        
        # Iterate in order to find the last assignment to a variable in the loop body and get its final SSA version and the corresponding entry SSA version
        exit_ssa_map: dict[str, str] = {}
        entry_ssa_map: dict[str, str] = {}
        for node in trans_path:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue:
                    base_name = self._get_base_name(ir.lvalue)
                    if not base_name:
                        raise NoneTypeVarName()
                    loop_var_names.add(base_name)
                    exit_ssa_map[base_name] = self._var_to_smt(ir.lvalue)
                    if hasattr(ir, 'read') and ir.read:
                        for var in ir.read:
                            if self._get_base_name(var) == base_name:
                                entry_ssa_map[base_name] = self._var_to_smt(var)
        
        # Handle variable that are only read within the loop body
        unmapped_vars = {v for v in loop_var_names if v not in entry_ssa_map}
        for node in trans_path:
            for ir in node.irs_ssa:
                if hasattr(ir, 'read') and ir.read:
                    for var in ir.read:
                        base_name = self._get_base_name(var)
                        if base_name and base_name in unmapped_vars:
                            smt_ssa_name = self._var_to_smt(var)
                            entry_ssa_map[base_name] = smt_ssa_name
                            exit_ssa_map[base_name] = smt_ssa_name

        return sorted(list(loop_var_names)), entry_ssa_map, exit_ssa_map

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
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
   
