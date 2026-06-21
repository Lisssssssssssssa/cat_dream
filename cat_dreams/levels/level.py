import os
import random
from typing import List, Tuple, Dict, Optional

import pygame
import config as cfg
from utilits.ui import load_scaled_image
from .bsp_generator import generate_bsp_grid


class Level:
    """
    Представляет игровой уровень. Управляет сеткой проходимости, 
    объектами, точками старта/финиша и процедурной генерацией.
    """

    def __init__(self, width: int = cfg.SCREEN_WIDTH, height: int = cfg.SCREEN_HEIGHT, cell_size: int = 32):
        """
        Инициализация уровня и загрузка ресурсов.

        Args:
            width: Ширина уровня в пикселях.
            height: Высота уровня в пикселях.
            cell_size: Размер одной клетки сетки.
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size

        # Данные уровня
        self.grid: List[List[int]] = []
        self.objects: List[Dict] = []
        self.rooms: List[Tuple[int, int, int, int]] = []
        self.start: Tuple[int, int] = (0, 0)
        self.finish: Tuple[int, int] = (0, 0)

        # Состояние редактора
        self.placed_platforms = 0
        self.max_platforms = 5
        self.placed_ladders = 0
        self.max_ladders = 10
        self.collected_types: set[str] = set()

        # Загрузка ресурсов через утилиту
        bg_path = os.path.join(cfg.ASSETS_PATH, 'backgrounds', 'dream_bg.png')
        self.bg_surface = load_scaled_image(bg_path, (cfg.SCREEN_WIDTH * 2, cfg.SCREEN_HEIGHT))
        if self.bg_surface:
            self.bg_surface.set_alpha(60)

        plat_path = os.path.join(cfg.ASSETS_PATH, 'sprites', 'platform.png')
        self.platform_sprite = load_scaled_image(plat_path, (self.cell_size * 3, self.cell_size))

        ladder_path = os.path.join(cfg.ASSETS_PATH, 'sprites', 'ladder.png')
        self.ladder_sprite = load_scaled_image(ladder_path, (self.cell_size, self.cell_size * 3))

        # Загрузка спрайтов частиц сна по словарю из конфига
        self.dream_particle_sprites: Dict[str, Optional[pygame.Surface]] = {}
        for typ, filename in cfg.DREAM_TYPE_TO_SPRITE.items():
            path = os.path.join(cfg.ASSETS_PATH, 'sprites', f'{filename}.png')
            self.dream_particle_sprites[typ] = load_scaled_image(path, (32, 32))

    def generate(self, max_depth: int = 4) -> None:
        """
        Процедурная генерация уровня через BSP-разбиение.
        Размещает старт, финиш, игрушки и типы снов.

        Args:
            max_depth: Глубина рекурсивного разбиения BSP-дерева.
        """
        self.grid, self.rooms = generate_bsp_grid(
            self.width, self.height,
            cell_size=self.cell_size,
            max_depth=max_depth
        )

        # Поиск клеток пола для старта и финиша
        floor_cells = [
            (x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2)
            for y, row in enumerate(self.grid)
            for x, cell in enumerate(row)
            if cell == 0
        ]

        if floor_cells:
            self.start = min(floor_cells, key=lambda p: (p[0], p[1]))
            self.finish = max(floor_cells, key=lambda p: (p[0], p[1]))
        else:
            self.start = self.finish = (0, 0)

        # Определение комнат старта и финиша
        start_room = finish_room = None
        sx, sy = self.start[0] // self.cell_size, self.start[1] // self.cell_size
        fx, fy = self.finish[0] // self.cell_size, self.finish[1] // self.cell_size

        for room in self.rooms:
            rx, ry, rw, rh = room
            if rx <= sx < rx + rw and ry <= sy < ry + rh:
                start_room = room
            if rx <= fx < rx + rw and ry <= fy < ry + rh:
                finish_room = room

        # Генерация коридорных клеток
        corridor_cells = [
            (x, y) for y, row in enumerate(self.grid)
            for x, cell in enumerate(row)
            if cell == 0 and not any(rx <= x < rx + rw and ry <= y < ry + rh for rx, ry, rw, rh in self.rooms)
        ]

        # Размещение игрушек
        toy_count = min(3, len(corridor_cells))
        for gx, gy in random.sample(corridor_cells, toy_count):
            self.objects.append({
                'type': 'toy',
                'x': gx * self.cell_size + self.cell_size // 2,
                'y': gy * self.cell_size + self.cell_size // 2,
                'radius': 5
            })

        # Размещение типов снов в доступных комнатах
        available_rooms = [r for r in self.rooms if r != start_room and r != finish_room]
        selected_rooms = random.sample(available_rooms, min(6, len(available_rooms)))
        dream_types_shuffled = random.sample(cfg.DREAM_TYPES, len(cfg.DREAM_TYPES))

        for i, room in enumerate(selected_rooms):
            typ = dream_types_shuffled[i % len(dream_types_shuffled)]
            rx, ry, rw, rh = room
            cx = (rx + rw // 2) * self.cell_size + self.cell_size // 2
            cy = (ry + rh // 2) * self.cell_size + self.cell_size // 2

            self.objects.append({
                'type': typ,
                'x': cx,
                'y': cy,
                'radius': 8
            })

    def add_object(self, obj_type: str, x: int, y: int) -> None:
        """
        Добавляет объект на уровень в указанных координатах.
        Поддерживает платформы, лестницы и произвольные объекты.

        Args:
            obj_type: Тип объекта ('platform', 'ladder' или другой).
            x: Координата X в пикселях.
            y: Координата Y в пикселях.
        """
        grid_x, grid_y = int(x // self.cell_size), int(y // self.cell_size)

        if obj_type == "platform":
            if self.placed_platforms >= self.max_platforms:
                return
            self.objects.append({
                'type': 'platform',
                'x': grid_x * self.cell_size + self.cell_size // 2,
                'y': grid_y * self.cell_size + self.cell_size // 2,
                'width': self.cell_size * 3,
                'height': self.cell_size
            })
            self.placed_platforms += 1

        elif obj_type == "ladder":
            if self.placed_ladders >= self.max_ladders:
                return
            self.objects.append({
                'type': 'ladder',
                'x': grid_x * self.cell_size + self.cell_size // 2,
                'y': grid_y * self.cell_size + self.cell_size // 2,
                'width': self.cell_size,
                'height': self.cell_size * 3
            })
            self.placed_ladders += 1
        else:
            self.objects.append({'type': obj_type, 'x': x, 'y': y})

    def draw(self, screen: pygame.Surface) -> None:
        """
        Отрисовывает уровень: фон, сетку стен/пола и все объекты.

        Args:
            screen: Поверхность экрана Pygame.
        """
        screen.fill((10, 5, 30))
        if self.bg_surface:
            screen.blit(self.bg_surface, (0, 0))

        # Отрисовка сетки
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                if cell == 1:
                    wall_surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                    wall_surf.fill((30, 30, 40, 90))
                    screen.blit(wall_surf, rect.topleft)
                else:
                    pygame.draw.rect(screen, (60, 50, 90), rect)

        # Отрисовка объектов
        for obj in self.objects:
            ox, oy = obj['x'], obj['y']

            if obj['type'] == 'platform' and self.platform_sprite:
                w = obj.get('width', self.cell_size * 3)
                h = obj.get('height', self.cell_size)
                screen.blit(self.platform_sprite, (ox - w // 2, oy - h // 2))

            elif obj['type'] == 'ladder' and self.ladder_sprite:
                w = obj.get('width', self.cell_size)
                h = obj.get('height', self.cell_size * 3)
                screen.blit(self.ladder_sprite, (ox - w // 2, oy - h // 2))

            elif obj['type'] in cfg.DREAM_TYPES:
                sprite = self.dream_particle_sprites.get(obj['type'])
                if sprite:
                    screen.blit(sprite, (ox - 16, oy - 16))
                else:
                    color = (128, 128, 128)
                    pygame.draw.circle(screen, color, (ox, oy), obj.get('radius', 8))

            else:
                color_map = {'toy': (255, 100, 255)}
                color = color_map.get(obj['type'], (128, 128, 128))
                pygame.draw.circle(screen, color, (ox, oy), obj.get('radius', 8))

        # Маркеры старта и финиша
        pygame.draw.circle(screen, (50, 50, 255), self.start, 10, 2)
        pygame.draw.circle(screen, (50, 255, 50), self.finish, 10, 2)

    def remove_object_at(self, x: int, y: int, radius: int = cfg.ERASER_RADIUS) -> None:
        """
        Удаляет объекты в радиусе клика, защищая критические элементы.

        Args:
            x: Координата X центра удаления.
            y: Координата Y центра удаления.
            radius: Радиус области удаления.
        """
        protected_types = {'spike', 'toy', 'start', 'finish'} | set(cfg.DREAM_TYPES)
        to_remove = [
            i for i, obj in enumerate(self.objects)
            if ((obj['x'] - x) ** 2 + (obj['y'] - y) ** 2) <= radius ** 2 and obj.get('type') not in protected_types]

        for i in reversed(to_remove):
            obj = self.objects[i]
            if obj['type'] == 'platform':
                self.placed_platforms = max(0, self.placed_platforms - 1)
            elif obj['type'] == 'ladder':
                self.placed_ladders = max(0, self.placed_ladders - 1)
            del self.objects[i]

    def is_walkable_pixel(self, px: int, py: int) -> bool:
        """
        Проверяет проходимость конкретной точки в пиксельных координатах.

        Args:
            px: Координата X в пикселях.
            py: Координата Y в пикселях.
        Returns:
            True, если клетка является полом (0), иначе False.
        """
        grid_x = int(px // self.cell_size)
        grid_y = int(py // self.cell_size)

        rows = len(self.grid)
        cols = len(self.grid[0]) if rows > 0 else 0

        if not (0 <= grid_y < rows and 0 <= grid_x < cols):
            return False

        return self.grid[grid_y][grid_x] == 0
