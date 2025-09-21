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

    def __init__(self, file_path: str):
        self.slither = Slither(file_path, disable_plugins=["solc-ast-exporter"])
        
        self._type_map = {
            "bool": "Bool"
        }
        for t in Int+Uint:
            self._type_map[t] = "Int"

    def generate(self, inv: str) -> tuple[str, str, str]:
        """Generates the SMT-LIB2 verification conditions to verify a loop invariant

        Args:
            inv (str): The loop invariant in SMT-LIB2 format
        Raises:
            ContractNotFound: If no contract is found in the Solidity file
            FunctionNotFound: If no function is found in the contract
            LoopNotFound: If no loop is found in the function
        Returns:
            tuple[str, str, str]: The pre-condition, transition, and post-condition verification conditions in SMT-LIB2 format
        """

        if len(self.slither.contracts) == 0:
            raise ContractNotFound()
        contract = self.slither.contracts[0]

        if len(contract.functions) == 0:
            raise FunctionNotFound()
        function = contract.functions[0]

        compute_dominators(function.nodes)

        # Get the first loop header and latch
        loops = self._get_loop_nodes(function)
        if len(loops) == 0:
            raise LoopNotFound()
        loop_header, loop_latch = loops[0]

        # Get all state variables and base variables in the function and contract
        base_vars, state_vars = self._get_declarations_vars(function, contract)

        # Get all temporary IR operations in the function
        tmp_irs = self._get_tmp_irs(function) 

        # Get the execution paths
        pre_path, trans_path, post_path = self._get_paths(function, loop_header, loop_latch)

        # Get the loop condition in SMT-LIB2 format
        loop_smt_condition = self._conditional_node_to_smt(loop_header, tmp_irs)

        # Get the pre-condition in SMT-LIB2 format
        smt_pre_conditions = self._get_smt_pre_conditions(pre_path, tmp_irs)

        # Get the transition execution conditions in SMT-LIB2 format
        trans_execution_smt_conditions = self._get_trans_execution_smt_conditions(base_vars, loop_smt_condition, trans_path, tmp_irs)

        smt_post_conditions = self._get_smt_post_conditions(post_path, tmp_irs)

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
        """Returns a mapping of temporary variable names to their corresponding IR operations in the functions

        Args:
            function (Function): The function to analyze

        Returns:
            dict[str, OperationWithLValue]: A dictionary mapping temporary variable names to their corresponding IR operations
        """

        tmp_irs = {}
        for node in function.nodes:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue and isinstance(ir.lvalue, TemporaryVariable):
                    tmp_irs[str(ir.lvalue)] = ir
        return tmp_irs

    def _is_tmp_assignment(self, ir: OperationWithLValue) -> bool:
        """ Checks if the given IR operation is an assignment to a temporary variable

        Args:
            ir (OperationWithLValue): The IR operation to checks

        Returns:
            bool: True if the operation is an assignment to a temporary variable, False otherwise
        """

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
        """ Converts the condition of a conditional node to SMT-LIB2 format

        Args:
            node (Node): The conditional node to convert
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations
            
        Raises:
            Exception: If the node is not conditional

        Returns:
            str: The condition in SMT-LIB2 format
        """

        if not node.is_conditional():
            raise Exception(f'Node is not conditional {node}')

        conditions_irs = []
        for ir in node.irs_ssa:
            if not isinstance(ir, Phi) and isinstance(ir, OperationWithLValue) and ir.lvalue:
                conditions_irs.append(ir)

        return self._op_to_smt(conditions_irs[-1], tmp_irs)

    def _update_var_ssa_bounds(self, var_ssa_bounds: dict[str, tuple[str, str]], ir: OperationWithLValue, tmp_irs: dict[str, OperationWithLValue]):
        """ Updates the SSA bounds for the variables involved in the given IR operations

        Args:
            var_ssa_bounds (dict[str, tuple[str, str]]): a mapping of variable base names to their SSA bounds
            ir (OperationWithLValue): The IR operation to analyze

        Raises:
            Exception: If the operation is invalid
        """

        def get_read_vars(ir: OperationWithLValue, vars: list[Variable]):
            if not ir.read:
                return
            for var in ir.read:
                if  not isinstance(var, TemporaryVariable) and not isinstance(var, Constant):
                    vars.append(var)
                    continue
                if isinstance(var, TemporaryVariable):
                    get_read_vars(tmp_irs[str(var)], vars)

        if not ir.lvalue or not ir.read:
            raise Exception('Invalid operation {ir}')
        vars = [ir.lvalue]
        get_read_vars(ir, vars)
        print(vars)
        for var in vars:
            var_base_name = self._get_base_name(var)
            if var_base_name not in var_ssa_bounds:
                var_ssa_bounds[var_base_name] = (str(var), str(var))
                continue
            if var_ssa_bounds[var_base_name][0] > str(var):
                var_ssa_bounds[var_base_name] = (str(var), var_ssa_bounds[var_base_name][1])
            if var_ssa_bounds[var_base_name][1] < str(var):
                var_ssa_bounds[var_base_name] = (var_ssa_bounds[var_base_name][0], str(var))

    def _add_bounds_checks(self, conditions: list[str], var_ssa_bounds: dict[str, tuple[str, str]]):
        """ Adds bounds checks for all variables in the SSA bounds mapping to the given conditions list

        Args:
            conditions (list[str]): The list of conditions to update
            var_ssa_bounds (dict[str, tuple[str, str]]): a mapping of variable base names to their SSA bounds
        """
        
        for var, bounds in var_ssa_bounds.items():
            conditions.append(f'(= {bounds[0]} {var} )')
            conditions.append(f'(= {bounds[1]} {var}! )')

    def _get_execution_smt_conditions(self, node: Node, tmp_irs: dict[str, OperationWithLValue], var_ssa_bounds: dict[str, tuple[str, str]], execution_smt_conditions: list[list[str]] = [[]]) -> list[list[str]]:
        """ Recursively generates SMT-LIB2 execution conditions from the given node

        Args:
            node (Node): The current node to process
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations
            var_ssa_bounds (dict[str, tuple[str, str]]): A mapping of variable base names to their SSA bounds
            execution_smt_conditions (list[list[str]], optional): The list of execution conditions being built. Defaults to [[]].

        Returns:
            list[list[str]]: A list of execution conditions in SMT-LIB2 format
        """
        if not node.is_conditional():
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue and not self._is_tmp_assignment(ir) and not isinstance(ir, Phi):
                    # Update the SSA bounds for the variables involved in the operation
                    self._update_var_ssa_bounds(var_ssa_bounds, ir, tmp_irs)
                    # Add the operation to the current execution condition
                    execution_smt_conditions[-1].append(self._lvalue_op_to_smt(ir, tmp_irs))

            # Continue to the next node if it does not dominate the current node (to avoid cycles)
            if len(node.sons) > 0 and node.sons[0] not in node.dominators:
                return self._get_execution_smt_conditions(node.sons[0], tmp_irs, var_ssa_bounds, execution_smt_conditions)

            # If the node is a leaf, add bounds checks and return
            self._add_bounds_checks(execution_smt_conditions[-1], var_ssa_bounds)
            return execution_smt_conditions
        
        # If the node is conditional, create two branches
        conditions = execution_smt_conditions[-1].copy()
        if node.son_true:
            execution_smt_conditions[-1].append(self._conditional_node_to_smt(node, tmp_irs))
            self._get_execution_smt_conditions(node.son_true, tmp_irs, var_ssa_bounds.copy(), execution_smt_conditions)
        if node.son_false:
            execution_smt_conditions.append(conditions)
            execution_smt_conditions[-1].append(f'( not {self._conditional_node_to_smt(node, tmp_irs)} )')
            self._get_execution_smt_conditions(node.son_false, tmp_irs, var_ssa_bounds.copy(), execution_smt_conditions)

        return execution_smt_conditions

    def _get_trans_execution_smt_conditions(self, base_declarations: list[tuple[str, str]], loop_smt_condition: str, trans_path: list[Node], tmp_irs: dict[str, OperationWithLValue]) -> list[list[str]]:
        """ Generates SMT-LIB2 execution conditions for the transition path

        Args:
            base_declarations (list[tuple[str, str]]): A list of tuples where each tuple contains the base variable name and type
            loop_smt_condition (str): The loop condition in SMT-LIB2 format
            trans_path (list[Node]): The list of nodes in the transition path
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations

        Returns:
            list[list[str]]: A list of execution conditions in SMT-LIB2 format
        """

        var_ssa_bounds: dict[str, tuple[str, str]] = {}
        execution_smt_conditions = self._get_execution_smt_conditions(trans_path[1], tmp_irs, var_ssa_bounds)

        # Add the loop condition to the beginning of each execution condition
        for conditions in execution_smt_conditions:
            conditions.insert(0, loop_smt_condition)
        
        # Add the execution condition that represents the case where the loop body is not executed
        execution_smt_conditions.append([])
        for var in var_ssa_bounds:
            execution_smt_conditions[-1].append(f'( = {var_ssa_bounds[var][0]} {var} )')
            execution_smt_conditions[-1].append(f'( = {var_ssa_bounds[var][0]} {var}! )')

        return execution_smt_conditions

    def _get_smt_pre_conditions(self, pre_path: list[Node], tmp_irs: dict[str, OperationWithLValue]) -> list[str]:
        """Generates SMT-LIB2 pre-conditions from the pre-path nodes

        The pre-conditions formula is constructed by:
        1. Adding guards that equate each state variable to its corresponding base variable
        2. Adding conditions for each IR operation with an LValue in the pre-path nodes

        Args:
            pre_path (list[Node]): The list of nodes in the pre-path
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations

        Returns:
            list[str]: A list of pre-conditions in SMT-LIB2 format
        """

        guards = set()
        pre_conditions = []
        for node in pre_path:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue and not isinstance(ir, Phi):
                    # The guard transports the value of the base variable to the state variable
                    guards.add(f'( = {ir.lvalue} {self._get_base_name(ir.lvalue)} )')

                    pre_conditions.append(self._lvalue_op_to_smt(ir, tmp_irs)) 
        
        pre_conditions = list(guards) + pre_conditions 

        return pre_conditions

    def _lvalue_op_to_smt(self, ir: OperationWithLValue, tmp_irs: dict[str, OperationWithLValue]) -> str:
        """ Converts an IR operation with an LValue to SMT-LIB2 format

        Args:
            ir (OperationWithLValue): The IR operation to convert
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations

        Raises:
            Exception: If the operation is invalid or unsupported

        Returns:
            str: The operation in SMT-LIB2 format

        """

        return f'( = {ir.lvalue} {self._op_to_smt(ir, tmp_irs)} )'

    def _op_to_smt(self, ir: OperationWithLValue, tmp_irs: dict[str, OperationWithLValue]) -> str:
        """ Converts an IR operation to SMT-LIB2 format

        Args:
            ir (OperationWithLValue): The IR operation to convert
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations

        Raises:
            Exception: If the operation is invalid or unsupported

        Returns:
            str: The operation in SMT-LIB2 format
        """

        if isinstance(ir, Binary):
            reads = [str(ir.read[0]), str(ir.read[1])]
            
            # If one of the reads is a temporary variable, recursively resolve it
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
        """ Returns the base name of a variable by removing its SSA suffix

        Args:
            var (Variable): The variable to process

        Returns:
            str: The base name of the variable
        """

        return str(var).split('_')[0]

    def _get_declarations_vars(self, function: Function, contract: Contract) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        """Finds all state variables (SSA) and base variables (non-SSA) in the function and contract

        Args:
            function (Function): The function to analyze
            contract (Contract): The contract to analyze

        Returns:
            tuple[list[tuple[str, str]], list[tuple[str, str]]]: A tuple containing two lists:
                - The first list contains tuples of base variable names and types
                - The second list contains tuples of state variable names and types
        """

        state_vars = [(var[0], self._type_map[var[1]]) for var in self._get_lvalue_ops_vars(function.nodes)]
        base_vars = [(str(var), self._type_map[str(var.type)]) for var in chain(function.variables, contract.variables)]

        return base_vars, state_vars

    def _get_lvalue_ops_vars(self, nodes: list[Node]) -> list[tuple[str, str]]:
        """Finds all SSA variables that are assigned a value or read in the given nodes

        Args:
            nodes (list[Node]): The list of nodes to analyze

        Returns:
            list[tuple[str, str]]: A list of tuples where each tuple contains the variable name and type
        """

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

    def _get_loop_nodes(self, function: Function) -> list[tuple[Node, Node]]:
        """Finds all loops in the function
        
        Identifies loops by looking for back edges in the control flow graph (CFG) of the function. For every edge (v -> u) in the CFG, if u dominates v, then (v -> u) is a back edge, and u is a loop header.

        Args:
            function (Function): The function to analyze

        Returns:
            list[tuple[Node, Node]]: A list of tuples where each tuple contains the loop header and loop latch nodes
        """

        loops = []
        for v in function.nodes:
            for u in v.sons:
                if u in v.dominators:
                    loops.append((u, v))
        return loops

    def _get_paths(self, function: Function, loop_header: Node, loop_latch: Node) -> tuple[list[Node], list[Node], list[Node]]:
        """Divides the function's nodes into three paths: pre-path, transition path, and post-path

        Retrieves the nodes in the pre-path (nodes that dominate the loop header), transition path (nodes in the loop body), and post-path (all other nodes).

        Args:
            function (Function): The function to analyze
            loop_header (Node): The loop header node
            loop_latch (Node): The loop latch node

        Returns:
            tuple[list[Node], list[Node], list[Node]]: A tuple containing three lists:
                - The first list contains the nodes in the pre-path
                - The second list contains the nodes in the transition path
                - The third list contains the nodes in the post-path
        """

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
