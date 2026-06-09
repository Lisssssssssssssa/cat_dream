import random
from typing import List, Tuple, Optional


class BSPNode:

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.left: Optional['BSPNode'] = None
        self.right: Optional['BSPNode'] = None
        self.room: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)

    def split(self, min_size: int = 8) -> bool:
        if self.left or self.right:
            return False

        if self.width > self.height * 1.25:
            split_axis = 0
        elif self.height > self.width * 1.25:
            split_axis = 1
        else:
            split_axis = random.choice([0, 1])

        max_split = (self.width if split_axis == 0 else self.height) - min_size
        if max_split <= min_size:
            return False

        split_pos = random.randint(min_size, max_split)

        if split_axis == 0:
            self.left = BSPNode(self.x, self.y, split_pos, self.height)
            self.right = BSPNode(self.x + split_pos, self.y, self.width - split_pos, self.height)
        else:
            self.left = BSPNode(self.x, self.y, self.width, split_pos)
            self.right = BSPNode(self.x, self.y + split_pos, self.width, self.height - split_pos)

        return True

    def create_rooms(self, grid: List[List[int]], min_room: int = 3, padding: int = 1):
        """Рекурсивно создаёт комнаты в сетке."""
        if self.left or self.right:
            if self.left:
                self.left.create_rooms(grid, min_room, padding)
            if self.right:
                self.right.create_rooms(grid, min_room, padding)
        else:
            max_w = self.width - padding * 2
            max_h = self.height - padding * 2
            if max_w < min_room or max_h < min_room:
                return

            rw = random.randint(min_room, max_w)
            rh = random.randint(min_room, max_h)
            rx = self.x + random.randint(padding, self.width - rw - padding)
            ry = self.y + random.randint(padding, self.height - rh - padding)

            self.room = (rx, ry, rw, rh)

            for y in range(ry, ry + rh):
                for x in range(rx, rx + rw):
                    if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                        grid[y][x] = 0

    def get_room_center(self) -> Optional[Tuple[int, int]]:
        if self.room:
            rx, ry, rw, rh = self.room
            return (rx + rw // 2, ry + rh // 2)
        if self.left:
            return self.left.get_room_center()
        if self.right:
            return self.right.get_room_center()
        return None


def carve_corridor(grid: List[List[int]], start: Tuple[int, int], end: Tuple[int, int], width: int = 2):
    x1, y1 = start
    x2, y2 = end

    radius = max(0, (width - 1) // 2)

    for x in range(min(x1, x2), max(x1, x2) + 1):
        for dy in range(-radius, radius + 1):
            ny = y1 + dy
            if 0 <= ny < len(grid) and 0 <= x < len(grid[0]):
                grid[ny][x] = 0

    for y in range(min(y1, y2), max(y1, y2) + 1):
        for dx in range(-radius, radius + 1):
            nx = x2 + dx
            if 0 <= y < len(grid) and 0 <= nx < len(grid[0]):
                grid[y][nx] = 0


def generate_bsp_grid(width: int, height: int, cell_size: int = 16,
                      max_depth: int = 5, min_size: int = 4) -> Tuple[List[List[int]], List[Tuple[int, int, int, int]]]:

    cols = width // cell_size
    rows = height // cell_size
    grid = [[1 for _ in range(cols)] for _ in range(rows)]

    root = BSPNode(0, 0, cols, rows)

    def _split(node: BSPNode, depth: int):
        if depth >= max_depth:
            return
        if node.split(min_size):
            _split(node.left, depth + 1)
            _split(node.right, depth + 1)

    _split(root, 0)

    root.create_rooms(grid, min_room=2, padding=1)

    def collect_leaves(node: BSPNode) -> List[BSPNode]:
        if not node.left and not node.right:
            return [node] if node.room else []
        result = []
        if node.left:
            result.extend(collect_leaves(node.left))
        if node.right:
            result.extend(collect_leaves(node.right))
        return result

    leaves = collect_leaves(root)

    for i in range(len(leaves) - 1):
        c1 = leaves[i].get_room_center()
        c2 = leaves[i + 1].get_room_center()
        if c1 and c2:
            carve_corridor(grid, c1, c2, width=2)

    rooms = []
    for leaf in leaves:
        if leaf.room:
            x, y, w, h = leaf.room
            rooms.append((x, y, w, h))

    return grid, rooms
