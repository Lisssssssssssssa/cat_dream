from typing import List, Tuple, Dict
from collections import deque


class LevelValidator:

    def __init__(self, grid: List[List[int]], cell_size: int):
        self.grid = grid
        self.cell_size = cell_size
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0

    def is_walkable(self, x: int, y: int) -> bool:
        if 0 <= y < self.rows and 0 <= x < self.cols:
            return self.grid[y][x] == 0
        return False

    def bfs_path_exists(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:

        # Переводим пиксельные координаты в координаты сетки
        sx, sy = start[0] // self.cell_size, start[1] // self.cell_size
        ex, ey = end[0] // self.cell_size, end[1] // self.cell_size

        if not self.is_walkable(sx, sy) or not self.is_walkable(ex, ey):
            return False

        visited = set()
        queue = deque([(sx, sy)])
        visited.add((sx, sy))

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == (ex, ey):
                return True  # Путь найден!

            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if self.is_walkable(nx, ny) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return False  # Путь не найден

    def validate_request(self, objects: List[Dict], required: List[str]) -> Dict[str, bool]:
        """
        Проверяет, содержит ли уровень все обязательные объекты из ТЗ.
        Возвращает словарь: {'враг': True, 'финиш': False, ...}
        """
        found_types = {obj['type'] for obj in objects}
        result = {}

        for req in required:
            result[req] = req in found_types

        return result

    def get_validation_report(self, start: Tuple[int, int], finish: Tuple[int, int],
                              objects: List[Dict], required: List[str]) -> Dict:
        """Полный отчет о валидации уровня."""
        path_ok = self.bfs_path_exists(start, finish)
        request_ok = self.validate_request(objects, required)

        return {
            'path_exists': path_ok,
            'request_fulfilled': request_ok,
            'is_valid': path_ok and all(request_ok.values())
        }
