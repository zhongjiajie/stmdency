from dataclasses import dataclass, field
from typing import Dict, Optional, Set, Union

import libcst as cst
import libcst.matchers as m
from libcst import Assign, FunctionDef, Import, ImportFrom

from stmdency.models.node import StmdencyNode
from stmdency.visitors.assign import AssignVisitor
from stmdency.visitors.function_def import FunctionDefVisitor


@dataclass
class BaseVisitor(cst.CSTVisitor):
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
        if m.matches(node.names, m.ImportStar()):
            return
        for name in node.names:
            if m.matches(name, m.ImportAlias(asname=m.AsName())):
                self.stack.update([(name.asname.name.value, StmdencyNode(node=node))])
            else:
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
