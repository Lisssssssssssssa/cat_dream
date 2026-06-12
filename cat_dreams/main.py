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
            # Проверяем, нажата ли E и нет ли задержки
            if keys[pygame.K_e]:
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
                    current_state = 'HUB'
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

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
