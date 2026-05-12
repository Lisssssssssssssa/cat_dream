import pygame
import config as cfg
from hub import Hub
from levels.level import Level


def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption("Cat_dreams")
    hub = Hub()
    current_state = 'HUB'
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_state == 'HUB':
                hub.handle_event(event)
                if hub.current_request and not hub.dialogue_active and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    current_state = 'BUILDING'
                    level = Level()
                    level.generate(max_depth=3)
            elif current_state == 'BUILDING':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = 'HUB'
        screen.fill(cfg.LIGHT_BLUE)
        if current_state == 'HUB':
            hub.draw(screen)
        elif current_state == 'BUILDING':
            if level:
                level.draw(screen)
                font = pygame.font.Font(None, 32)
                text = font.render('нажми esc чтобы вернуться', True, cfg.BLACK)
                screen.blit(text, (10, 10))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
