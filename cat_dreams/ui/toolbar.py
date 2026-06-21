"""Модуль интерфейса панели инструментов для редактора уровней."""

import pygame
import config as cfg


class Toolbar:
    """
    Горизонтальная панель инструментов внизу экрана.
    Управляет выбором объектов для размещения на уровне.
    """
    def __init__(self):
        """Инициализация панели инструментов и списка доступных объектов."""
        self.tools = [
            {"name": "Ластик", "type": "eraser", "color": (100, 100, 100)},
            {"name": "Платформа", "type": "platform", "color": (100, 100, 255)},
            {"name": "Лестница", "type": "ladder", "color": (150, 100, 100)}
        ]

        self.selected_index = 0
        self.height = 80
        self.y = cfg.SCREEN_HEIGHT - self.height

        # Расчет начальной позиции для центрирования
        total_width = len(self.tools) * cfg.BTN_WIDTH + (len(self.tools) - 1) * cfg.BTN_GAP
        self.start_x = (cfg.SCREEN_WIDTH - total_width) // 2

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обрабатывает событие мыши для выбора инструмента.

        Args:
            event: Событие Pygame.

        Returns:
            True, если клик произошел по кнопке тулбара.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.tools)):
                rect = self._get_button_rect(i)
                if rect.collidepoint(event.pos):
                    self.selected_index = i
                    print(f"🛠 Выбран инструмент: {self.tools[i]['name']}")
                    return True
        return False

    def get_selected_type(self) -> str:
        """
        Возвращает тип выбранного в данный момент инструмента.

        Returns:
            Строковый идентификатор типа объекта.
        """
        return self.tools[self.selected_index]["type"]

    def _get_button_rect(self, index: int) -> pygame.Rect:
        """
        Вычисляет прямоугольник кнопки по её индексу.

        Args:
            index: Индекс инструмента в списке.

        Returns:
            pygame.Rect с координатами и размерами кнопки.
        """
        x = self.start_x + index * (cfg.BTN_WIDTH + cfg.BTN_GAP)
        y = self.y + 12
        return pygame.Rect(x, y, cfg.BTN_WIDTH, cfg.BTN_HEIGHT)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Отрисовывает панель инструментов и все кнопки.

        Args:
            screen: Поверхность экрана Pygame.
        """
        # Фон панели
        panel_rect = pygame.Rect(0, self.y, cfg.SCREEN_WIDTH, self.height)
        pygame.draw.rect(screen, cfg.PANEL_BG_COLOR, panel_rect)
        pygame.draw.line(screen, cfg.DIVIDER_COLOR, (0, self.y), (cfg.SCREEN_WIDTH, self.y), 3)

        font = pygame.font.Font(None, 26)

        for i, tool in enumerate(self.tools):
            self._draw_button(screen, tool, i, font)

    def _draw_button(self, screen: pygame.Surface, tool: dict, index: int, font: pygame.font.Font) -> None:
        """
        Отрисовывает отдельную кнопку инструмента.

        Args:
            screen: Поверхность экрана.
            tool: Словарь с данными инструмента.
            index: Индекс кнопки для определения состояния.
            font: Шрифт для текста.
        """
        rect = self._get_button_rect(index)
        is_selected = (index == self.selected_index)
        colors = cfg.SELECTED_COLORS if is_selected else cfg.DEFAULT_COLORS

        # Рисуем основу кнопки
        pygame.draw.rect(screen, colors['bg'], rect, border_radius=cfg.BTN_BORDER_RADIUS)
        pygame.draw.rect(screen, colors['border'], rect, 3, border_radius=cfg.BTN_BORDER_RADIUS)

        # Иконка цвета
        color_rect = pygame.Rect(rect.x + 12, rect.y + 17, 22, 22)
        pygame.draw.rect(screen, tool["color"], color_rect, border_radius=4)

        # Специальная иконка для ластика
        if tool['type'] == 'eraser':
            self._draw_eraser_icon(screen, color_rect)

        # Текст названия
        text_surf = font.render(tool["name"], True, colors['text'])
        text_y = rect.y + (cfg.BTN_HEIGHT - text_surf.get_height()) // 2
        screen.blit(text_surf, (rect.x + 45, text_y))

    @staticmethod
    def _draw_eraser_icon(screen: pygame.Surface, rect: pygame.Rect) -> None:
        """Рисует крестик поверх иконки ластика."""
        p1 = (rect.x + 4, rect.y + 4)
        p2 = (rect.x + 18, rect.y + 18)
        p3 = (rect.x + 18, rect.y + 4)
        p4 = (rect.x + 4, rect.y + 18)

        pygame.draw.line(screen, (255, 255, 255), p1, p2, 2)
        pygame.draw.line(screen, (255, 255, 255), p3, p4, 2)
