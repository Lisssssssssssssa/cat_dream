import pygame
import config as cfg
from hub import Hub


def main():
    pygame.init()
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
    pygame.display.set_caption("Cat_dreams")
    hub = Hub()
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            hub.handle_event(event)

        hub.update()
        hub.draw(screen)
        if not hub.dialogue_active and hub.current_request:
            print("всё круто переход")
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                hub.current_request = None
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
