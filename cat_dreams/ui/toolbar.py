import pygame
import config as cfg


class Toolbar:
    """Горизонтальная панель инструментов внизу экрана."""

    def __init__(self):
        self.tools = [
            {"name": "Враг", "type": "enemy", "color": (255, 80, 80)},
            {"name": "Оружие", "type": "weapon", "color": (255, 255, 80)},
            {"name": "Ластик", "type": "eraser", "color": (100, 100, 100)},
            {"name": "Платформа", "type": "platform", "color": (100, 100, 255)},
            {"name": "Лестница", "type": "ladder", "color": (150, 100, 100)}
        ]
        self.selected_index = 0
        self.height = 80  # Чуть выше для удобства
        self.y = cfg.SCREEN_HEIGHT - self.height
        self.btn_width = 130
        self.btn_height = 55

        # Рассчитываем общую ширину всех кнопок с отступами
        gap = 10
        total_width = len(self.tools) * self.btn_width + (len(self.tools) - 1) * gap
        self.start_x = (cfg.SCREEN_WIDTH - total_width) // 2

    def handle_event(self, event) -> bool:
        """Обрабатывает клик. Возвращает True, если клик был по тулбару."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.tools)):
                x = self.start_x + i * (self.btn_width + 10)
                rect = pygame.Rect(x, self.y + 12, self.btn_width, self.btn_height)

                if rect.collidepoint(event.pos):
                    self.selected_index = i
                    print(f"🛠 Выбран индекс {i}: {self.tools[i]['name']}")
                    return True
        return False

    def get_selected_type(self) -> str:
        return self.tools[self.selected_index]["type"]

    def draw(self, screen):
        # 1. Рисуем фон панели ПОВЕРХ всего остального
        panel_rect = pygame.Rect(0, self.y, cfg.SCREEN_WIDTH, self.height)
        pygame.draw.rect(screen, (25, 25, 35), panel_rect)

        # Линия-разделитель сверху
        pygame.draw.line(screen, (60, 60, 80), (0, self.y), (cfg.SCREEN_WIDTH, self.y), 3)

        # 2. Рисуем кнопки
        font = pygame.font.Font(None, 26)
        gap = 10

        for i, tool in enumerate(self.tools):
            x = self.start_x + i * (self.btn_width + gap)
            y = self.y + 12
            is_selected = (i == self.selected_index)

            # Цвета для выбранной и невыбранной кнопки
            if is_selected:
                bg_color = (60, 140, 220)  # Яркий синий
                border_color = (120, 220, 255)  # Светлая обводка
                text_color = (255, 255, 255)  # Белый текст
            else:
                bg_color = (45, 45, 55)  # Темно-серый
                border_color = (70, 70, 85)  # Тусклая обводка
                text_color = (180, 180, 190)  # Серый текст

            rect = pygame.Rect(x, y, self.btn_width, self.btn_height)

            # Рисуем кнопку
            pygame.draw.rect(screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=8)

            # Иконка цвета (квадратик слева)
            color_rect = pygame.Rect(rect.x + 12, rect.y + 17, 22, 22)
            pygame.draw.rect(screen, tool["color"], color_rect, border_radius=4)

            # Если это ластик, добавим ему "крестик" для наглядности
            if tool['type'] == 'eraser':
                pygame.draw.line(screen, (255, 255, 255), (color_rect.x + 4, color_rect.y + 4),
                                 (color_rect.x + 18, color_rect.y + 18), 2)
                pygame.draw.line(screen, (255, 255, 255), (color_rect.x + 18, color_rect.y + 4),
                                 (color_rect.x + 4, color_rect.y + 18), 2)

            # Текст названия
            text_surf = font.render(tool["name"], True, text_color)
            # Центрируем текст относительно оставшегося места
            text_x = rect.x + 45
            text_y = rect.y + (self.btn_height - text_surf.get_height()) // 2
            screen.blit(text_surf, (text_x, text_y))
