import config as cfg
import pygame.draw
from requests import Request


class Client:
    def __init__(self, name: str, problem: str, request: Request, position: tuple[int, int]):
        self.name = name
        self.problem = problem
        self.request = request
        self.x, self.y = position
        self.width = 40
        self.height = 40
        self.color = (200, 50, 50)

    def draw(self, screen):
        rect = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.color, rect)
        font = pygame.font.Font(None, 24)
        text_surf = font.render(self.name, True, cfg.BLACK)
        screen.blit(text_surf, (self.x, self.y - 25))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
