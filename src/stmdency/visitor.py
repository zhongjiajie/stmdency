from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Union

import libcst as cst
import libcst.matchers as m
from libcst import (
    Assign,
    AssignTarget,
    Attribute,
    Call,
    FunctionDef,
    Import,
    ImportFrom,
    Name,
    Param,
)


@dataclass
class StmdencyNode:
    """Stmdency extracted node.

    :param node: The libcst node for current statement dependency
    :param parent: The parent node of current statement dependency, type StmdencyNode
    """

    # name: str
    node: cst.CSTNode
    parent: List["StmdencyNode"] = field(default_factory=list)

    def __hash__(self):
        return hash(self.node)

    def __eq__(self, other):
        """Override the default implementation."""
        if isinstance(other, StmdencyNode):
            return self.node == other.node and self.parent == other.parent
        return False


@dataclass
class Visitor(cst.CSTVisitor):
    """Main class for extract statement dependency, will route to sub visitor for different node type.

    :param stack: The stack for store all the statement dependency, key is the identifier name,
        value is StmdencyNode
    :param scope: The scope flag to skip the some of visit_xxx in function
    """

    stack: Dict[str, StmdencyNode] = field(default_factory=dict)
    # Add scope to determine if the node is in the same scope
    scope: Set[cst.CSTNode] = field(default_factory=set)

    def handle_import(self, node: Union[Import, ImportFrom]) -> None:
        """Handle `import` / `from xx import xxx` statement and parse/add to stack."""
        for name in node.names:
            self.stack.update([(name.name.value, StmdencyNode(node=node))])

    def visit_Import(self, node: Import) -> Optional[bool]:
        """Handle `import` statement and parse/add to stack."""
        self.handle_import(node)

    def visit_ImportFrom(self, node: ImportFrom) -> Optional[bool]:
        """Handle `from xx import xxx` statement and parse/add to stack."""
        self.handle_import(node)

    def visit_FunctionDef(self, node: FunctionDef) -> Optional[bool]:
        """Handle function definition, pass to FunctionVisitor and add scope.

        the reason add scope is to skip the visit_Assign in current class
        """
        self.scope.add(node)
        node.visit(FunctionDefVisitor(self))

    def leave_FunctionDef(self, original_node: FunctionDef) -> None:
        """Remove function definition in scope."""
        self.scope.remove(original_node)

    def visit_Assign(self, node: Assign) -> Optional[bool]:
        """Handle assign statement in all expect function definition, and pass to AssignVisitor."""
        if self.scope:
            return False
        name = cst.ensure_type(node.targets[0].target, cst.Name).value
        self.stack.update([(name, StmdencyNode(node=node))])
        node.visit(AssignVisitor(self, node))


@dataclass
class AssignVisitor(cst.CSTVisitor):
    """Handle assign statement dependencies.

    :param PV: The parent visitor from visitor route :class:`stmdency.visitor.Visitor`, type Visitor
    :param root_node: Assign statement root node
    :param name: Assign statement name target variable name
    """

    # current: str
    PV: Visitor
    root_node: cst.CSTNode
    name: str = None

    def visit_AssignTarget_target(self, node: AssignTarget) -> None:
        """Extract assign target name and update it to the parent stack."""
        self.name = cst.ensure_type(node.target, cst.Name).value
        self.PV.stack.update([(self.name, StmdencyNode(node=self.root_node))])

    def visit_Name(self, node: Name) -> Optional[bool]:
        """Extract global dependencies according to assign expression cst.Name."""
        if (
            not cst.ensure_type(node, cst.Name)
            or cst.ensure_type(node, cst.Name).value == self.name
        ):
            return False
        current = self.PV.stack.get(self.name, None)
        previous = self.PV.stack.get(node.value, None)
        if previous:
            current.parent.append(previous)

    def visit_Call_func(self, node: Call) -> None:
        """Extract global dependencies according to assign expression cst.Call."""
        func = node.func
        if m.matches(
            func,
            m.Attribute(
                value=m.Name(m.MatchIfTrue(lambda name: name in self.PV.stack)),
                attr=m.Name(),
            ),
        ):
            func_name = cst.ensure_type(func, cst.Attribute).value.value
            func_node = self.PV.stack[func_name]
            self.PV.stack[self.name].parent.append(func_node)


@dataclass
class FunctionDefVisitor(cst.CSTVisitor):
    """Handle function definition dependencies.

    :param PV: The parent visitor from visitor route :class:`stmdency.visitor.Visitor`, type Visitor
    :param func_name: Current function name
    :param local_param: local parameter of current function parameters
    :param scope: statement scope set to avoid error handle
    """

    PV: Visitor
    func_name: Optional[str] = None
    local_param: Set[str] = field(default_factory=set)
    # Add scope to determine if the node is in the same scope
    scope: Set[cst.CSTNode] = field(default_factory=set)

    def leave_FunctionDef_leading_lines(self, node: FunctionDef) -> None:
        """Remove leading lines from function definition.

        This function is called behind function :func:`visit_FunctionDef`
        """
        if node.leading_lines:
            func_node = self.PV.stack[self.func_name].node
            self.PV.stack[self.func_name].node = func_node.with_changes(
                leading_lines=(),
            )

    # TODO: should add module config to do it, instead of hard code
    def visit_FunctionDef_decorators(self, node: "FunctionDef") -> None:
        """Remove function definition decorators."""
        if node.decorators:
            node_change = node.with_changes(
                decorators=(),
            )
            self.PV.stack[self.func_name] = StmdencyNode(node_change)
            self.scope.add(node)

    def leave_FunctionDef_decorators(self, node: "FunctionDef") -> None:
        """Remove function definition decorators in scope."""
        if node.decorators:
            self.scope.remove(node)

    def visit_FunctionDef(self, node: FunctionDef) -> Optional[bool]:
        """Extract function name from function definition."""
        self.func_name = node.name.value
        self.PV.stack.update([(self.func_name, StmdencyNode(node=node))])

    def handle_func_call(self, func_name: str) -> None:
        """Handle function call name dependencies."""
        # func come from parameter
        if func_name in self.local_param:
            return

        # func come from global scope
        if func_name in self.PV.stack:
            in_func_node = self.PV.stack.get(func_name)
            self.PV.stack[self.func_name].parent.append(in_func_node)

    def visit_Call_func(self, node: Call) -> None:
        """Extract global dependency in function body."""
        if not m.matches(
            node.func,
            m.Attribute | m.Name,
        ):
            raise ValueError("Not support function call type yet, %s", type(node.func))

        # func is Attribute
        if m.matches(
            node.func,
            m.Attribute(
                value=m.Name(m.MatchIfTrue(lambda name: name in self.PV.stack)),
                attr=m.Name(),
            ),
        ):
            inline_func_name = cst.ensure_type(
                cst.ensure_type(node.func, Attribute).value, Name
            ).value
            self.handle_func_call(inline_func_name)

        # func is Name
        if m.matches(
            node.func,
            m.Name(
                value=m.MatchIfTrue(lambda name: name in self.PV.stack),
            ),
        ):
            inline_func_name = cst.ensure_type(node.func, Name).value
            self.handle_func_call(inline_func_name)

    def visit_Param_name(self, node: Param) -> None:
        """Add param name to skip global dependency, Add param default to dependency."""
        if not cst.ensure_type(node.name, cst.Name):
            return
        self.local_param.update([node.name.value])
        if node.default and cst.ensure_type(node.default, cst.Name):
            default = node.default.value
            default_node = self.PV.stack.get(default)
            self.PV.stack[self.func_name].parent.append(default_node)

    def visit_Assign(self, node: Assign) -> Optional[bool]:
        """Extract local parameter and add current nodo to local scope."""
        name = cst.ensure_type(node.targets[0].target, cst.Name).value
        # Add to assign target to skip visit in :func:`visit_Name`
        self.local_param.update(name)

    def visit_Name(self, node: Name) -> Optional[bool]:
        """Find using global name as dependency."""
        name = node.value

        # func come from parameter or have scope cover
        if self.scope or name in self.local_param:
            return

        # func come from global scope, NOTE: need to skip current function itself
        if name in self.PV.stack and name != self.func_name:
            name_node = self.PV.stack.get(name)
            self.PV.stack[self.func_name].parent.append(name_node)
