import config as cfg
import pygame
import random
from requests import Request
import os
from typing import Tuple, List


class Client:
    CLIENT_SPRITES = [
        "assets/sprites/clients/cat_white.png",
        "assets/sprites/clients/cat_siam.png",
        "assets/sprites/clients/cat_orange.png",
        "assets/sprites/clients/cat_grey.png"
    ]

    def __init__(self, name: str, problem: str, request: Request, position: tuple[int, int]):
        self.name = name
        self.problem = problem
        self.request = request
        self.x, self.y = position
        self.width = 400
        self.height = 600

        sprite_path = random.choice(self.CLIENT_SPRITES)
        self.sprite = pygame.image.load(sprite_path).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))

    def draw(self, screen):
        draw_x = self.x - self.width // 2
        screen.blit(self.sprite, (draw_x, self.y))

    def get_rect(self):
        draw_x = self.x - self.width // 2
        return pygame.Rect(draw_x, self.y, self.width, self.height)
