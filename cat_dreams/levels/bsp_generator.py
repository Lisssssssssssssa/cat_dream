import random
from typing import List


class BSPNode:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.left = None
        self.right = None
        self.is_leaf = True

    def split(self, min_size: int = 8) -> bool:
        if self.width < 2 * min_size and self.height < 2 * min_size:
            return False

        if self.width > self.height:
            split_axis = 0
        elif self.height > self.width:
            split_axis = 1
        else:
            split_axis = random.choice([0, 1])

        if split_axis == 0:
            max_split = self.width - min_size
            if max_split <= min_size:
                return False
            split_pos = random.randint(min_size, max_split)
            self.left = BSPNode(self.x, self.y, split_pos, self.height)
            self.right = BSPNode(self.x + split_pos, self.y, self.width - split_pos, self.height)
        else:
            max_split = self.height - min_size
            if max_split <= min_size:
                return False
            split_pos = random.randint(min_size, max_split)
            self.left = BSPNode(self.x, self.y, self.width, split_pos)
            self.right = BSPNode(self.x, self.y + split_pos, self.width, self.height - split_pos)

        self.is_leaf = False
        return True

    def get_leaves(self) -> List["BSPNode"]:
        if self.is_leaf:
            return [self]
        leaves = []
        if self.left:
            leaves.extend(self.left.get_leaves())
        if self.right:
            leaves.extend(self.right.get_leaves())
        return leaves


def generate_bsp(width: int, height: int, max_depth: int = 5, min_size: int = 8) -> List[BSPNode]:
    root = BSPNode(0, 0, width, height)

    def _split(node: BSPNode, depth: int):
        if depth >= max_depth:
            return
        if node.split(min_size):
            _split(node.left, depth + 1)
            _split(node.right, depth + 1)

    _split(root, 0)
    return root.get_leaves()
