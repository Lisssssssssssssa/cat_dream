import os
import random
import pygame
import config as cfg
from utilits.ui import load_scaled_image
from entities.client import Client
from requests.examples import REQUESTS
from requests.requests import Request


class Hub:
    """
    Управляет состоянием хаба: генерацией случайных клиентов, 
    обработкой диалогов и отрисовкой интерфейса общения.
    """

    def __init__(self):
        """Инициализация хаба, загрузка фона и первого клиента."""
        self.dialogue_active = False
        self.current_client: Client | None = None
        self.current_request: Request | None = None

        # Загрузка спрайтов клиентов с защитой от ошибок
        self.client_sprites = []
        for i in range(4):
            path = os.path.join(cfg.ASSETS_PATH, 'sprites', f'client_sprie_{i}.png')
            sprite = load_scaled_image(path, (64, 64))
            self.client_sprites.append(sprite)

        # Загрузка фона хаба
        bg_path = os.path.join(cfg.ASSETS_PATH, 'backgrounds', 'house.png')
        self.background = load_scaled_image(bg_path, (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))

        # Генерируем первого клиента при старте
        self.generate_random_request()

    def generate_random_request(self) -> None:
        """
        Создает нового клиента со случайным заданием на два типа сна.
        Обновляет текущий запрос и визуальное представление клиента.
        """
        template = random.choice(REQUESTS)
        emotions = random.sample(cfg.DREAM_TYPES, 2)

        problem_text = template["problem"].format(
            emotion=emotions[0],
            emotion2=emotions[1]
        )

        self.current_request = Request(
            problem=problem_text,
            required=emotions
        )

        # Выбираем случайный спрайт из загруженных
        sprite = random.choice(self.client_sprites) if self.client_sprites else None

        self.current_client = Client(
            problem=problem_text,
            request=self.current_request,
            position=(200, cfg.SCREEN_HEIGHT - 700),
            sprite_override=sprite
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обрабатывает события ввода для открытия/закрытия диалога.

        Args:
            event: Событие Pygame.

        Returns:
            True, если событие было обработано как взаимодействие с клиентом.
        """
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._toggle_dialogue()
            return True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.current_client and self.current_client.get_rect().collidepoint(event.pos):
                self._toggle_dialogue()
                return True

        return False

    def _toggle_dialogue(self) -> None:
        """Переключает состояние активности диалогового окна."""
        self.dialogue_active = not self.dialogue_active

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int, color: tuple) -> list[pygame.Surface]:
        """Разбивает текст на строки, чтобы он помещался в max_width."""
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            # Проверяем, поместится ли слово в текущую строку
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                # Если не поместилось, сохраняем текущую строку и начинаем новую
                if current_line:
                    lines.append(font.render(current_line, True, color))
                current_line = word

        # Не забываем добавить последнюю строку
        if current_line:
            lines.append(font.render(current_line, True, color))
        return lines

    def draw_dialogue_box(self, screen: pygame.Surface) -> None:
        """
        Отрисовывает окно диалога с текстом проблемы клиента.
        Args:
            screen: Поверхность экрана для отрисовки.
        """
        box_width = cfg.SCREEN_WIDTH - 100
        box_height = 200
        box_x, box_y = 50, cfg.SCREEN_HEIGHT - box_height - 50

        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, cfg.WHITE, box_rect)
        pygame.draw.rect(screen, cfg.BLACK, box_rect, 2)

        font = pygame.font.Font(None, 26)
        y_offset = box_y + 10

        # Отступы внутри окна
        padding_x = 20
        available_width = box_width - (padding_x * 2)
        # 2. Рисуем проблему с переносом строк
        problem_lines = self._wrap_text(
            self.current_client.problem,
            font,
            available_width,
            cfg.BLACK
        )
        for line_surf in problem_lines:
            screen.blit(line_surf, (box_x + padding_x, y_offset))
            y_offset += 28  # Межстрочный интервал

    def draw(self, screen: pygame.Surface) -> None:
        """
        Полная отрисовка состояния хаба.
        Args:
            screen: Поверхность экрана для отрисовки.
        """
        screen.blit(self.background, (0, 0))
        if self.current_client:
            self.current_client.draw(screen)
        if self.dialogue_active:
            self.draw_dialogue_box(screen)
            