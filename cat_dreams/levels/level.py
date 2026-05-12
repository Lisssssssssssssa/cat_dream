from typing import List, Tuple, Dict, Optional
from .bsp_generator import BSPNode, generate_bsp
import pygame
import config as cfg


class Level:
    def __init__(self, width: int = cfg.SCREEN_WIDTH, height: int = cfg.SCREEN_HEIGHT // 2):
        self.width = width
        self.height = height
        self.rooms = []
        self.objects = []
        self.start = (100, 100)
        self.finish = (width - 100, height - 100)

    def generate(self, max_depth: int = 4):
        self.rooms = generate_bsp(self.width, self.height, max_depth=max_depth)
        if self.rooms:
            r1 = self.rooms[0]
            if len(self.rooms) > 1:
                r2 = self.rooms[-1]
            else:
                r2 = r1
            self.start = (r1.x + r1.width // 2, r1.y + r1.height // 2)
            self.finish = (r2.x + r2.width // 2, r2.y + r2.height // 2)

    def add_object(self, obj_type: str, x: int, y: int):
        """Добавляет объект в уровень."""
        self.objects.append({
            'type': obj_type,
            'x': x,
            'y': y
        })

    def draw(self, screen):
        """Отрисовка структуры (комнаты как прямоугольники)."""
        for room in self.rooms:
            rect = pygame.Rect(room.x, room.y, room.width, room.height)
            pygame.draw.rect(screen, (100, 100, 200, 100), rect, 1)  # полупрозрачные контуры

        # Отрисовка объектов
        for obj in self.objects:
            color = {
                'enemy': (255, 50, 50),
                'finish': (50, 255, 50),
                'player_start': (50, 50, 255),
                'object': (255, 255, 50)
            }.get(obj['type'], (128, 128, 128))
            pygame.draw.circle(screen, color, (obj['x'], obj['y']), 12)

        # Старт и финиш
        pygame.draw.circle(screen, (50, 50, 255), self.start, 16, 2)
        pygame.draw.circle(screen, (50, 255, 50), self.finish, 16, 2)
