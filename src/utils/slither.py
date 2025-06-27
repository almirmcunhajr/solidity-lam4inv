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
               
def preorder_traversal(origin_node: Node, backward: bool = False) -> list[Node]:
    path, visited, stack = [], set(), [origin_node]
    while stack:
        node = stack.pop()
        visited.add(node)
        path.append(node)

        preds = node.sons
        if backward:
            preds = node.fathers
        for pred in preds:
            if pred not in visited:
                stack.append(pred)
    return path
                
