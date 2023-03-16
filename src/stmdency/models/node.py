from __future__ import annotations

from dataclasses import dataclass, field

import libcst as cst


@dataclass
class StmdencyNode:
    """Stmdency extracted node.

    :param node: The libcst node for current statement dependency
    :param parent: The parent node of current statement dependency, type StmdencyNode
    """

    # name: str
    node: cst.CSTNode
    parent: list["StmdencyNode"] = field(default_factory=list)

    def __hash__(self):
        return hash(self.node)

    def __eq__(self, other):
        """Override the default implementation."""
        if isinstance(other, StmdencyNode):
            return self.node == other.node and self.parent == other.parent
        return False
