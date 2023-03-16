from __future__ import annotations

from dataclasses import dataclass

import libcst as cst
import libcst.matchers as m
from libcst import AssignTarget, Call, Name

from stmdency.models.node import StmdencyNode


@dataclass
class AssignVisitor(cst.CSTVisitor):
    """Handle assign statement dependencies.

    :param PV: The parent visitor from visitor route :class:`stmdency.visitor.Visitor`, type Visitor
    :param root_node: Assign statement root node
    :param name: Assign statement name target variable name
    """

    # current: str
    PV: "BaseVisitor"  # noqa: F821
    root_node: cst.CSTNode
    name: str = None

    def visit_AssignTarget_target(self, node: AssignTarget) -> None:
        """Extract assign target name and update it to the parent stack."""
        self.name = cst.ensure_type(node.target, cst.Name).value
        self.PV.stack.update([(self.name, StmdencyNode(node=self.root_node))])

    def visit_Name(self, node: Name) -> bool | None:
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
