import pygame
import config as cfg
import random
from entities.client import Client
import os
# Импортируем шаблоны и типы сна
from requests.examples import REQUESTS
# или cfg.DREAM_TYPES
from requests.requests import Request


class Hub:
    def __init__(self):
        self.dialogue_active = False
        self.current_client = None
        self.current_request = None

        # Загрузка спрайтов клиентов
        self.client_sprites = []
        for i in range(4):  # например, 5 разных портретов
            path = os.path.join(cfg.ASSETS_PATH, 'sprites', f'client_sprie_{i}.png')
            spr = pygame.image.load(path).convert_alpha()
            spr = pygame.transform.scale(spr, (64, 64))
            self.client_sprites.append(spr)

        self.background = pygame.image.load(os.path.join(cfg.ASSETS_PATH, 'backgrounds', 'house.png')).convert()
        if self.background.get_size() != (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT):
            self.background = pygame.transform.scale(
                self.background,
                (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
            )
        self.generate_random_request()

    def generate_random_request(self):
        """Генерирует новый случайный запрос с 2 типами сна."""
        template = random.choice(REQUESTS)
        emotions = random.sample(cfg.DREAM_TYPES, 2)  # 2 разных типа
        problem = template["problem"].format(emotion=emotions[0], emotion2=emotions[1])
        required = emotions
        self.current_request = Request(problem, required)

        # Выбираем случайный спрайт для клиента
        sprite = random.choice(self.client_sprites)
        self.current_client = Client(
            problem=problem,
            request=self.current_request,
            position=(200, cfg.SCREEN_HEIGHT - 700),
            sprite_override=sprite  # передаём спрайт
        )

    def handle_event(self, event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not self.dialogue_active:
                self.dialogue_active = True
                print(f"ТЗ: {self.current_request}")
            else:
                self.dialogue_active = False
            return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.current_client and self.current_client.get_rect().collidepoint(event.pos):
                if not self.dialogue_active:
                    self.dialogue_active = True
                    print(f"ТЗ: {self.current_request}")
                else:
                    self.dialogue_active = False
                return True
        return False

    def _draw_dialogue_box(self, screen):
        box_width = cfg.SCREEN_WIDTH - 100
        box_height = 200
        box_x, box_y = 50, cfg.SCREEN_HEIGHT - box_height - 50

        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, cfg.WHITE, box_rect)
        pygame.draw.rect(screen, cfg.BLACK, box_rect, 2)

        font = pygame.font.Font(None, 26)
        y_offset = box_y + 10

        text_surf = font.render(self.current_client.problem, True, cfg.BLACK)
        screen.blit(text_surf, (box_x + 10, y_offset))
        y_offset += 30

        text_surf = font.render("Задание: ", True, cfg.BLACK)
        screen.blit(text_surf, (box_x + 10, y_offset))
        y_offset += 25

        req_text = f"Требуется: {', '.join(self.current_client.request.required)}"
        text_surf = font.render(req_text, True, cfg.BLACK)
        screen.blit(text_surf, (box_x + 20, y_offset))

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        if self.current_client:
            self.current_client.draw(screen)
        if self.dialogue_active:
            self._draw_dialogue_box(screen)

