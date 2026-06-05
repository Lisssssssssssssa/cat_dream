from typing import List, Tuple, Dict
from .bsp_generator import generate_bsp_grid
import pygame
import config as cfg
import os
import random


class Level:

    def __init__(self, width: int = cfg.SCREEN_WIDTH, height: int = cfg.SCREEN_HEIGHT, cell_size: int = 32):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid: List[List[int]] = []
        self.objects: List[Dict] = []
        self.start: Tuple[int, int] = (0, 0)
        self.finish: Tuple[int, int] = (0, 0)

        bg_path = os.path.join(cfg.ASSETS_PATH, 'backgrounds', 'dream_bg.png')
        self.bg_surface = pygame.image.load(bg_path).convert_alpha()
        self.bg_surface.set_alpha(60)
        self.bg_surface = pygame.transform.scale(self.bg_surface, (cfg.SCREEN_WIDTH * 2, cfg.SCREEN_HEIGHT))

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

        if floor_cells:
            self.start = min(floor_cells, key=lambda p: (p[0], p[1]))  # левый верхний
            self.finish = max(floor_cells, key=lambda p: (p[0], p[1]))  # правый нижний
        else:
            self.start, self.finish = (0, 0), (0, 0)

        valid_cells = [
            p for p in floor_cells
            if p != self.start and p != self.finish
        ]

        # Если мало клеток — берём сколько можно (минимум 3)
        if len(valid_cells) >= 3:
            toy_positions = random.sample(valid_cells, 3)
        else:
            toy_positions = valid_cells[:]  # бери всё, что есть

        # Добавляем игрушки как объекты
        for tx, ty in toy_positions:
            self.objects.append({
                'type': 'toy',
                'x': tx,
                'y': ty,
                'radius': 12
            })
        print(f"Генерация завершена Найдено клеток пола: {len(floor_cells)}")

    def add_object(self, obj_type: str, x: int, y: int):
        grid_x, grid_y = int(x // self.cell_size), int(y // self.cell_size)

        if obj_type == "platform":
            # Горизонтальная платформа: 3 клетки в ширину, 1 в высоту
            for dx in range(3):
                self.objects.append({
                    'type': 'platform',
                    'x': (grid_x + dx) * self.cell_size + self.cell_size // 2,
                    'y': grid_y * self.cell_size + self.cell_size // 2,
                    'width': self.cell_size * 3,
                    'height': self.cell_size
                })
        elif obj_type == "ladder":
            # Вертикальная лестница: 1 клетка в ширину, 3 в высоту
            for dy in range(3):
                self.objects.append({
                    'type': 'ladder',
                    'x': grid_x * self.cell_size + self.cell_size // 2,
                    'y': (grid_y + dy) * self.cell_size + self.cell_size // 2,
                    'width': self.cell_size,
                    'height': self.cell_size * 3
                })
        else:
            # Старая логика для enemy, weapon и т.д.
            self.objects.append({'type': obj_type, 'x': x, 'y': y})

    def draw(self, screen, camera_offset=(0, 0)):
        """Отрисовывает уровень по сетке с учётом камеры."""
        # Рисуем стены и пол
        screen.fill((10, 5, 30))

        cloud_scroll_x = -camera_offset[0] * 0.5
        cloud_scroll_y = -camera_offset[1] * 0.3
        screen.blit(self.bg_surface, (cloud_scroll_x, cloud_scroll_y))
        screen.blit(self.bg_surface, (cloud_scroll_x + cfg.SCREEN_WIDTH, cloud_scroll_y))

        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(
                    x * self.cell_size - camera_offset[0],
                    y * self.cell_size - camera_offset[1],
                    self.cell_size, self.cell_size
                )
                if cell == 1:
                    wall_surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    wall_surf.fill((30, 30, 40, 90))  # (R, G, B, A)
                    screen.blit(wall_surf, (rect.x, rect.y))
                else:
                    pygame.draw.rect(screen, (60, 50, 90), rect)  # комната

        # Рисуем объекты
        for obj in self.objects:
            color = {
                'enemy': (255, 50, 50),
                'finish': (50, 255, 50),
                'start': (50, 50, 255),
                'weapon': (255, 255, 50),
                'object': (255, 165, 0)
            }.get(obj['type'], (128, 128, 128))
            pygame.draw.circle(screen, color,
                               (obj['x'] - camera_offset[0], obj['y'] - camera_offset[1]),
                               8)

        # Старт и финиш
        pygame.draw.circle(screen, (50, 50, 255),
                           (self.start[0] - camera_offset[0], self.start[1] - camera_offset[1]),
                           10, 2)
        pygame.draw.circle(screen, (50, 255, 50),
                           (self.finish[0] - camera_offset[0], self.finish[1] - camera_offset[1]),
                           10, 2)

    def remove_object_at(self, x: int, y: int, radius: int = 20):
        self.objects = [
            obj for obj in self.objects
            if ((obj['x'] - x) ** 2 + (obj['y'] - y) ** 2) > radius ** 2
        ]

    def is_walkable_pixel(self, px: int, py: int) -> bool:
        """Проверяет, находится ли пиксель (px, py) на полу (не на стене)."""
        # Переводим пиксельные координаты в координаты сетки
        grid_x = int(px // self.cell_size)
        grid_y = int(py // self.cell_size)

        # Проверяем границы
        if not (0 <= grid_y < len(self.grid)) or not (0 <= grid_x < len(self.grid[0])):
            return False

        return self.grid[grid_y][grid_x] == 0
