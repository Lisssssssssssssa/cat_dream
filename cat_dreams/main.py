import pygame
import config as cfg
from hub import Hub
from levels.level import Level
from ui.toolbar import Toolbar
from entities.player import Player
import os


def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption("Cat_dreams")

    player = None
    win_screen_active = False
    show_help_screen = False

    hub = Hub()
    toolbar = Toolbar()
    level = None
    current_state = 'TITLE'
    clock = pygame.time.Clock()

    title_bg_path = os.path.join(cfg.ASSETS_PATH, 'backgrounds', 'title_bg.png')
    title_background = pygame.image.load(title_bg_path).convert()
    if title_background.get_size() != (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT):
        title_background = pygame.transform.scale(title_background, (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))

    running = True
    while running:
        # --- ОБРАБОТКА СОБЫТИЙ ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Глобальная кнопка подсказки (?)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                help_r = 20
                hx = 30
                hy = cfg.SCREEN_HEIGHT - 30
                if ((mx - hx) ** 2 + (my - hy) ** 2) ** 0.5 <= help_r:
                    show_help_screen = not show_help_screen

            # --- ЛОГИКА ДЛЯ TITLE ---
            if current_state == 'TITLE':
                # Сначала определяем координаты кнопки, чтобы проверить клик
                btn_font = pygame.font.Font(None, 40)
                btn_text_surf = btn_font.render("Начать", True, (255, 255, 255))
                b_w = btn_text_surf.get_width() + 40
                b_h = btn_text_surf.get_height() + 20
                b_x = cfg.SCREEN_WIDTH // 2 - b_w // 2
                b_y = cfg.SCREEN_HEIGHT // 2 + 40

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    if b_x <= mx <= b_x + b_w and b_y <= my <= b_y + b_h:
                        current_state = 'HUB'
                        hub.generate_random_request()

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    current_state = 'HUB'
                    hub.generate_random_request()

            # --- ЛОГИКА ДЛЯ HUB ---
            elif current_state == 'HUB':
                hub.handle_event(event)
                if (hub.current_request and
                        event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                    current_state = 'BUILDING'
                    level = Level(width=cfg.SCREEN_WIDTH, height=cfg.SCREEN_HEIGHT - 80, cell_size=32)
                    level.generate(max_depth=4)

            # --- ЛОГИКА ДЛЯ BUILDING ---
            elif current_state == 'BUILDING':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = 'HUB'
                    level = None
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    clicked_toolbar = toolbar.handle_event(event)
                    if not clicked_toolbar and level:
                        obj_type = toolbar.get_selected_type()
                        if obj_type == "eraser":
                            level.remove_object_at(mouse_pos[0], mouse_pos[1], radius=30)
                        else:
                            if level.is_walkable_pixel(mouse_pos[0], mouse_pos[1]):
                                level.add_object(obj_type, mouse_pos[0], mouse_pos[1])
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    if level:
                        mouse_pos = pygame.mouse.get_pos()
                        level.remove_object_at(mouse_pos[0], mouse_pos[1], radius=30)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    current_state = 'PLAYING'
                    player = Player(level.start[0], level.start[1])

        # --- ОТРИСОВКА ---

        # 1. ТИТУЛЬНЫЙ ЭКРАН
        if current_state == 'TITLE':
            screen.blit(title_background, (0, 0))

            title_font = pygame.font.Font(None, 72)
            t_text = title_font.render("Cat dreams", True, (255, 255, 255))
            t_rect = t_text.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 - 60))
            screen.blit(t_text, t_rect)

            btn_font = pygame.font.Font(None, 40)
            btn_text = btn_font.render("Начать", True, (255, 255, 255))
            btn_w, btn_h = btn_text.get_width() + 40, btn_text.get_height() + 20
            btn_x = cfg.SCREEN_WIDTH // 2 - btn_w // 2
            btn_y = cfg.SCREEN_HEIGHT // 2 + 40

            pygame.draw.rect(screen, (100, 150, 200), (btn_x, btn_y, btn_w, btn_h), border_radius=8)
            pygame.draw.rect(screen, (60, 100, 160), (btn_x, btn_y, btn_w, btn_h), 2, border_radius=8)
            screen.blit(btn_text, (btn_x + btn_w // 2 - btn_text.get_width() // 2,
                                   btn_y + btn_h // 2 - btn_text.get_height() // 2))

        # 2. ХАБ (убрано дублирование из цикла событий)
        elif current_state == 'HUB':
            hub.draw(screen)

        # 3. РЕДАКТОР
        elif current_state == 'BUILDING' and level:
            level.draw(screen)
            toolbar.draw(screen)

        # 4. ИГРА
        elif current_state == 'PLAYING' and player:
            keys = pygame.key.get_pressed()
            dx = 0

            # Управление в игре
            if keys[pygame.K_ESCAPE]:
                current_state = 'BUILDING'
            elif keys[pygame.K_r]:
                player.x = float(level.start[0])
                player.y = float(level.start[1])
                player.vel_x = 0
                player.vel_y = 0
                level.collected_types = set()
                player.e_cooldown = 0
            elif keys[pygame.K_e] and player.e_cooldown == 0:
                for obj in level.objects[:]:
                    if obj['type'] in cfg.DREAM_TYPES or obj['type'] == 'toy':
                        dist = ((player.x - obj['x']) ** 2 + (player.y - obj['y']) ** 2) ** 0.5
                        if dist < 25:
                            if obj['type'] in cfg.DREAM_TYPES:
                                level.collected_types.add(obj['type'])
                            level.objects.remove(obj)
                            player.e_cooldown = 30
                            break

            # Движение
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1

            on_ladder = False
            for obj in level.objects:
                if obj['type'] == 'ladder':
                    ol = obj['x'] - obj.get('width', level.cell_size) // 2
                    or_ = obj['x'] + obj.get('width', level.cell_size) // 2
                    ot = obj['y'] - obj.get('height', level.cell_size) // 2
                    ob = obj['y'] + obj.get('height', level.cell_size) // 2
                    if (player.x + player.width > ol and player.x < or_ and
                            player.y + player.height > ot and player.y < ob):
                        on_ladder = True
                        break

            if on_ladder:
                player.vel_x = dx * player.speed
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    player.vel_y = -player.speed
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    player.vel_y = player.speed
                else:
                    player.vel_y = 0
            else:
                player.move(dx)
                if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
                    player.jump()
                else:
                    player.vel_y = min(player.vel_y, player.jump_power * -0.5)

            player.update(level.grid, level.cell_size, level.objects)

            level.draw(screen)
            player.draw(screen)

            dist_fin = ((player.x - level.finish[0]) ** 2 + (player.y - level.finish[1]) ** 2) ** 0.5
            if dist_fin < 100:  # Показываем, когда кот подходит к финишу
                req_set = set(hub.current_request.required)
                status_font = pygame.font.Font(None, 24)

                if level.collected_types == req_set:
                    msg = "Можно выходить!"
                    color = (100, 255, 100)
                elif not req_set.issubset(level.collected_types):
                    missing = req_set - level.collected_types
                    msg = f"Не хватает: {len(missing)} снов"
                    color = (255, 100, 100)
                else:
                    extra = level.collected_types - req_set
                    msg = f"Лишние сны: {len(extra)}"
                    color = (255, 200, 100)

                surf = status_font.render(msg, True, color)
                screen.blit(surf, (cfg.SCREEN_WIDTH // 2 - surf.get_width() // 2, cfg.SCREEN_HEIGHT - 60))

            # Кнопка подсказки (?)
            hr = 20
            hx = 30
            hy = cfg.SCREEN_HEIGHT - 30
            pygame.draw.circle(screen, (200, 200, 200), (hx, hy), hr)
            pygame.draw.circle(screen, (100, 100, 100), (hx, hy), hr, 2)
            f = pygame.font.Font(None, 32)
            qt = f.render("?", True, (0, 0, 0))
            screen.blit(qt, (hx - qt.get_width() // 2, hy - qt.get_height() // 2))

            # Окно подсказки
            if show_help_screen:
                overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))

                hw, hh = 520, 580
                hrx = (cfg.SCREEN_WIDTH - hw) // 2
                hry = (cfg.SCREEN_HEIGHT - hh) // 2

                pygame.draw.rect(screen, (240, 240, 240), (hrx, hry, hw, hh), border_radius=12)
                pygame.draw.rect(screen, (100, 100, 100), (hrx, hry, hw, hh), 2, border_radius=12)

                ft = pygame.font.Font(None, 36)
                fn = pygame.font.Font(None, 28)
                tt = ft.render("Подсказка", True, (0, 0, 0))
                screen.blit(tt, (hrx + hw // 2 - tt.get_width() // 2, hry + 20))

                y_off = hry + 60
                for i, dt in enumerate(cfg.DREAM_TYPES):
                    spr = getattr(level, 'dream_particle_sprites', {}).get(dt) if hasattr(level,
                                                                                          'dream_particle_sprites') else None
                    if spr:
                        screen.blit(spr, (hrx + 20, y_off + i * 40))
                    else:
                        pygame.draw.rect(screen, (100, 100, 100), (hrx + 20, y_off + i * 40, 32, 32))

                    txt = fn.render(dt, True, (0, 0, 0))
                    screen.blit(txt, (hrx + 60, y_off + i * 40))

                y_off += len(cfg.DREAM_TYPES) * 40 + 20
                ctrls = ["E — собрать сон/игрушку", "ESC — в редактор", "R — рестарт", "<-> — движение",
                         "Пробел — прыжок"]
                for i, c in enumerate(ctrls):
                    txt = fn.render(c, True, (0, 0, 0))
                    screen.blit(txt, (hrx + 20, y_off + i * 25))

            # Проверка победы
            dist_fin = ((player.x - level.finish[0]) ** 2 + (player.y - level.finish[1]) ** 2) ** 0.5
            if dist_fin < 30:
                req_set = set(hub.current_request.required)
                if level.collected_types == req_set:
                    win_screen_active = True

        # --- ЭКРАН ПОБЕДЫ ---
        if win_screen_active:
            overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            rw, rh = 400, 200
            rx = (cfg.SCREEN_WIDTH - rw) // 2
            ry = (cfg.SCREEN_HEIGHT - rh) // 2

            pygame.draw.rect(screen, (240, 230, 210), (rx, ry, rw, rh), border_radius=12)
            pygame.draw.rect(screen, (180, 160, 140), (rx, ry, rw, rh), 3, border_radius=12)

            fb = pygame.font.Font(None, 48)
            fs = pygame.font.Font(None, 32)
            t = fb.render("Уровень пройден!", True, (50, 30, 10))
            screen.blit(t, (rx + rw // 2 - t.get_width() // 2, ry + 40))

            bx = rx + rw // 2 - 80
            by = ry + 150
            bw, bh = 160, 40
            pygame.draw.rect(screen, (100, 150, 200), (bx, by, bw, bh), border_radius=8)
            bt = fs.render("Дальше", True, (255, 255, 255))
            screen.blit(bt, (bx + bw // 2 - bt.get_width() // 2, by + bh // 2 - bt.get_height() // 2))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if bx <= mx <= bx + bw and by <= my <= by + bh:
                    win_screen_active = False
                    current_state = 'HUB'
                    player = None
                    level = None
                    hub.generate_random_request()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
