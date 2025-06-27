from typing import Optional
from slither.slither import Slither
from slither.core.declarations import Contract, Function
from slither.core.source_mapping.source_mapping import SourceMapping
from slither.core.cfg.node import Constant, Node
from slither.core.dominators.utils import compute_dominators
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
        
        ssa_vars = self._get_ssa_vars()

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
                if hasattr(ir, 'lvalue') and ir.lvalue and not isinstance(ir.lvalue, Constant):
                    ssa_vars.add(self._var_to_smt(ir.lvalue))
                for var in ir.read:
                    if not isinstance(var, Constant):
                        ssa_vars.add(self._var_to_smt(var))
        return sorted(list(ssa_vars))

    def _var_to_smt(self, var: SourceMapping) -> str:
        if isinstance(var, Constant):
            return str(var.value)
        return str(var)

class ContractNotFound(Exception):
    def __init__(self, contract_name: str):
        super().__init__(f'Contract "{contract_name}" not found')
    
class FunctionNotFound(Exception):
    def __init__(self, function_name: str):
        super().__init__(f'Function "{function_name}" not found')

class LoopNotFound(Exception):
    def __init__(self, loop_index: int):
        super().__init__(f'Loop {loop_index} not found')

