import pygame
import random
from requests import Request


class Client:
    def __init__(self, problem: str, request: Request, position: tuple[int, int], sprite_override=None):
        self.problem = problem
        self.request = request
        self.x, self.y = position
        self.width = 450
        self.height = 600
        self.sprite = sprite_override
        self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))

    def draw(self, screen):
        draw_x = self.x - self.width // 2
        screen.blit(self.sprite, (draw_x, self.y))

    def get_rect(self):
        draw_x = self.x - self.width // 2
        return pygame.Rect(draw_x, self.y, self.width, self.height)
