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
        self.rooms: List[Tuple[int, int, int, int]] = []
        self.placed_platforms = 0
        self.max_platforms = 5
        self.placed_ladders = 0
        self.max_ladders = 10
        self.collected_types = set()

        bg_path = os.path.join(cfg.ASSETS_PATH, 'backgrounds', 'dream_bg.png')
        self.bg_surface = pygame.image.load(bg_path).convert_alpha()
        self.bg_surface.set_alpha(60)
        self.bg_surface = pygame.transform.scale(self.bg_surface, (cfg.SCREEN_WIDTH * 2, cfg.SCREEN_HEIGHT))

        plat_path = os.path.join(cfg.ASSETS_PATH, 'sprites', 'platform.png')
        self.platform_sprite = pygame.image.load(plat_path).convert_alpha()
        self.platform_sprite = pygame.transform.scale(self.platform_sprite, (self.cell_size * 3, self.cell_size))

        ladder_path = os.path.join(cfg.ASSETS_PATH, 'sprites', 'ladder.png')
        self.ladder_sprite = pygame.image.load(ladder_path).convert_alpha()
        self.ladder_sprite = pygame.transform.scale(self.ladder_sprite, (self.cell_size, self.cell_size * 3))

        self.dream_particle_sprites = {}
        for typ, filename in cfg.DREAM_TYPE_TO_SPRITE.items():
            path = os.path.join(cfg.ASSETS_PATH, 'sprites', f'{filename}.png')

            spr = pygame.image.load(path).convert_alpha()
            spr = pygame.transform.scale(spr, (32, 32))
            self.dream_particle_sprites[typ] = spr

    def generate(self, max_depth: int = 4):
        print(f"Начинаю генерацию BSP (depth={max_depth}, cell_size={self.cell_size})...")
        self.grid, self.rooms = generate_bsp_grid(
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

        start_room = None
        finish_room = None
        for room in self.rooms:
            rx, ry, rw, rh = room
            # Проверим, находится ли start в этой комнате
            if (self.start[0] // self.cell_size >= rx and
                self.start[0] // self.cell_size < rx + rw and
                self.start[1] // self.cell_size >= ry and
                self.start[1] // self.cell_size < ry + rh):
                start_room = room

            if (self.finish[0] // self.cell_size >= rx and
                self.finish[0] // self.cell_size < rx + rw and
                self.finish[1] // self.cell_size >= ry and
                self.finish[1] // self.cell_size < ry + rh):
                finish_room = room
        corridor_cells = []
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == 0:
                    # Проверяем, не в комнате ли эта клетка
                    in_room = any(
                        rx <= x < rx + rw and ry <= y < ry + rh
                        for rx, ry, rw, rh in self.rooms
                    )
                    if not in_room:
                        corridor_cells.append((x, y))

        # Выбираем 3 случайные клетки из коридоров
        if len(corridor_cells) >= 3:
            toy_cells = random.sample(corridor_cells, 3)
        else:
            toy_cells = corridor_cells[:]

        # Ставим игрушки в коридорах
        for gx, gy in toy_cells:
            cx = gx * self.cell_size + self.cell_size // 2
            cy = gy * self.cell_size + self.cell_size // 2
            self.objects.append({
                'type': 'toy',
                'x': cx,
                'y': cy,
                'radius': 5
            })
        available_rooms = [r for r in self.rooms if r != start_room and r != finish_room]

        if len(available_rooms) >= 6:
            selected_rooms = random.sample(available_rooms, 6)
        else:
            selected_rooms = available_rooms[:]

        # Перемешиваем типы, чтобы не было порядка
        random.shuffle(cfg.DREAM_TYPES)

        for i, room in enumerate(selected_rooms):
            typ = cfg.DREAM_TYPES[i]
            rx, ry, rw, rh = room
            cx = (rx + rw // 2) * self.cell_size + self.cell_size // 2
            cy = (ry + rh // 2) * self.cell_size + self.cell_size // 2
            self.objects.append({
                'type': typ,
                'x': cx,
                'y': cy,
                'radius': 8
            })

    print(f"Генерация завершена Найдено клеток пола: ")

    def add_object(self, obj_type: str, x: int, y: int):
        grid_x, grid_y = int(x // self.cell_size), int(y // self.cell_size)

        if obj_type == "platform":
            if self.placed_platforms >= self.max_platforms:
                print("❌ Нельзя поставить больше платформ!")
                return
                # Горизонтальная платформа: 3 клетки в ширину, 1 в высоту
            elif obj_type == "platform":
                if self.placed_platforms >= self.max_platforms:
                    print("❌ Нельзя поставить больше платформ!")
                    return

                # Одна платформа: 3 клетки в ширину, 1 в высоту
                self.objects.append({
                    'type': 'platform',
                    'x': grid_x * self.cell_size + self.cell_size // 2,  # центр первой клетки
                    'y': grid_y * self.cell_size + self.cell_size // 2,
                    'width': self.cell_size * 3,
                    'height': self.cell_size
                })
                self.placed_platforms += 1  # 🔥 Увеличиваем счётчик

        elif obj_type == "ladder":
            if self.placed_ladders >= self.max_ladders:
                print("❌ Нельзя поставить больше лестниц!")
                return
            # Одна лестница: 1 клетка в ширину, 3 в высоту
            self.objects.append({
                'type': 'ladder',
                'x': grid_x * self.cell_size + self.cell_size // 2,
                'y': grid_y * self.cell_size + self.cell_size // 2,
                'width': self.cell_size,
                'height': self.cell_size * 3
            })
            self.placed_ladders += 1  # 🔥 Увеличиваем счётчик

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
            # Рисуем платформы и лестницы как спрайты
            if obj['type'] == 'platform':
                if self.platform_sprite:
                    rect = pygame.Rect(
                        obj['x'] - obj.get('width', self.cell_size * 3) // 2 - camera_offset[0],
                        obj['y'] - obj.get('height', self.cell_size) // 2 - camera_offset[1],
                        obj.get('width', self.cell_size * 3),
                        obj.get('height', self.cell_size)
                    )
                    screen.blit(self.platform_sprite, rect.topleft)
                else:
                    pygame.draw.rect(screen, (100, 100, 150), (
                        obj['x'] - obj.get('width', self.cell_size * 3) // 2 - camera_offset[0],
                        obj['y'] - obj.get('height', self.cell_size) // 2 - camera_offset[1],
                        obj.get('width', self.cell_size * 3),
                        obj.get('height', self.cell_size)
                    ))
                continue

            elif obj['type'] == 'ladder':
                if self.ladder_sprite:
                    rect = pygame.Rect(
                        obj['x'] - obj.get('width', self.cell_size) // 2 - camera_offset[0],
                        obj['y'] - obj.get('height', self.cell_size * 3) // 2 - camera_offset[1],
                        obj.get('width', self.cell_size),
                        obj.get('height', self.cell_size * 3)
                    )
                    screen.blit(self.ladder_sprite, rect.topleft)
                else:
                    pygame.draw.rect(screen, (80, 80, 120), (
                        obj['x'] - obj.get('width', self.cell_size) // 2 - camera_offset[0],
                        obj['y'] - obj.get('height', self.cell_size * 3) // 2 - camera_offset[1],
                        obj.get('width', self.cell_size),
                        obj.get('height', self.cell_size * 3)
                    ))
                continue
            # Определяем цвет
            elif obj['type'] in cfg.DREAM_TYPES:
                # 🔥 Берём спрайт по ключу (а не по индексу)
                sprite = self.dream_particle_sprites.get(obj['type'])
                if sprite:
                    rect = pygame.Rect(
                        obj['x'] - 16 - camera_offset[0],  # 32px → центр = x-16
                        obj['y'] - 16 - camera_offset[1],
                        32, 32
                    )
                    screen.blit(sprite, rect.topleft)
                else:
                    # fallback: круг
                    color = cfg.TYPE_COLORS.get(obj['type'], (128, 128, 128))
                    radius = obj.get('radius', 8)
                    pygame.draw.circle(screen, color,
                                       (obj['x'] - camera_offset[0], obj['y'] - camera_offset[1]),
                                       radius)
                continue
            else:
                color = {
                    'enemy': (255, 50, 50),
                    'finish': (50, 255, 50),
                    'start': (50, 50, 255),
                    'weapon': (255, 255, 50),
                    'object': (255, 165, 0),
                    'toy': (255, 100, 255),  # ярко-розовый для игрушки
                }.get(obj['type'], (128, 128, 128))

            radius = obj.get('radius', 8)
            pygame.draw.circle(screen, color,
                               (obj['x'] - camera_offset[0], obj['y'] - camera_offset[1]),
                               radius)

        # Старт и финиш
        pygame.draw.circle(screen, (50, 50, 255),
                           (self.start[0] - camera_offset[0], self.start[1] - camera_offset[1]),
                           10, 2)
        pygame.draw.circle(screen, (50, 255, 50),
                           (self.finish[0] - camera_offset[0], self.finish[1] - camera_offset[1]),
                           10, 2)

    def remove_object_at(self, x: int, y: int, radius: int = 20):
        protected_types = {'spike', 'toy', 'start', 'finish'}
        to_remove = []
        for i, obj in enumerate(self.objects):
            if ((obj['x'] - x) ** 2 + (obj['y'] - y) ** 2) <= radius ** 2 and obj.get('type') not in protected_types:
                to_remove.append(i)

        # Удаляем в обратном порядке, чтобы не сломать индексы
        for i in reversed(to_remove):
            obj = self.objects[i]
            if obj['type'] == 'platform':
                self.placed_platforms = max(0, self.placed_platforms - 1)
            elif obj['type'] == 'ladder':
                self.placed_ladders = max(0, self.placed_ladders - 1)
            del self.objects[i]

    def is_walkable_pixel(self, px: int, py: int) -> bool:
        """Проверяет, находится ли пиксель (px, py) на полу (не на стене)."""
        # Переводим пиксельные координаты в координаты сетки
        grid_x = int(px // self.cell_size)
        grid_y = int(py // self.cell_size)

        # Проверяем границы
        if not (0 <= grid_y < len(self.grid)) or not (0 <= grid_x < len(self.grid[0])):
            return False

        return self.grid[grid_y][grid_x] == 0
