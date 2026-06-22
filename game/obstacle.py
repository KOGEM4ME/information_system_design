import pygame

COLUMN_WIDTH = 120


class Obstacle:
    HEIGHT = 40
    COLOR = (220, 50, 50)

    def __init__(self, col: int, speed: float) -> None:
        self.col = col
        self.x = col * COLUMN_WIDTH + 5
        self.y = float(-self.HEIGHT)
        self.speed = speed

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, int(self.y), COLUMN_WIDTH - 10, self.HEIGHT)

    def update(self, dt: float) -> None:
        self.y += self.speed * dt

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.COLOR, self.rect, border_radius=4)

    def is_off_screen(self, screen_height: int) -> bool:
        return self.y > screen_height
