import pygame
import config as cfg
from hub import Hub
from levels.level import Level
from levels.validator import LevelValidator
from ui.toolbar import Toolbar


def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption("Cat_dreams")

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
                    level = Level()
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

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    clicked_toolbar = toolbar.handle_event(event)

                    if not clicked_toolbar and level:
                        obj_type = toolbar.get_selected_type()
                        if obj_type == "eraser":
                            level.remove_object_at(mouse_pos[0], mouse_pos[1], radius=30)
                            print("🗑️ Объект удален")
                        else:
                            level.add_object(obj_type, mouse_pos[0], mouse_pos[1])
                            print(f"➕ Добавлен: {obj_type}")

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    if level:
                        mouse_pos = pygame.mouse.get_pos()
                        level.remove_object_at(mouse_pos[0], mouse_pos[1], radius=30)
                        print("️ Объект удален (ПКМ)")

        screen.fill(cfg.LIGHT_BLUE)

        if current_state == 'HUB':
            hub.draw(screen)

        elif current_state == 'BUILDING' and level:
            level.draw(screen)
            toolbar.draw(screen)

            # Подсказка на экране
            font = pygame.font.Font(None, 32)
            hint_text = font.render('W - Проверить | ESC - Назад', True, cfg.BLACK)
            screen.blit(hint_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
