from typing import List, Tuple, Dict
from .bsp_generator import generate_bsp_grid
import pygame
import config as cfg
import os


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

        if len(floor_cells) >= 2:
            self.start = floor_cells[0]
            self.finish = floor_cells[-1]
        elif floor_cells:
            self.start = floor_cells[0]
            self.finish = floor_cells[0]
        print(f"Генерация завершена Найдено клеток пола: {len(floor_cells)}")

    def add_object(self, obj_type: str, x: int, y: int):
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
