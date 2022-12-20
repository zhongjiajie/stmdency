from dataclasses import dataclass, field
from typing import Optional

import libcst as cst

from stmdency.constants import TOKEN
from stmdency.visitor import StmdencyNode, Visitor


@dataclass
class Extractor:
    """Main class for extract statement dependency, will call the visitor to get dependency.

    :param source: The source code want to extract dependency
    :param visitor: The visitor class, default is :class:`stmdency.visitor.Visitor`
    """

    source: str
    visitor: Visitor = field(init=False, default_factory=Visitor)

    def walk(self) -> None:
        """Walk the source code and run libcst visitor."""
        parse_cst = cst.parse_module(self.source)
        parse_cst.visit(self.visitor)

    def build_parents_str(self, node: StmdencyNode) -> str:
        """Build the parents string for given node, will travel all exists parents and build the string.

        :param node: The node want to travel all the parents
        """
        parents = []
        cst_mod = cst.parse_module("")

        for parent_node in node.parent:
            for uniq in parent_node.parent:
                parents.append(self.build_parents_str(uniq))

            curr = cst_mod.code_for_node(parent_node.node)
            parents.append(curr)

        # Remove duplicates and keep order, after cpython 3.6, dict can be ordered set to filter
        # out duplicate items
        uniq_parents = list(dict.fromkeys(parents))
        uniq_parents.append(cst_mod.code_for_node(node.node))
        return TOKEN.EXTRACTOR_NEW_LINE.join(uniq_parents)

    def get(self, value: str) -> Optional[StmdencyNode]:
        """Get dependency node for given identifier name, you can paste vairable name and function name here.

        :param value: The identifier name, variable name or function name
        """
        self.walk()
        return self.visitor.stack.get(value, None)

    def get_code(self, value: str) -> Optional[str]:
        """Get dependency code for given identifier name, you can paste vairable name and function name here.

        Will call :meth:`stmdency.extractor.Extractor.get` to get the node and build the code string.

        :param value: The identifier name, variable name or function name
        """
        sdn = self.get(value)
        if not sdn:
            raise ValueError(f"Statement {value} not found")

        return self.build_parents_str(sdn)
