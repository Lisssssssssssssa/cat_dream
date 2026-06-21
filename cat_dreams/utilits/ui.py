# utils/ui.py
import pygame
from typing import Tuple


def get_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Безопасный расчет расстояния."""
    return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5


def draw_button(
    screen: pygame.Surface, 
    text: str, 
    rect: pygame.Rect, 
    font: pygame.font.Font, 
    bg_color: Tuple[int, int, int], 
    border_color: Tuple[int, int, int], 
    text_color: Tuple[int, int, int]
) -> None:
    """Стандартная кнопка с текстом."""
    pygame.draw.rect(screen, bg_color, rect, border_radius=8)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=8)
    txt_surf = font.render(text, True, text_color)
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)


def load_scaled_image(path: str, size: Tuple[int, int]) -> pygame.Surface:
    """Безопасная загрузка и масштабирование изображения."""
    surf = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(surf, size)
