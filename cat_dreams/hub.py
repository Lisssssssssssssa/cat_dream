import pygame
import config as cfg
from entities.client import Client
from requests.examples import REQUESTS


class Hub:
    def __init__(self):
        self.dialogue_active = False
        self.current_client = None
        self.current_request = None
        req = REQUESTS[0]
        self.current_client = Client(
            name="Барсик",
            problem=req.problem,
            request=req,
            position=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT - 100)
        )

        self.background = pygame.image.load("assets/backgrounds/house.png").convert()
        if self.background.get_size() != (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT):
            self.background = pygame.transform.scale(
                self.background,
                (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
            )

    def handle_event(self, event) -> bool:
        """Обрабатывает событие. Возвращает True, если событие обработано."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.dialogue_active:
                self.current_request = self.current_client.request
                self.dialogue_active = False
                print(f"ТЗ: {self.current_request}")
                return True
            else:
                self.dialogue_active = True
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.current_client and self.current_client.get_rect().collidepoint(event.pos):
                self.dialogue_active = True
                return True
        return False

    def update(self):
        pass

    def _draw_dialogue_box(self, screen):
        """Рисует диалоговое окно."""
        box_width = cfg.SCREEN_WIDTH - 100
        box_height = 200
        box_x, box_y = 50, cfg.SCREEN_HEIGHT - box_height - 50

        # Рамка
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, cfg.WHITE, box_rect)
        pygame.draw.rect(screen, cfg.BLACK, box_rect, 2)

        # Текст
        font = pygame.font.Font(None, 26)
        y_offset = box_y + 10

        # Проблема
        text_surf = font.render(f"{self.current_client.name}:", True, cfg.BLACK)
        screen.blit(text_surf, (box_x + 10, y_offset))
        y_offset += 30

        text_surf = font.render(self.current_client.problem, True, cfg.BLACK)
        screen.blit(text_surf, (box_x + 10, y_offset))
        y_offset += 30

        # ТЗ
        text_surf = font.render("Задание:", True, cfg.BLACK)
        screen.blit(text_surf, (box_x + 10, y_offset))
        y_offset += 25

        # Требуется
        req_text = f"Требуется: {', '.join(self.current_client.request.required)}"
        text_surf = font.render(req_text, True, cfg.BLACK)
        screen.blit(text_surf, (box_x + 20, y_offset))
        y_offset += 25

        # Запрещено
        if self.current_client.request.forbidden:
            forb_text = f"Запрещено: {', '.join(self.current_client.request.forbidden)}"
            text_surf = font.render(forb_text, True, cfg.BLACK)
            screen.blit(text_surf, (box_x + 20, y_offset))

    def draw(self, screen):

        screen.blit(self.background, (0, 0))
        self.current_client.draw(screen)
        self._draw_dialogue_box(screen)
