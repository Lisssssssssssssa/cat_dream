import pygame
import config as cfg
from hub import Hub
from levels.level import Level
from ui.toolbar import Toolbar
from entities.player import Player


def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption("Cat_dreams")
    player = None
    camera = [0, 0]
    win_screen_active = False

    hub = Hub()
    toolbar = Toolbar()
    level = None  # Инициализируем уровень как None
    current_state = 'HUB'
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_state == 'HUB':
                hub.handle_event(event)
                hub.draw(screen)
                if (hub.current_request and not hub.dialogue_active and
                        event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                    current_state = 'BUILDING'
                    level = Level(width=cfg.SCREEN_WIDTH, height=cfg.SCREEN_HEIGHT - 80, cell_size=32)
                    level.generate(max_depth=4)
                    print("🏗️ Уровень сгенерирован!")

            elif current_state == 'BUILDING':
                # ESC - выход из конструктора
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
                            print("🗑️ Объект удален")
                        else:
                            if level.is_walkable_pixel(mouse_pos[0], mouse_pos[1]):
                                level.add_object(obj_type, mouse_pos[0], mouse_pos[1])
                                print(f"➕ Добавлен: {obj_type} в ({mouse_pos[0]}, {mouse_pos[1]})")
                            else:
                                print("⚠️ Нельзя ставить объект в стену!")

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    if level:
                        mouse_pos = pygame.mouse.get_pos()
                        level.remove_object_at(mouse_pos[0], mouse_pos[1], radius=30)
                        print("️ Объект удален (ПКМ)")

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    current_state = 'PLAYING'
                    player = Player(level.start[0], level.start[1])
                    print("🐱 Режим игры запущен!")

        screen.fill(cfg.LIGHT_BLUE)

        if current_state == 'HUB':
            hub.draw(screen)

        elif current_state == 'BUILDING' and level:
            level.draw(screen, camera_offset=(0, 0))
            toolbar.draw(screen)

            # Подсказка на экране
            font = pygame.font.Font(None, 32)
            hint_text = font.render('W - Проверить | ESC - Назад', True, cfg.BLACK)
            screen.blit(hint_text, (10, 10))

        elif current_state == 'PLAYING' and player:
            keys = pygame.key.get_pressed()
            dx = 0
            # 🔥 НОВОЕ: Обработка клавиш в режиме игры
            if keys[pygame.K_ESCAPE]:
                current_state = 'BUILDING'
                print("🔧 Вернулись в редактор.")
            elif keys[pygame.K_r]:  # например, R — рестарт
                # 🔥 Просто возвращаем игрока на старт
                player.x = float(level.start[0])
                player.y = float(level.start[1])
                player.vel_x = 0
                player.vel_y = 0
                # 🔥 Сбрасываем собранные типы сна
                level.collected_types = set()
                # 🔥 Сбрасываем cooldown
                player.e_cooldown = 0
                print("🔄 Кот возвращён к началу.")
            elif keys[pygame.K_e]:
                if player.e_cooldown == 0:
                    # Проверяем сбор
                    for obj in level.objects[:]:
                        if obj['type'] in cfg.DREAM_TYPES or obj['type'] == 'toy':
                            dist = ((player.x - obj['x']) ** 2 + (player.y - obj['y']) ** 2) ** 0.5
                            if dist < 25:
                                if obj['type'] in cfg.DREAM_TYPES:
                                    print(f"✨ Собран сон: {obj['type']}")
                                    level.collected_types.add(obj['type'])  # 🔥 ДОБАВЬ ЭТУ СТРОКУ
                                elif obj['type'] == 'toy':
                                    print("🎉 Собрана игрушка!")
                                level.objects.remove(obj)
                                player.e_cooldown = 30  # 0.5 секунды (60 FPS)
                                break
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
            on_ladder = False
            for obj in level.objects:
                if obj['type'] == 'ladder':
                    obj_left = obj['x'] - obj.get('width', level.cell_size) // 2
                    obj_right = obj['x'] + obj.get('width', level.cell_size) // 2
                    obj_top = obj['y'] - obj.get('height', level.cell_size) // 2
                    obj_bottom = obj['y'] + obj.get('height', level.cell_size) // 2

                    if (player.x + player.width > obj_left and player.x < obj_right and
                        player.y + player.height > obj_top and player.y < obj_bottom):
                        on_ladder = True
                        break

            # Управление
            if on_ladder:
                # На лестнице: можно подниматься/спускаться
                player.vel_x = dx * player.speed
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    player.vel_y = -player.speed
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    player.vel_y = player.speed
                else:
                    player.vel_y = 0  # Не держим движение по вертикали, если не нажато
            else:
                # Обычное движение
                player.move(dx)
                if keys[pygame.K_SPACE] or keys[pygame.K_UP]: player.jump()
                else: player.vel_y = min(player.vel_y, player.jump_power * -0.5)  # Не ускоряем падение

            player.update(level.grid, level.cell_size, level.objects)
            for obj in level.objects[:]:  # копия списка, чтобы не ломать при удалении
                if obj['type'] == 'toy':
                    dist = ((player.x - obj['x']) ** 2 + (player.y - obj['y']) ** 2) ** 0.5
                    if dist < 25:
                        print("🎉 Собрана игрушка!")
                        level.objects.remove(obj)
            if keys[pygame.K_SPACE] or keys[pygame.K_UP]: player.jump()
            player.update(level.grid, level.cell_size, level.objects)
            # Камера следует за игроком (центрируем)
            camera[0] = player.x - cfg.SCREEN_WIDTH // 2
            camera[1] = player.y - cfg.SCREEN_HEIGHT // 2
            # Ограничение камеры границами уровня
            camera[0] = max(0, min(camera[0], level.width - cfg.SCREEN_WIDTH))
            camera[1] = max(0, min(camera[1], level.height - cfg.SCREEN_HEIGHT))
            # --- ВАЖНО: РИСУЕМ УРОВЕНЬ С КАМЕРОЙ --
            level.draw(screen, camera_offset=camera)  # <-- Эта строка была пропущена!
            # --- РИСУЕМ ИГРОКА ПОВЕРХ УРОВНЯ ---
            player.draw(screen, camera_offset=camera)
            # Проверка победы/поражения (оставляем как есть)
            dist_to_finish = ((player.x - level.finish[0]) ** 2 + (player.y - level.finish[1]) ** 2) ** 0.5
            if dist_to_finish < 30:
                # 🔥 Проверяем, собраны ли все нужные типы сна
                required_set = set(hub.current_request.required)
                if level.collected_types == required_set:
                    print("🐱 ПОБЕДА! Все нужные сны собраны, лишних нет!")
                    win_screen_active = True
                else:
                    if not required_set.issubset(level.collected_types):
                        needed = required_set - level.collected_types
                        print(f"🔒 Не все сны собраны! Нужно: {needed}")
                    else:
                        extra = level.collected_types - required_set
                        print(f"🔒 Есть лишние сны: {extra}. Соберите только нужные!")
            for obj in level.objects[:]:  # [:] — копия, чтобы можно было удалять
                if obj['type'] == 'weapon':
                    dist = ((player.x - obj['x']) ** 2 + (player.y - obj['y']) ** 2) ** 0.5
                    if dist < 25:
                        player.pickup_weapon()
                        level.objects.remove(obj)  # подобрали — исчезло
                elif obj['type'] == 'enemy':
                    dist = ((player.x - obj['x']) ** 2 + (player.y - obj['y']) ** 2) ** 0.5
                    if dist < 25:
                        if player.attack_enemy():  # атакуем
                            level.objects.remove(obj)  # враг побеждён
                        else:
                            # поражение
                            print("💀 Кот столкнулся с врагом без оружия! Поражение!")
                            player.x, player.y = level.start
                elif obj['type'] == 'spike':
                    dist = ((player.x - obj['x']) ** 2 + (player.y - obj['y']) ** 2) ** 0.5
                    if dist < 25:
                        print("🗡️ Кот наступил на шип! Возвращается к началу!")
                        player.x = float(level.start[0])
                        player.y = float(level.start[1])
                        player.vel_x = 0
                        player.vel_y = 0

        # --- ЭКРАН ПОБЕДЫ ---
        if win_screen_active:
            # Полупрозрачный чёрный фон
            overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # (R, G, B, A=180)
            screen.blit(overlay, (0, 0))

            # Бежевый прямоугольник
            rect_width, rect_height = 400, 200
            rect_x = (cfg.SCREEN_WIDTH - rect_width) // 2
            rect_y = (cfg.SCREEN_HEIGHT - rect_height) // 2
            pygame.draw.rect(screen, (240, 230, 210), (rect_x, rect_y, rect_width, rect_height), border_radius=12)
            pygame.draw.rect(screen, (180, 160, 140), (rect_x, rect_y, rect_width, rect_height), 3, border_radius=12)

            # Надпись
            font_big = pygame.font.Font(None, 48)
            font_small = pygame.font.Font(None, 32)
            title = font_big.render("Уровень пройден!", True, (50, 30, 10))
            screen.blit(title, (rect_x + rect_width // 2 - title.get_width() // 2, rect_y + 40))

            # Кнопка "Дальше"
            btn_x = rect_x + rect_width // 2 - 80
            btn_y = rect_y + 150
            btn_w, btn_h = 160, 40
            pygame.draw.rect(screen, (100, 150, 200), (btn_x, btn_y, btn_w, btn_h), border_radius=8)
            pygame.draw.rect(screen, (60, 100, 160), (btn_x, btn_y, btn_w, btn_h), 2, border_radius=8)
            btn_text = font_small.render("Дальше", True, (255, 255, 255))
            screen.blit(btn_text, (
            btn_x + btn_w // 2 - btn_text.get_width() // 2, btn_y + btn_h // 2 - btn_text.get_height() // 2))

            # Обработка клика по кнопке
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if btn_x <= mx <= btn_x + btn_w and btn_y <= my <= btn_y + btn_h:
                    win_screen_active = False
                    current_state = 'HUB'
                    player = None
                    level = None
                    hub.generate_random_request()
                    print("🚪 Вернулись в Хаб.")
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
