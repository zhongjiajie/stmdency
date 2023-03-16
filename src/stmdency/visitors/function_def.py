from __future__ import annotations

from dataclasses import dataclass, field

import libcst as cst
import libcst.matchers as m
from libcst import Assign, Attribute, Call, FunctionDef, Name, Param

from stmdency.models.node import StmdencyNode


@dataclass
class FunctionDefVisitor(cst.CSTVisitor):
    """Handle function definition dependencies.

    :param PV: The parent visitor from visitor route :class:`stmdency.visitor.Visitor`, type Visitor
    :param func_name: Current function name
    :param local_param: local parameter of current function parameters
    :param scope: statement scope set to avoid error handle
    """

    PV: "BaseVisitor"  # noqa: F821
    func_name: str | None = None
    local_param: set[str] = field(default_factory=set)
    # Add scope to determine if the node is in the same scope
    scope: set[cst.CSTNode] = field(default_factory=set)

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
    def visit_FunctionDef_decorators(self, node: FunctionDef) -> None:
        """Remove function definition decorators."""
        if node.decorators:
            node_change = node.with_changes(
                decorators=(),
            )
            self.PV.stack[self.func_name] = StmdencyNode(node_change)
            self.scope.add(node)

    def leave_FunctionDef_decorators(self, node: FunctionDef) -> None:
        """Remove function definition decorators in scope."""
        if node.decorators:
            self.scope.remove(node)

    def visit_FunctionDef(self, node: FunctionDef) -> bool | None:
        """Extract function name from function definition."""
        self.func_name = node.name.value
        self.PV.stack.update([(self.func_name, StmdencyNode(node=node))])
        return True

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
        if node.default and m.matches(node.default, m.Name()):
            default = node.default.value
            default_node = self.PV.stack.get(default)
            self.PV.stack[self.func_name].parent.append(default_node)

    def visit_Assign(self, node: Assign) -> bool | None:
        """Extract local parameter and add current nodo to local scope."""
        if m.matches(node.targets[0].target, m.Name()):
            name = cst.ensure_type(node.targets[0].target, cst.Name).value
            # Add to assign target to skip visit in :func:`visit_Name`
            self.local_param.update(name)
        return True

    def visit_Name(self, node: Name) -> bool | None:
        """Find using global name as dependency."""
        name = node.value

        # func come from parameter or have scope cover
        if self.scope or name in self.local_param:
            return

        # func come from global scope, NOTE: need to skip current function itself
        if name in self.PV.stack and name != self.func_name:
            name_node = self.PV.stack.get(name)
            self.PV.stack[self.func_name].parent.append(name_node)
