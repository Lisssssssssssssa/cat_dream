import pygame
from requests.requests import Request
from typing import Tuple, Optional


class Client:
    """
    Представляет клиента в хабе. Управляет отображением портрета,
    текстом проблемы и геометрией области взаимодействия.
    """
    def __init__(
            self,
            problem: str,
            request: Request,
            position: Tuple[int, int],
            sprite_override: Optional[pygame.Surface] = None
    ):
        """
        Инициализация клиента.
        Args:
            problem: Текст проблемы или диалога.
            request: Объект запроса с требованиями.
            position: Координаты центра по X и верхней границы по Y.
            sprite_override: Готовый спрайт портрета. Если None, используется заглушка.
        """
        self.problem = problem
        self.request = request
        self.x, self.y = position

        # Размеры портрета
        self.width = 450
        self.height = 600

        # Безопасная обработка спрайта
        if sprite_override:
            self.sprite = pygame.transform.scale(sprite_override, (self.width, self.height))
        else:
            # Создаем временную заглушку, если спрайт не передан
            self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.sprite.fill((200, 180, 255, 128))

    @property
    def _draw_x(self) -> int:
        """Вычисляет координату X для отрисовки (центрирование)."""
        return self.x - self.width // 2

    def draw(self, screen: pygame.Surface) -> None:
        """
        Отрисовывает портрет клиента на экране.
        Args:
            screen: Поверхность экрана Pygame.
        """
        screen.blit(self.sprite, (self._draw_x, self.y))

    def get_rect(self) -> pygame.Rect:
        """
        Возвращает прямоугольник области взаимодействия клиента.
        Returns:
            pygame.Rect: Прямоугольник с координатами и размерами клиента.
        """
        return pygame.Rect(self._draw_x, self.y, self.width, self.height)
