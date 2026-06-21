import pygame
import config as cfg
from utilits.ui import draw_button, get_distance, load_scaled_image
from hub import Hub
from levels.level import Level
from ui.toolbar import Toolbar
from entities.player import Player
import os


class GameApp:
    """
    Основной класс приложения. Управляет жизненным циклом игры,
    переключением состояний и глобальной отрисовкой.
    """
    def __init__(self):
        """Инициализация Pygame, экрана и основных компонентов."""
        pygame.init()
        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        pygame.display.set_caption("Cat dreams")

        # Компоненты игры
        self.hub = Hub()
        self.toolbar = Toolbar()
        self.clock = pygame.time.Clock()

        # Состояние
        self.current_state = 'TITLE'
        self.level = None
        self.player = None
        self.win_screen_active = False
        self.show_help_screen = False

        # Ресурсы
        title_bg_path = os.path.join(cfg.ASSETS_PATH, 'backgrounds', 'title_bg.png')
        self.title_bg = load_scaled_image(title_bg_path, (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))

    def handle_title_events(self, event: pygame.event.Event) -> None:
        """
        Обработка событий для титульного экрана.
        Args:
            event: Событие Pygame.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            # Координаты кнопки "Начать"
            btn_rect = pygame.Rect(
                cfg.SCREEN_WIDTH // 2 - 100,
                cfg.SCREEN_HEIGHT // 2 + 40,
                200, 50
            )
            if btn_rect.collidepoint(mx, my):
                self.start_game()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.start_game()

    def start_game(self) -> None:
        """Переход в состояние HUB и генерация первого запроса."""
        self.current_state = 'HUB'
        self.hub.generate_random_request()

    def handle_playing_events(self, event: pygame.event.Event) -> None:
        """
        Обработка событий во время игрового процесса.
        Args:
            event: Событие Pygame.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_state = 'BUILDING'
            elif event.key == pygame.K_r:
                self.restart_level()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hx, hy = cfg.HELP_BUTTON_POS
            if get_distance(pygame.mouse.get_pos(), (hx, hy)) <= cfg.HELP_BUTTON_RADIUS:
                self.show_help_screen = not self.show_help_screen

    def restart_level(self) -> None:
        """Мягкий перезапуск уровня без пересоздания карты."""
        if self.level and self.player:
            self.player.x, self.player.y = float(self.level.start[0]), float(self.level.start[1])
            self.player.vel_x = self.player.vel_y = 0
            self.level.collected_types = set()
            self.player.e_cooldown = 0

    def update_playing(self) -> None:
        """Обновление игровой логики: физика, сбор предметов, проверка победы."""
        if not self.player or not self.level:
            return
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])

        # Сбор снов и фрагментов
        if keys[pygame.K_e] and self.player.e_cooldown == 0:
            p_pos = (self.player.x, self.player.y)
            for obj in self.level.objects[:]:
                if get_distance(p_pos, (obj['x'], obj['y'])) < cfg.COLLECT_DISTANCE:
                    if obj['type'] in cfg.DREAM_TYPES:
                        self.level.collected_types.add(obj['type'])
                    self.level.objects.remove(obj)
                    self.player.e_cooldown = 30
                    break

        # Физика
        on_ladder = False
        for obj in self.level.objects:
            if obj['type'] == 'ladder':
                ol = obj['x'] - obj.get('width', self.level.cell_size) // 2
                or_ = obj['x'] + obj.get('width', self.level.cell_size) // 2
                ot = obj['y'] - obj.get('height', self.level.cell_size) // 2
                ob = obj['y'] + obj.get('height', self.level.cell_size) // 2
                if (self.player.x + self.player.width > ol and self.player.x < or_ and
                        self.player.y + self.player.height > ot and self.player.y < ob):
                    on_ladder = True
                    break

        if on_ladder:
            self.player.vel_x = dx * self.player.speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.vel_y = -self.player.speed
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player.vel_y = self.player.speed
            else:
                self.player.vel_y = 0
        else:
            self.player.move(dx)
            if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
                self.player.jump()
            else:
                self.player.vel_y = min(self.player.vel_y, self.player.jump_power * -0.5)

        self.player.update(self.level.grid, self.level.cell_size, self.level.objects)
        self.check_win_condition()

    def check_win_condition(self) -> None:
        """Проверка достижения финиша и выполнения условий задания."""
        dist = get_distance((self.player.x, self.player.y), self.level.finish)
        if dist < cfg.FINISH_CHECK_DISTANCE:
            req_set = set(self.hub.current_request.required)
            if self.level.collected_types == req_set:
                self.win_screen_active = True

    def draw_title(self) -> None:
        """Отрисовка титульного экрана."""
        self.screen.blit(self.title_bg, (0, 0))
        title_font = pygame.font.Font(None, 72)
        t_text = title_font.render("Cat dreams", True, cfg.WHITE)
        t_rect = t_text.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 - 60))
        self.screen.blit(t_text, t_rect)

        btn_font = pygame.font.Font(None, 40)
        btn_text = btn_font.render("Начать", True, cfg.WHITE)
        btn_w, btn_h = btn_text.get_width() + 40, btn_text.get_height() + 20
        btn_rect = pygame.Rect(cfg.SCREEN_WIDTH // 2 - btn_w // 2, cfg.SCREEN_HEIGHT // 2 + 40, btn_w, btn_h)
        draw_button(self.screen, "Начать", btn_rect, btn_font,
                    cfg.UI_COLORS['BUTTON_BG'], cfg.UI_COLORS['BUTTON_BORDER'], cfg.WHITE)

    def draw_playing_ui(self) -> None:
        """Отрисовка интерфейса во время игры (кнопка ?, статус, подсказка)."""
        # Кнопка помощи
        hx, hy = cfg.HELP_BUTTON_POS
        pygame.draw.circle(self.screen, (200, 200, 200), (hx, hy), cfg.HELP_BUTTON_RADIUS)
        pygame.draw.circle(self.screen, (100, 100, 100), (hx, hy), cfg.HELP_BUTTON_RADIUS, 2)
        f = pygame.font.Font(None, 32)
        qt = f.render("?", True, cfg.BLACK)
        self.screen.blit(qt, (hx - qt.get_width() // 2, hy - qt.get_height() // 2))

        # Статус задания
        if self.level and self.hub.current_request:
            dist_fin = get_distance((self.player.x, self.player.y), self.level.finish)
            if dist_fin < 100:
                req_set = set(self.hub.current_request.required)
                status_font = pygame.font.Font(None, 24)
                if self.level.collected_types == req_set:
                    msg, color = "Можно выходить!", cfg.UI_COLORS['STATUS_OK']
                elif not req_set.issubset(self.level.collected_types):
                    missing = req_set - self.level.collected_types
                    msg, color = f"Не хватает: {len(missing)} снов", cfg.UI_COLORS['STATUS_MISSING']
                else:
                    extra = self.level.collected_types - req_set
                    msg, color = f"Лишние сны: {len(extra)}", cfg.UI_COLORS['STATUS_EXTRA']

                surf = status_font.render(msg, True, color)
                self.screen.blit(surf, (cfg.SCREEN_WIDTH // 2 - surf.get_width() // 2, cfg.SCREEN_HEIGHT - 60))

        # Окно подсказки
        if self.show_help_screen:
            overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            hw, hh = 520, 580
            hrx = (cfg.SCREEN_WIDTH - hw) // 2
            hry = (cfg.SCREEN_HEIGHT - hh) // 2

            pygame.draw.rect(self.screen, (240, 240, 240), (hrx, hry, hw, hh), border_radius=12)
            pygame.draw.rect(self.screen, (100, 100, 100), (hrx, hry, hw, hh), 2, border_radius=12)

            ft = pygame.font.Font(None, 36)
            fn = pygame.font.Font(None, 28)
            tt = ft.render("Подсказка", True, cfg.BLACK)
            self.screen.blit(tt, (hrx + hw // 2 - tt.get_width() // 2, hry + 20))

            y_off = hry + 60
            for i, dt in enumerate(cfg.DREAM_TYPES):
                spr = None
                if self.level:
                    spr = getattr(self.level, 'dream_particle_sprites', {}).get(dt)
                if spr:
                    self.screen.blit(spr, (hrx + 20, y_off + i * 40))
                else:
                    pygame.draw.rect(self.screen, (100, 100, 100), (hrx + 20, y_off + i * 40, 32, 32))

                txt = fn.render(dt, True, cfg.BLACK)
                self.screen.blit(txt, (hrx + 60, y_off + i * 40))

            y_off += len(cfg.DREAM_TYPES) * 40 + 20
            ctrls = ["E — собрать тип сна/фрагмент сна", "ESC — в редактор", "R — рестарт", "<-> — движение",
                     "Пробел — прыжок"]
            for i, c in enumerate(ctrls):
                txt = fn.render(c, True, cfg.BLACK)
                self.screen.blit(txt, (hrx + 20, y_off + i * 25))

    def draw_win_screen(self) -> None:
        """Отрисовка экрана победы."""
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        rw, rh = 400, 200
        rx = (cfg.SCREEN_WIDTH - rw) // 2
        ry = (cfg.SCREEN_HEIGHT - rh) // 2

        pygame.draw.rect(self.screen, cfg.UI_COLORS['WIN_PANEL_BG'], (rx, ry, rw, rh), border_radius=12)
        pygame.draw.rect(self.screen, cfg.UI_COLORS['WIN_PANEL_BORDER'], (rx, ry, rw, rh), 3, border_radius=12)

        fb = pygame.font.Font(None, 48)
        fs = pygame.font.Font(None, 32)
        t = fb.render("Уровень пройден!", True, (50, 30, 10))
        self.screen.blit(t, (rx + rw // 2 - t.get_width() // 2, ry + 40))

        bx = rx + rw // 2 - 80
        by = ry + 150
        bw, bh = 160, 40
        draw_button(self.screen, "Дальше", pygame.Rect(bx, by, bw, bh), fs,
                    cfg.UI_COLORS['BUTTON_BG'], cfg.UI_COLORS['BUTTON_BORDER'], cfg.WHITE)

    def run(self) -> None:
        """Основной игровой цикл."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.current_state == 'TITLE':
                    self.handle_title_events(event)
                elif self.current_state == 'HUB':
                    self.hub.handle_event(event)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.current_state = 'BUILDING'
                        self.level = Level(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT - 80, 32)
                        self.level.generate(max_depth=4)
                elif self.current_state == 'BUILDING':
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.current_state = 'HUB'
                        self.level = None
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        clicked_toolbar = self.toolbar.handle_event(event)
                        if not clicked_toolbar and self.level:
                            obj_type = self.toolbar.get_selected_type()
                            if obj_type == "eraser":
                                self.level.remove_object_at(mouse_pos[0], mouse_pos[1])
                            else:
                                if self.level.is_walkable_pixel(mouse_pos[0], mouse_pos[1]):
                                    self.level.add_object(obj_type, mouse_pos[0], mouse_pos[1])
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                        if self.level:
                            mouse_pos = pygame.mouse.get_pos()
                            self.level.remove_object_at(mouse_pos[0], mouse_pos[1])
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                        self.current_state = 'PLAYING'
                        self.player = Player(self.level.start[0], self.level.start[1])
                elif self.current_state == 'PLAYING':
                    self.handle_playing_events(event)
                    # Клик по кнопке "Дальше" на экране победы
                    if self.win_screen_active and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        rw, rh = 400, 200
                        rx = (cfg.SCREEN_WIDTH - rw) // 2
                        ry = (cfg.SCREEN_HEIGHT - rh) // 2
                        bx = rx + rw // 2 - 80
                        by = ry + 150
                        bw, bh = 160, 40
                        if bx <= mx <= bx + bw and by <= my <= by + bh:
                            self.win_screen_active = False
                            self.current_state = 'HUB'
                            self.player = None
                            self.level = None
                            self.hub.generate_random_request()

            if self.current_state == 'PLAYING':
                self.update_playing()

            # Отрисовка
            self.screen.fill(cfg.LIGHT_BLUE)
            if self.current_state == 'TITLE':
                self.draw_title()
            elif self.current_state == 'HUB':
                self.hub.draw(self.screen)
            elif self.current_state == 'BUILDING' and self.level:
                self.level.draw(self.screen);
                self.toolbar.draw(self.screen)
            elif self.current_state == 'PLAYING' and self.player:
                self.level.draw(self.screen)
                self.player.draw(self.screen)
                self.draw_playing_ui()

            if self.win_screen_active:
                self.draw_win_screen()

            pygame.display.flip()
            self.clock.tick(cfg.FPS)
        pygame.quit()


if __name__ == "__main__":
    app = GameApp()
    app.run()
