import pygame

COLUMN_WIDTH = 120


class Collectible:
    SIZE = 28
    COLOR = (255, 215, 0)
    POINTS = 10

    def __init__(self, col: int, speed: float) -> None:
        self.col = col
        self.x = col * COLUMN_WIDTH + (COLUMN_WIDTH - self.SIZE) // 2
        self.y = float(-self.SIZE)
        self.speed = speed

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, int(self.y), self.SIZE, self.SIZE)

    def update(self, dt: float) -> None:
        self.y += self.speed * dt

    def draw(self, screen: pygame.Surface) -> None:
        center = (self.x + self.SIZE // 2, int(self.y) + self.SIZE // 2)
        pygame.draw.circle(screen, self.COLOR, center, self.SIZE // 2)

    def is_off_screen(self, screen_height: int) -> bool:
        return self.y > screen_height
