from typing import Optional
from slither.core.cfg.node import Node

def get_nearest_node(origin_node: Node, nodes: list[Node]) -> Optional[Node]:
    for node in nodes:
        if reaches_node(origin_node, node):
            return node

def reaches_node(origin_node: Node, dest_node: Node) -> bool:
    visited, stack = set(), [origin_node]
    while stack:
        node = stack.pop()
        if node == dest_node:
            return True
        if node not in visited:
            visited.add(node)
            stack.extend(node.sons)
    return False
               
