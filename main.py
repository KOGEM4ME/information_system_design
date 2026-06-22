import sys

import pygame

from game.world import World

SCREEN_WIDTH = 360
SCREEN_HEIGHT = 640
FPS = 60


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Vertical Dash")
    clock = pygame.time.Clock()

    world = World(screen)

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            world.handle_event(event)

        world.update(dt)
        world.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
