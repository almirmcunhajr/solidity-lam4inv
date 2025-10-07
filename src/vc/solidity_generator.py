import logging
import os
import sys
from itertools import chain
from typing import Callable, Optional

from slither.core.cfg.node import NodeType
from slither.core.solidity_types.elementary_type import Int, Uint
from slither.slither import Slither
from slither.core.cfg.node import Constant, InternalCall, Node, Operation, Phi, TemporaryVariable, Variable
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

    def __init__(self, file_path: str, logger: logging.Logger, contract_name: str, function_name: str):
        self._logger = logger
        self._slither = Slither(file_path, disable_plugins=["solc-ast-exporter"])
        self._contract_name = contract_name
        self._function_name = function_name

        self._base_vars: list[tuple[str, str]]|None = None
        self._state_vars: list[tuple[str, str]]|None = None
        self._reachability_op: Op|None = None
        self._inductive_op: Op|None = None
        self._provability_op: Op|None = None
        self._generated = False

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

        if self._generated:
            return self._render_vcs(inv)

        self.contract = next((c for c in self._slither.contracts if c.name == self._contract_name), None)
        if self.contract is None:
            raise ContractNotFound()

        self.function = next((f for f in self.contract.functions if f.name == self._function_name), None)
        if self.function is None:
            raise FunctionNotFound()

        compute_dominators(self.function.nodes)

        # Get the first loop header and latch
        loops = self._get_solidity_loop_nodes()
        if len(loops) == 0:
            raise LoopNotFound()
        self.loop_header = loops[0]
        self.loop_end = next((n for n in self.loop_header.sons if n.type == NodeType.ENDLOOP), None)

        # Get all state variables and base variables in the function and contract
        self._base_vars, self._state_vars = self._get_solidity_vars()

        # Get all temporary IR operations in the function
        self.tmp_irs = self._get_solidity_tmp_irs() 

        # Get the loop condition operation
        self.loop_condition_op = self._solidity_conditional_node_to_op(self.loop_header)

        # Get the reachability verification condition op
        self._reachability_op = self._get_pre_op()

        # Get the inductive verification condition op
        self._inductive_op = self._get_trans_op()

        # Get the provability verification condition op
        self._provability_op = self._get_post_op()
        
        # Mark as generated to avoid recomputation
        self._generated = True

        return self._render_vcs(inv) 

    def _render_vcs(self, inv) -> tuple[str, str, str]:
        """ Generates the SMT-LIB2 verification conditions using a Jinja2 template

        Args:
            inv (str): The loop invariant in SMT-LIB2 format

        Returns:
            tuple[str, str, str]: The pre-condition, transition, and post-condition verification conditions in SMT-LIB2 format
        """
        with open(os.path.join(os.path.dirname(__file__), 'templates/vc.tpl')) as tpl_file:
            tpl_data = tpl_file.read()

        template = Template(tpl_data)
        pre_vc = template.render(
            base_vars=self._base_vars,
            state_vars=self._state_vars,
            inv=inv,
            reachability_vc=str(self._reachability_op),
        )
        trans_vc = template.render(
            base_vars=self._base_vars,
            state_vars=self._state_vars,
            inv=inv,
            inductive_vc=str(self._inductive_op),
        )
        post_vc = template.render(
            base_vars=self._base_vars,
            state_vars=self._state_vars,
            inv=inv,
            provability_vc=str(self._provability_op),
        )

        return pre_vc, trans_vc, post_vc

    def _get_solidity_tmp_irs(self) -> dict[str, OperationWithLValue]:
        """Returns a mapping of temporary variable names to their corresponding IR operations in the functions

        Args:
            function (Function): The function to analyze

        Returns:
            dict[str, OperationWithLValue]: A dictionary mapping temporary variable names to their corresponding IR operations
        """
        tmp_irs = {}
        for node in self.function.nodes:
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

    def _traverse(self, node: Node, limiter: Node, visited: set[Node], visit_function: Callable, *args, **kwargs):
        """ Helper function to traverse the CFG from node to limiter using DFS

        Args:
            node (Node): The current node in the traversal
            limiter (Node): The node at which to stop the traversal
            visited (set[Node]): A set of visited nodes to avoid cycles
            visit_function (callable): A function to call on each visited node
        """

        if node in visited:
            return
        visited.add(node)
        visit_function(node, *args, **kwargs)
        if node == limiter:
            return
        for son in node.sons:
            self._traverse(son, limiter, visited, visit_function)

    def _get_post_op(self) -> Or:
        """Generate the SMT operation that represents the loop invariant post-condition. 

        This ensures that after the loop terminates, the invariant still holds.

        Returns:
            Op: An Op object to check the loop invariant post condition
        """
        start_node = self.loop_end.sons[0]
        end_node = self.function.nodes[-1]

        # The invariant must hold if the loop exits. Negating the loop condition expresses that we are at loop exit.
        assertion_op = And()
        if self.loop_condition_op != "":
            assertion_op = And(Not(self.loop_condition_op))

        def visit_function(node: Node, *args, **kwargs):
            # If there are extra conditions in the post-path (e.g. if-statements, asserts), we append them to the assertion.
            if node.contains_if():
                return
            for ir in node.irs_ssa:
                # If the node contains an assert, we capture its IR and negate it.
                if  isinstance(ir, SolidityCall) and ir.function.name == "assert(bool)":
                    post_condition_ir = self.tmp_irs[str(ir.arguments[0])]
                    assertion_op.append(Not(self._solidity_op_to_op(post_condition_ir)))
                    return
        self._traverse(start_node, end_node, set(), visit_function, assertion_op)

        # Root operator is the OR of possible violations of the post-condition.
        root_op = Or(Not(assertion_op))

        # Ensures that variables are not trivially unchanged
        triviality_op = And()
        vars_ssa_bounds: dict[str, Optional[tuple[str, str]]] = {}
        self._init_bounds(start_node, end_node, vars_ssa_bounds)
        for var in vars_ssa_bounds:
            bounds = vars_ssa_bounds[var]
            if not bounds:
                continue
            triviality_op.append(Equal(bounds[0], var))

        # Negating this ensures we don't accept "stuttering" executions where all variables are identical before and after.
        root_op.append(Not(triviality_op))

        return root_op

    def _solidity_conditional_node_to_op(self, node: Node) -> Op|str:
        """ Converts a Solidity conditional node to an operation

        Args:
            node (Node): The conditional node to convert
        Raises:
            Exception: If the node is not conditional

        Returns:
            Op|str: The operation representing the condition of the node
        """

        if not node.is_conditional():
            raise Exception(f'Node is not conditional {node}')

        conditions_irs = []
        for ir in node.irs_ssa:
            if not isinstance(ir, Phi) and isinstance(ir, OperationWithLValue) and ir.lvalue and not isinstance(ir, InternalCall):
                conditions_irs.append(ir)
                
        if len(conditions_irs) == 0:
            return ""
        return self._solidity_op_to_op(conditions_irs[-1])

    def _retrieve_read_vars(self, ir: Operation, vars: list[Variable]):
        """ Recursively retrieves all variables read by the given IR operation, including those read by temporary variables
        Args:
            ir (OperationWithLValue): The IR operation to analyze
            vars (list[Variable]): The list to populate with read variables
        """

        if not ir.read:
            return
        for var in ir.read:
            if  not isinstance(var, TemporaryVariable) and not isinstance(var, Constant):
                vars.append(var)
                continue
            if isinstance(var, TemporaryVariable):
                self._retrieve_read_vars(self.tmp_irs[str(var)], vars)

    def _update_var_ssa_bounds(self, var_ssa_bounds: dict[str, Optional[tuple[str, str]]], ir: OperationWithLValue):
        """ Updates the SSA bounds for the variables involved in the given IR operations

        Args:
            var_ssa_bounds (dict[str, tuple[str, str]]): a mapping of variable base names to their SSA bounds
            ir (OperationWithLValue): The IR operation to analyze

        Raises:
            Exception: If the operation is invalid
        """
        
        if not ir.lvalue:
            raise Exception('Invalid operation {ir}')
        var_base_name = self._get_solidity_ssa_var_base_name(ir.lvalue)
        if var_base_name not in var_ssa_bounds or var_ssa_bounds[var_base_name] is None:
            var_ssa_bounds[var_base_name] = ("", str(ir.lvalue))
            return
        bounds = var_ssa_bounds[var_base_name]
        if bounds[1] < str(ir.lvalue):
            var_ssa_bounds[var_base_name] = (bounds[0], str(ir.lvalue))

    def _init_bounds(self, node: Node, limiter: Node, var_ssa_bounds: dict[str, Optional[tuple[str, str]]]):
        """ Initializes the SSA bounds for all variables in the path from node to limiter (inclusive)

        This uses DFS to traverse the nodes from node to limiter, initializing the SSA bounds for all variables encountered.

        Args:
            node (Node): The starting node
            limiter (Node): The ending node
            var_ssa_bounds (dict[str, tuple[str, str]]): a mapping of variable base names to their SSA bounds
        """

        stack = [node]
        visited = set()
        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            for ir in curr.irs_ssa:
                if not isinstance(ir, Phi):
                    vars = []
                    self._retrieve_read_vars(ir, vars)
                    for var in vars:
                        var_base_name = self._get_solidity_ssa_var_base_name(var)
                        if var_base_name not in var_ssa_bounds or var_ssa_bounds[var_base_name] is None:
                            var_ssa_bounds[var_base_name] = (str(var), str(var))
            if curr == limiter:
                continue
            stack.extend(curr.sons)

        if self._base_vars is None:
            return
        for var in self._base_vars:
            var_base_name = var[0]
            if var_base_name not in var_ssa_bounds:
                var_ssa_bounds[var_base_name] = None

    def _add_bounds_checks(self, op: NaryOp, var_ssa_bounds: dict[str, Optional[tuple[str, str]]]):
        """ Adds bounds checks for all variables in the SSA bounds mapping to the given conditions list

        Args:
            conditions (list[str]): The list of conditions to update
            var_ssa_bounds (dict[str, tuple[str, str]]): a mapping of variable base names to their SSA bounds
        """
        
        for var, bounds in var_ssa_bounds.items():
            if not bounds:
                # Variable was never written, so it must be unchanged
                op.append(Equal(var, f'{var}!'))
                continue
            if bounds[0] != "":
                op.append(Equal(bounds[0], var))
            op.append(Equal(bounds[1], f'{var}!'))

    def _merge_bounds(self, var_ssa_bounds: dict[str, Optional[tuple[str, str]]], branch_bounds: dict[str, Optional[tuple[str, str]]]):
        for var, bounds in branch_bounds.items():
            if not bounds:
                continue
            lb, ub = bounds
            if var in var_ssa_bounds:
                old_bounds = var_ssa_bounds[var]
                if not old_bounds:
                    var_ssa_bounds[var] = (lb, ub)
                    continue
                old_lb, old_ub = old_bounds
                if old_lb == "":
                    old_lb = lb
                var_ssa_bounds[var] = (min(lb, old_lb), max(ub, old_ub))
                continue

            var_ssa_bounds[var] = (lb, ub)

    def _compute_trans_op(self, node: Node, var_ssa_bounds: dict[str, Optional[tuple[str, str]]], root_op: Or, branch_op: And):
        """ Recursively computes the execution conditions for the loop transition path

        Args:
            node (Node): The current node in the transition path
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
                    self._update_var_ssa_bounds(var_ssa_bounds, ir)
                    # Add the operation to the current execution condition
                    branch_op.append(self._solidity_lvalue_op_to_smt(ir))

            # Continue to the next node if it does not dominate the current node (to avoid cycles)
            if len(node.sons) > 0 and node.sons[0] not in node.dominators:
                return self._compute_trans_op(node.sons[0], var_ssa_bounds, root_op, branch_op)
            
            # If the node is a leaf, add bounds checks and return
            self._add_bounds_checks(branch_op, var_ssa_bounds)
            return

        # If the node is conditional, bifurcate
        new_branch_op = And(*branch_op.args.copy())
        root_op.append(new_branch_op)
        
        true_branch_var_ssa_bounds = var_ssa_bounds.copy()
        false_branch_var_ssa_bounds = var_ssa_bounds.copy()

        if node.son_true:
            op = self._solidity_conditional_node_to_op(node)
            if op != "":
                branch_op.append(op)
            self._compute_trans_op(node.son_true, true_branch_var_ssa_bounds, root_op, branch_op)
        if node.son_false:
            op = self._solidity_conditional_node_to_op(node)
            if op != "":
                new_branch_op.append(Not(op))
            self._compute_trans_op(node.son_false, false_branch_var_ssa_bounds, root_op, new_branch_op)

        self._merge_bounds(var_ssa_bounds, true_branch_var_ssa_bounds)
        self._merge_bounds(var_ssa_bounds, false_branch_var_ssa_bounds)

    def _get_trans_op(self) -> Or:
        """ Generate the operation to check the invariant in the loop transition

        Returns:
            Op: An Op object to check the invariant in the loop transition
        """
        start_node = next((n for n in self.loop_header.sons if n.type != NodeType.ENDLOOP), None)
        if start_node is None:
            raise Exception('Invalid loop structure')
        end_node = self.loop_header

        branch_op = And()
        root_op = Or(branch_op)
        var_ssa_bounds: dict[str, Optional[tuple[str, str]]] = {}
        self._init_bounds(start_node, end_node, var_ssa_bounds)
        self._compute_trans_op(start_node, var_ssa_bounds, root_op, branch_op)

        # Add the loop condition to the beginning of each execution condition
        for branch_op in root_op:
            if not isinstance(branch_op, And):
                raise Exception(f'Invalid branch operation {branch_op}')
            if self.loop_condition_op != "": 
                branch_op.insert(0, self.loop_condition_op)

        # Add the execution condition that represents the case where the loop body is not executed
        branch_op = And()
        root_op.append(branch_op)
        for var in var_ssa_bounds:
            branch_op.append(Equal(var, var+'!'))

        return root_op

    def _get_pre_op(self) -> Op:
        """ Generate the operation to check the loop invariant pre-conditions

        Returns:
            Op: An Op object to check the loop invariant pre-conditions
        """

        start_node = self.function.nodes[0]
        end_node = self.loop_header

        vars_ssa_bounds: dict[str, Optional[tuple[str, str]]] = {}
        self._init_bounds(start_node, end_node, vars_ssa_bounds)

        pre_conditions = []
        def visit_function(node: Node, *args, **kwargs):
            for ir in node.irs_ssa:
                if isinstance(ir, SolidityCall) and ir.function.name == "require(bool,string)":
                    ir = self.tmp_irs[str(ir.arguments[0])]
                    pre_conditions.append(self._solidity_op_to_op(ir))
                if isinstance(ir, OperationWithLValue) and ir.lvalue and not isinstance(ir, Phi) and not self._is_solidity_tmp_assignment(ir):
                    pre_conditions.append(self._solidity_lvalue_op_to_smt(ir)) 
                    self._update_var_ssa_bounds(vars_ssa_bounds, ir)
        self._traverse(start_node, end_node, set(), visit_function)
        
        guards = set()
        for var in vars_ssa_bounds:
            bounds = vars_ssa_bounds[var]
            if not bounds:
                continue
            # The guard transports the value of the base variable to the state variable
            if bounds[0] != "":
                guards.add(Equal(bounds[0], var))
                continue
            guards.add(Equal(bounds[1], var))
        
        pre_conditions = list(guards) + pre_conditions 

        return And(*pre_conditions)

    def _solidity_lvalue_op_to_smt(self, ir: OperationWithLValue) -> Equal:
        """ Converts an IR operation with an LValue to SMT-LIB2 format

        Args:
            ir (OperationWithLValue): The IR operation to convert

        Raises:
            Exception: If the operation is invalid or unsupported

        Returns:
            Equal: An Equal object representing the operation in SMT-LIB2 format

        """

        return Equal(str(ir.lvalue), self._solidity_op_to_op(ir))

    def _solidity_op_to_op(self, ir: Operation) -> Op|str:
        """ Converts a Solidity IR operation to an Op object

        Args:
            ir (OperationWithLValue): The IR operation to convert

        Raises:
            Exception: If the operation is invalid or unsupported

        Returns:
            Op|str: The corresponding Op object or string representation of the operation
        """

        if isinstance(ir, Binary):
            reads:list[str|Op] = [str(ir.read[0]), str(ir.read[1])]
            
            # If one of the reads is a temporary variable, recursively resolve it
            if isinstance(ir.read[0], TemporaryVariable):
                reads[0] = self._solidity_op_to_op(self.tmp_irs[str(ir.read[0])])
            if isinstance(ir.read[1], TemporaryVariable):
                reads[1] = self._solidity_op_to_op(self.tmp_irs[str(ir.read[1])])
            
            return self.op_map[ir.type](reads[0], reads[1])
        if isinstance(ir, Unary):
            read = ir.read[0]
            if isinstance(ir.read[0], TemporaryVariable):
                read = self._solidity_op_to_op(self.tmp_irs[str(ir.read[0])])
            return self.op_map[ir.type](read)
        if isinstance(ir, Assignment):
            if isinstance(ir.read[0], TemporaryVariable):
                return self._solidity_op_to_op(self.tmp_irs[str(ir.read[0])])
            return str(ir.read[0])

        raise Exception(f'Invalid operation {ir}')

    def _get_solidity_ssa_var_base_name(self, var: Variable) -> str:
        """ Returns the base name of a variable by removing its SSA suffix

        Args:
            var (Variable): The variable to process

        Returns:
            str: The base name of the variable
        """

        return str(var).split('_')[0]

    def _get_solidity_vars(self) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        """Finds all state variables (SSA) and base variables (non-SSA) in the function and contract

        Returns:
            tuple[list[tuple[str, str]], list[tuple[str, str]]]: A tuple containing two lists:
                - The first list contains tuples of base variable names and types
                - The second list contains tuples of state variable names and types
        """
        state_vars = set()
        for node in self.function.nodes:
            for ir in node.irs_ssa:
                if isinstance(ir, OperationWithLValue) and ir.lvalue and not self._is_solidity_tmp_assignment(ir):
                    state_vars.add((str(ir.lvalue), self._type_map[str(ir.lvalue.type)]))
                if ir.read:
                    for var in ir.read:
                        if not isinstance(var, Constant) and not isinstance(var, TemporaryVariable):
                            state_vars.add((str(var), self._type_map[str(var.type)]))
        state_vars = sorted(list(state_vars))

        base_vars = [(str(var), self._type_map[str(var.type)]) for var in chain(self.function.variables, self.contract.variables)]

        return base_vars, state_vars

    def _get_solidity_loop_nodes(self) -> list[Node]:
        """Finds all loops in the function
        
        Identifies loops by looking for back edges in the control flow graph (CFG) of the function. For every edge (v -> u) in the CFG, if u dominates v, then (v -> u) is a back edge, and u is a loop header.

        Returns:
            list[tuple[Node, Node]]: A list of tuples where each tuple contains the loop header and loop exit nodes
        """

        loops = []
        for v in self.function.nodes:
            for u in v.sons:
                if u in v.dominators:
                    loops.append(u)
        
        return loops

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
    args = sys.argv
    if len(args) < 2:
        print(f'Usage: {args[0]} <solidity-file>')
        sys.exit(1)
    test_file_name = args[1]
    
    generator = SolidityGenerator(test_file_name, logging.getLogger(), 'LoopExample', 'constructor')
    pre_vc, trans_vc, post_vc = generator.generate('test')

    print(pre_vc)
    print(trans_vc)
    print(post_vc)
