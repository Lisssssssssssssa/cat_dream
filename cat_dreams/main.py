import pygame
import config as cfg
from hub import Hub
from levels.level import Level
from levels.validator import LevelValidator
from ui.toolbar import Toolbar
from entities.player import Player


def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption("Cat_dreams")
    player = None
    camera = [0, 0]
    current_level_report = {}

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
                    level.generate(max_depth=3)
                    print("🏗️ Уровень сгенерирован!")

            elif current_state == 'BUILDING':
                # ESC - выход из конструктора
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = 'HUB'
                    level = None

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                    if level and hub.current_request:
                        validator = LevelValidator(level.grid, level.cell_size)
                        report = validator.get_validation_report(
                            level.start,
                            level.finish,
                            level.objects,
                            hub.current_request.required
                        )
                        current_level_report = report

                        print("\n" + "=" * 50)
                        print("📋 ОТЧЕТ ВАЛИДАЦИИ:")
                        print(f"   Путь существует: {'✅' if report['path_exists'] else '❌'}")
                        print(f"   Требования ТЗ:")
                        for req, status in report['request_fulfilled'].items():
                            print(f"      - {req}: {'✅' if status else '❌'}")
                        print(f"   ИТОГ: {'✅ УРОВЕНЬ ГОТОВ' if report['is_valid'] else '❌ ЕСТЬ ОШИБКИ'}")
                        print("=" * 50 + "\n")
                    else:
                        print("⚠️ Нет уровня или ТЗ для проверки!")
                        current_level_report = {}

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
                    # Используем сохранённый отчёт!
                    if level and current_level_report.get('is_valid', False):
                        current_state = 'PLAYING'
                        player = Player(level.start[0], level.start[1])
                        print("🐱 Режим игры запущен!")
                    else:
                        print("⚠️ Уровень не прошёл валидацию! Нельзя запустить.")

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
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
            player.move(dx)
            if keys[pygame.K_SPACE] or keys[pygame.K_UP]: player.jump()
            player.update(level.grid, level.cell_size)
            # Камера следует за игроком (центрируем)
            camera[0] = player.x - cfg.SCREEN_WIDTH // 2
            camera[1] = player.y - cfg.SCREEN_HEIGHT // 2
            # Ограничение камеры границами уровня
            camera[0] = max(0, min(camera[0], level.width - cfg.SCREEN_WIDTH))
            camera[1] = max(0, min(camera[1], level.height - cfg.SCREEN_HEIGHT + 90))
            # --- ВАЖНО: РИСУЕМ УРОВЕНЬ С КАМЕРОЙ --
            level.draw(screen, camera_offset=camera)  # <-- Эта строка была пропущена!
            # --- РИСУЕМ ИГРОКА ПОВЕРХ УРОВНЯ ---
            player.draw(screen, camera_offset=camera)
            # Проверка победы/поражения (оставляем как есть)
            dist_to_finish = ((player.x - level.finish[0]) ** 2 + (player.y - level.finish[1]) ** 2) ** 0.5
            if dist_to_finish < 30:
                print("🐱 ПОБЕДА! Сон пройден!")
                current_state = 'HUB'
            for obj in level.objects:
                if obj['type'] == 'enemy':
                    dist = ((player.x - obj['x']) ** 2 + (player.y - obj['y']) ** 2) ** 0.5
                    if dist < 20:
                        print("💀 Поражение! Кот столкнулся с врагом.")
                        player.x, player.y = level.start

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
