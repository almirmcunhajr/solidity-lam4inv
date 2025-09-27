import os
from itertools import chain

from slither.core.solidity_types.elementary_type import Int, Uint
from slither.slither import Slither
from slither.core.declarations import Contract, Function
from slither.core.cfg.node import Constant, Node, Phi, TemporaryVariable, Variable
from slither.core.dominators.utils import compute_dominators
from slither.slithir.convert import Unary
from slither.slithir.variables.variable import Variable
from slither.slithir.operations import Assignment, Binary, BinaryType, OperationWithLValue, UnaryType, SolidityCall

from jinja2 import Template

from vc.generator import Generator
from vc.smt import *

class SolidityGenerator(Generator):
    op_map = {
        BinaryType.ADDITION: Addition,
        BinaryType.SUBTRACTION: Subtraction,
        BinaryType.MULTIPLICATION: Multiplication,
        BinaryType.DIVISION: Division,
        BinaryType.MODULO: Modulo,
        BinaryType.LESS: Less,
        BinaryType.GREATER: Greater,
        BinaryType.LESS_EQUAL: LessEqual,
        BinaryType.GREATER_EQUAL: GreaterEqual,
        BinaryType.EQUAL: Equal,
        BinaryType.NOT_EQUAL: NotEqual,
        BinaryType.ANDAND: And,
        BinaryType.OROR: Or,
        UnaryType.BANG: Not
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
        loops = self._get_solidity_loop_nodes(function)
        if len(loops) == 0:
            raise LoopNotFound()
        loop_header, loop_latch = loops[0]

        # Get all state variables and base variables in the function and contract
        base_vars, state_vars = self._get_solidity_vars(function, contract)

        # Get all temporary IR operations in the function
        tmp_irs = self._get_solidity_tmp_irs(function) 

        # Get the execution paths
        pre_path, trans_path, post_path = self._get_solidity_paths(function, loop_header, loop_latch)

        # Get the loop condition operation
        loop_condition_op = self._solidity_conditional_node_to_op(loop_header, tmp_irs)

        # Get the reachability verification condition op
        reachability_op = self._get_pre_op(pre_path, tmp_irs)

        # Get the inductive verification condition op
        inductive_op = self._get_trans_op(loop_condition_op, trans_path, tmp_irs)

        # Get the provability verification condition op
        provability_op = self._get_post_op(loop_condition_op, post_path, tmp_irs)

        with open(os.path.join(os.path.dirname(__file__), 'templates/vc.tpl')) as tpl_file:
            tpl_data = tpl_file.read()

        template = Template(tpl_data)
        pre_vc = template.render(
            base_vars=base_vars,
            state_vars=state_vars,
            inv=inv,
            reachability_vc=str(reachability_op),
        )
        trans_vc = template.render(
            base_vars=base_vars,
            state_vars=state_vars,
            inv=inv,
            inductive_vc=str(inductive_op),
        )
        post_vc = template.render(
            base_vars=base_vars,
            state_vars=state_vars,
            inv=inv,
            provability_vc=str(provability_op),
        )

        return pre_vc, trans_vc, post_vc

    def _get_solidity_tmp_irs(self, function) -> dict[str, OperationWithLValue]:
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

    def _is_solidity_tmp_assignment(self, ir: OperationWithLValue) -> bool:
        """ Checks if the given IR operation is an assignment to a temporary variable

        Args:
            ir (OperationWithLValue): The IR operation to checks

        Returns:
            bool: True if the operation is an assignment to a temporary variable, False otherwise
        """

        if ir.lvalue is None:
            return False
        return isinstance(ir.lvalue, TemporaryVariable)

    def _get_post_op(self, loop_condition_op: Op|str, post_path: list[Node], tmp_irs: dict[str, OperationWithLValue]) -> Or:
        """ Generate the operation to check loop invariant post condition

        This assumes that the post loop path contains only if statements and a single assert call.

        Args:
            loop_condition_op (str): The loop condition operation
            post_path (list[Node]): The list of nodes in the post loop path
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations

        Returns:
            Op: An Op object to check the loop invariant post condition
        """

        assertion_op = And(Not(loop_condition_op))
        root_op = Or(Not(assertion_op))
        for node in post_path[1:]:
            if node.contains_if():
                assertion_op.append(self._solidity_conditional_node_to_op(node, tmp_irs))
                continue
            for ir in node.irs_ssa:
                if  isinstance(ir, SolidityCall) and ir.function.name == "assert(bool)":
                    post_condition_ir = tmp_irs[str(ir.arguments[0])]
                    assertion_op.append(Not(self._solidity_op_to_op(post_condition_ir, tmp_irs)))
                    break

        return root_op

    def _solidity_conditional_node_to_op(self, node: Node, tmp_irs: dict[str, OperationWithLValue]) -> Op|str:
        """ Converts a Solidity conditional node to an operation

        Args:
            node (Node): The conditional node to convert
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations
        Raises:
            Exception: If the node is not conditional

        Returns:
            Op|str: The operation representing the condition of the node
        """

        if not node.is_conditional():
            raise Exception(f'Node is not conditional {node}')

        conditions_irs = []
        for ir in node.irs_ssa:
            if not isinstance(ir, Phi) and isinstance(ir, OperationWithLValue) and ir.lvalue:
                conditions_irs.append(ir)

        return self._solidity_op_to_op(conditions_irs[-1], tmp_irs)

    def get_read_vars(self, ir: OperationWithLValue, vars: list[Variable], tmp_irs: dict[str, OperationWithLValue]):
        """ Recursively retrieves all variables read by the given IR operation, including those read by temporary variables
        Args:
            ir (OperationWithLValue): The IR operation to analyze
            vars (list[Variable]): The list to populate with read variables
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations
        """

        if not ir.read:
            return
        for var in ir.read:
            if  not isinstance(var, TemporaryVariable) and not isinstance(var, Constant):
                vars.append(var)
                continue
            if isinstance(var, TemporaryVariable):
                self.get_read_vars(tmp_irs[str(var)], vars, tmp_irs)

    def _update_var_ssa_bounds(self, var_ssa_bounds: dict[str, tuple[str, str]], ir: OperationWithLValue, tmp_irs: dict[str, OperationWithLValue]):
        """ Updates the SSA bounds for the variables involved in the given IR operations

        Args:
            var_ssa_bounds (dict[str, tuple[str, str]]): a mapping of variable base names to their SSA bounds
            ir (OperationWithLValue): The IR operation to analyze

        Raises:
            Exception: If the operation is invalid
        """
        
        if not ir.lvalue or not ir.read:
            raise Exception('Invalid operation {ir}')
        vars = [ir.lvalue]
        self.get_read_vars(ir, vars, tmp_irs)
        for var in vars:
            var_base_name = self._get_solidity_var_base_name(var)
            if var_base_name not in var_ssa_bounds:
                var_ssa_bounds[var_base_name] = (str(var), str(var))
                continue
            if var_ssa_bounds[var_base_name][0] > str(var):
                var_ssa_bounds[var_base_name] = (str(var), var_ssa_bounds[var_base_name][1])
            if var_ssa_bounds[var_base_name][1] < str(var):
                var_ssa_bounds[var_base_name] = (var_ssa_bounds[var_base_name][0], str(var))

    def _init_var_ssa_bounds(self, var_ssa_bounds: dict[str, tuple[str, str]], path: list[Node], tmp_irs: dict[str, OperationWithLValue]):
        """ Initializes the SSA bounds for all variables in the given path

        Args:
            var_ssa_bounds (dict[str, tuple[str, str]]): a mapping of variable base names to their SSA bounds
            path (list[Node]): The list of nodes in the path
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations
        """

        for node in path:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue and not self._is_solidity_tmp_assignment(ir) and not isinstance(ir, Phi):
                    vars = [ir.lvalue]
                    self.get_read_vars(ir, vars, tmp_irs)
                    for var in vars:
                        var_base_name = self._get_solidity_var_base_name(var)
                        if var_base_name not in var_ssa_bounds:
                            var_ssa_bounds[var_base_name] = (str(var), str(var))

    def _add_bounds_checks(self, op: NaryOp, var_ssa_bounds: dict[str, tuple[str, str]]):
        """ Adds bounds checks for all variables in the SSA bounds mapping to the given conditions list

        Args:
            conditions (list[str]): The list of conditions to update
            var_ssa_bounds (dict[str, tuple[str, str]]): a mapping of variable base names to their SSA bounds
        """
        
        for var, bounds in var_ssa_bounds.items():
            op.append(Equal(bounds[0], var))
            op.append(Equal(bounds[1], f'{var}!'))

    def _merge_ssa_bounds(self, var_ssa_bounds: dict[str, tuple[str, str]], branch_bounds: dict[str, tuple[str, str]]):
        for var, (lb, ub) in branch_bounds.items():
            if var in var_ssa_bounds:
                old_lb, old_ub = var_ssa_bounds[var]
                var_ssa_bounds[var] = (min(lb, old_lb), max(ub, old_ub))
                continue

            var_ssa_bounds[var] = (lb, ub)

    def _compute_trans_op(self, node: Node, tmp_irs: dict[str, OperationWithLValue], var_ssa_bounds: dict[str, tuple[str, str]], root_op: Or, branch_op: And):
        """ Recursively computes the execution conditions for the loop transition path

        Args:
            node (Node): The current node in the transition path
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations
            var_ssa_bounds (dict[str, tuple[str, str]]): a mapping of variable base names to their SSA bounds
            root_op (Or): The root operation for the transition path
            branch_op (And): The current branch operation being constructed

        Returns:
            Or: The root operation representing all execution conditions for the transition path
        """

        if not node.contains_if():
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue and not self._is_solidity_tmp_assignment(ir) and not isinstance(ir, Phi):
                    # Update the SSA bounds for the variables involved in the operation
                    self._update_var_ssa_bounds(var_ssa_bounds, ir, tmp_irs)
                    # Add the operation to the current execution condition
                    branch_op.append(self._solidity_lvalue_op_to_smt(ir, tmp_irs))

            # Continue to the next node if it does not dominate the current node (to avoid cycles)
            if len(node.sons) > 0 and node.sons[0] not in node.dominators:
                return self._compute_trans_op(node.sons[0], tmp_irs, var_ssa_bounds, root_op, branch_op)
            
            # If the node is a leaf, add bounds checks and return
            self._add_bounds_checks(branch_op, var_ssa_bounds)
            return

        # If the node is conditional, bifurcate
        new_branch_op = And(*branch_op.args.copy())
        root_op.append(new_branch_op)
        
        true_branch_var_ssa_bounds = var_ssa_bounds.copy()
        false_branch_var_ssa_bounds = var_ssa_bounds.copy()

        if node.son_true:
            branch_op.append(self._solidity_conditional_node_to_op(node, tmp_irs))
            self._compute_trans_op(node.son_true, tmp_irs, true_branch_var_ssa_bounds, root_op, branch_op)
        if node.son_false:
            new_branch_op.append(Not(self._solidity_conditional_node_to_op(node, tmp_irs)))
            self._compute_trans_op(node.son_false, tmp_irs, false_branch_var_ssa_bounds, root_op, new_branch_op)

        self._merge_ssa_bounds(var_ssa_bounds, true_branch_var_ssa_bounds)
        self._merge_ssa_bounds(var_ssa_bounds, false_branch_var_ssa_bounds)

    def _get_trans_op(self, loop_condition_op: Op|str, trans_path: list[Node], tmp_irs: dict[str, OperationWithLValue]) -> Or:
        """ Generate the operation to check the invariant in the loop transition

        Args:
            loop_condition_op (str): The loop condition operation

        Returns:
            Op: An Op object to check the invariant in the loop transition
        """

        branch_op = And()
        root_op = Or(branch_op)
        var_ssa_bounds: dict[str, tuple[str, str]] = {}
        self._init_var_ssa_bounds(var_ssa_bounds, trans_path, tmp_irs)
        self._compute_trans_op(trans_path[1], tmp_irs, var_ssa_bounds, root_op, branch_op)

        # Add the loop condition to the beginning of each execution condition
        for branch_op in root_op:
            if not isinstance(branch_op, And):
                raise Exception(f'Invalid branch operation {branch_op}')
            branch_op.insert(0, loop_condition_op)

        # Add the execution condition that represents the case where the loop body is not executed
        branch_op = And()
        root_op.append(branch_op)
        for var in var_ssa_bounds:
            branch_op.append(Equal(var_ssa_bounds[var][0], var))
            branch_op.append(Equal(var_ssa_bounds[var][0], f'{var}!'))

        return root_op

    def _get_pre_op(self, pre_path: list[Node], tmp_irs: dict[str, OperationWithLValue]) -> Op:
        """ Generate the operation to check the loop invariant pre-conditions

        Args:
            pre_path (list[Node]): The list of nodes in the pre loop path 
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations
        Returns:
            Op: An Op object to check the loop invariant pre-conditions
        """
        
        guards = set()
        pre_conditions = []
        for node in pre_path:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue and not isinstance(ir, Phi):
                    # The guard transports the value of the base variable to the state variable
                    guards.add(Equal(str(ir.lvalue), self._get_solidity_var_base_name(ir.lvalue)))

                    pre_conditions.append(self._solidity_lvalue_op_to_smt(ir, tmp_irs)) 
        
        pre_conditions = list(guards) + pre_conditions 

        return And(*pre_conditions)

    def _solidity_lvalue_op_to_smt(self, ir: OperationWithLValue, tmp_irs: dict[str, OperationWithLValue]) -> Equal:
        """ Converts an IR operation with an LValue to SMT-LIB2 format

        Args:
            ir (OperationWithLValue): The IR operation to convert
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations

        Raises:
            Exception: If the operation is invalid or unsupported

        Returns:
            Equal: An Equal object representing the operation in SMT-LIB2 format

        """

        return Equal(str(ir.lvalue), self._solidity_op_to_op(ir, tmp_irs))

    def _solidity_op_to_op(self, ir: OperationWithLValue, tmp_irs: dict[str, OperationWithLValue]) -> Op|str:
        """ Converts a Solidity IR operation to an Op object

        Args:
            ir (OperationWithLValue): The IR operation to convert
            tmp_irs (dict[str, OperationWithLValue]): A mapping of temporary variable names to their corresponding IR operations

        Raises:
            Exception: If the operation is invalid or unsupported

        Returns:
            Op|str: The corresponding Op object or string representation of the operation
        """

        if isinstance(ir, Binary):
            reads:list[str|Op] = [str(ir.read[0]), str(ir.read[1])]
            
            # If one of the reads is a temporary variable, recursively resolve it
            if isinstance(ir.read[0], TemporaryVariable):
                reads[0] = self._solidity_op_to_op(tmp_irs[str(ir.read[0])], tmp_irs)
            if isinstance(ir.read[1], TemporaryVariable):
                reads[1] = self._solidity_op_to_op(tmp_irs[str(ir.read[1])], tmp_irs)
            
            return self.op_map[ir.type](reads[0], reads[1])
        if isinstance(ir, Unary):
            read = ir.read[0]
            if isinstance(ir.read[0], TemporaryVariable):
                read = self._solidity_op_to_op(tmp_irs[str(ir.read[0])], tmp_irs)
            return self.op_map[ir.type](read)
        if isinstance(ir, Assignment):
            if isinstance(ir.read[0], TemporaryVariable):
                return self._solidity_op_to_op(tmp_irs[str(ir.read[0])], tmp_irs)
            return str(ir.read[0])

        raise Exception(f'Invalid operation {ir}')

    def _get_solidity_var_base_name(self, var: Variable) -> str:
        """ Returns the base name of a variable by removing its SSA suffix

        Args:
            var (Variable): The variable to process

        Returns:
            str: The base name of the variable
        """

        return str(var).split('_')[0]

    def _get_solidity_vars(self, function: Function, contract: Contract) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        """Finds all state variables (SSA) and base variables (non-SSA) in the function and contract

        Args:
            function (Function): The function to analyze
            contract (Contract): The contract to analyze

        Returns:
            tuple[list[tuple[str, str]], list[tuple[str, str]]]: A tuple containing two lists:
                - The first list contains tuples of base variable names and types
                - The second list contains tuples of state variable names and types
        """

        state_vars = [(var[0], self._type_map[var[1]]) for var in self._get_solidity_lvalue_ops_vars(function.nodes)]
        base_vars = [(str(var), self._type_map[str(var.type)]) for var in chain(function.variables, contract.variables)]

        return base_vars, state_vars

    def _get_solidity_lvalue_ops_vars(self, nodes: list[Node]) -> list[tuple[str, str]]:
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

    def _get_solidity_loop_nodes(self, function: Function) -> list[tuple[Node, Node]]:
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

    def _get_solidity_paths(self, function: Function, loop_header: Node, loop_latch: Node) -> tuple[list[Node], list[Node], list[Node]]:
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
