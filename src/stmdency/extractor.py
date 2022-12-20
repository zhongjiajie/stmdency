from dataclasses import dataclass, field
from typing import List, Optional

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

    def get_parents(self, node: StmdencyNode) -> List[StmdencyNode]:
        """Get all parents node from given StmdencyNode.

        :param node: The node want to travel all the parents
        """
        parents = []

        for parent_node in node.parent:
            for grandparent in parent_node.parent:
                parents.extend(self.get_parents(grandparent))
            parents.append(parent_node)

        parents.append(node)
        return parents

    def get(self, value: str) -> Optional[StmdencyNode]:
        """Get dependency node for given identifier name, you can paste vairable name and function name here.

        :param value: The identifier name, variable name or function name
        """
        self.walk()
        return self.visitor.stack.get(value, None)

    def get_code(self, value: str) -> str:
        """Get dependency code for given identifier name, you can paste vairable name and function name here.

        Will call :meth:`stmdency.extractor.Extractor.get` to get the node and build the code string.

        :param value: The identifier name, variable name or function name
        """
        sdn = self.get(value)
        if not sdn:
            raise ValueError(f"Statement {value} not found")

        parents = self.get_parents(sdn)
        # Remove duplicates and keep order, after cpython 3.6, dict can be ordered set to filter
        # out duplicate items
        uniq_parents = list(dict.fromkeys(parents))

        cst_mod = cst.parse_module("")
        code_snippet = [cst_mod.code_for_node(parent.node) for parent in uniq_parents]
        return TOKEN.EXTRACTOR_NEW_LINE.join(code_snippet)
