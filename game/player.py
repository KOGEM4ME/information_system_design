import pygame

COLUMNS = 3
COLUMN_WIDTH = 120


class Player:
    WIDTH = 60
    HEIGHT = 60
    COLOR = (0, 200, 255)

    def __init__(self, screen_height: int) -> None:
        self.col = 1  # 0=左, 1=中, 2=右
        self.y = screen_height - self.HEIGHT - 20

    @property
    def x(self) -> int:
        return self.col * COLUMN_WIDTH + (COLUMN_WIDTH - self.WIDTH) // 2

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a and self.col > 0:
                self.col -= 1
            elif event.key == pygame.K_d and self.col < COLUMNS - 1:
                self.col += 1

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.COLOR, self.rect, border_radius=8)
