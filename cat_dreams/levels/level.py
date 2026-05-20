from typing import List, Tuple, Dict
from .bsp_generator import generate_bsp_grid
import pygame
import config as cfg


class Level:

    def __init__(self, width: int = cfg.SCREEN_WIDTH, height: int = cfg.SCREEN_HEIGHT, cell_size: int = 32):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid: List[List[int]] = []
        self.objects: List[Dict] = []
        self.start: Tuple[int, int] = (0, 0)
        self.finish: Tuple[int, int] = (0, 0)

    def generate(self, max_depth: int = 4):
        print(f"Начинаю генерацию BSP (depth={max_depth}, cell_size={self.cell_size})...")
        self.grid = generate_bsp_grid(
            self.width, self.height,
            cell_size=self.cell_size,
            max_depth=max_depth
        )

        floor_cells = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == 0:
                    floor_cells.append((x * self.cell_size + self.cell_size // 2,
                                        y * self.cell_size + self.cell_size // 2))

        if len(floor_cells) >= 2:
            self.start = floor_cells[0]
            self.finish = floor_cells[-1]
        elif floor_cells:
            self.start = floor_cells[0]
            self.finish = floor_cells[0]
        print(f"Генерация завершена Найдено клеток пола: {len(floor_cells)}")

    def add_object(self, obj_type: str, x: int, y: int):
        self.objects.append({'type': obj_type, 'x': x, 'y': y})

    def draw(self, screen):
        # Рисуем стены и пол
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size,
                                   self.cell_size, self.cell_size)
                color = (50, 50, 70) if cell == 1 else (100, 100, 120)  # Стена / Пол
                pygame.draw.rect(screen, color, rect)

        # Рисуем объекты
        for obj in self.objects:
            color = {
                'enemy': (255, 50, 50),
                'finish': (50, 255, 50),
                'start': (50, 50, 255),
                'weapon': (255, 255, 50),
                'object': (255, 165, 0)
            }.get(obj['type'], (128, 128, 128))
            pygame.draw.circle(screen, color, (obj['x'], obj['y']), 8)

        # Старт и финиш
        pygame.draw.circle(screen, (50, 50, 255), self.start, 10, 2)
        pygame.draw.circle(screen, (50, 255, 50), self.finish, 10, 2)

    def remove_object_at(self, x: int, y: int, radius: int = 20):
        self.objects = [
            obj for obj in self.objects
            if ((obj['x'] - x) ** 2 + (obj['y'] - y) ** 2) > radius ** 2
        ]
