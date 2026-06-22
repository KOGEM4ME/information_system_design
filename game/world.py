import random

import pygame

from game.collectible import Collectible
from game.obstacle import Obstacle
from game.player import Player

COLUMNS = 3
COLUMN_WIDTH = 120
SCREEN_WIDTH = 360
SCREEN_HEIGHT = 640

BASE_SPEED = 200       # px/sec
SPEED_RAMP = 15        # px/sec 毎秒加速
OBSTACLE_INTERVAL = 1.5   # sec
COLLECTIBLE_INTERVAL = 2.0  # sec


class World:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.SysFont(None, 36)
        self.big_font = pygame.font.SysFont(None, 72)
        self.reset()

    def reset(self) -> None:
        self.player = Player(SCREEN_HEIGHT)
        self.obstacles: list[Obstacle] = []
        self.collectibles: list[Collectible] = []
        self.score = 0
        self.elapsed = 0.0
        self.obstacle_timer = 0.0
        self.collectible_timer = 0.0
        self.game_over = False

    # ---- 速度 ----

    def _speed(self) -> float:
        return BASE_SPEED + SPEED_RAMP * self.elapsed

    # ---- イベント ----

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return
        self.player.handle_event(event)

    # ---- スポーン ----

    def _spawn_obstacle(self) -> None:
        col = random.randint(0, COLUMNS - 1)
        self.obstacles.append(Obstacle(col, self._speed()))

    def _spawn_collectible(self) -> None:
        col = random.randint(0, COLUMNS - 1)
        self.collectibles.append(Collectible(col, self._speed()))

    # ---- 更新 ----

    def update(self, dt: float) -> None:
        if self.game_over:
            return

        self.elapsed += dt
        speed = self._speed()

        # スポーンタイマー
        self.obstacle_timer += dt
        self.collectible_timer += dt
        if self.obstacle_timer >= OBSTACLE_INTERVAL:
            self._spawn_obstacle()
            self.obstacle_timer = 0.0
        if self.collectible_timer >= COLLECTIBLE_INTERVAL:
            self._spawn_collectible()
            self.collectible_timer = 0.0

        # 障害物・アイテム更新
        for obj in self.obstacles + self.collectibles:
            obj.speed = speed
            obj.update(dt)

        # 画面外削除
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen(SCREEN_HEIGHT)]
        self.collectibles = [c for c in self.collectibles if not c.is_off_screen(SCREEN_HEIGHT)]

        player_rect = self.player.rect

        # 障害物衝突 → ゲームオーバー
        for obs in self.obstacles:
            if player_rect.colliderect(obs.rect):
                self.game_over = True
                return

        # アイテム取得
        taken = [c for c in self.collectibles if player_rect.colliderect(c.rect)]
        for c in taken:
            self.score += c.POINTS
            self.collectibles.remove(c)

        # 生存スコア（時間ベース）
        self.score += int(dt * 5)

    # ---- 描画 ----

    def _draw_grid(self) -> None:
        for i in range(1, COLUMNS):
            x = i * COLUMN_WIDTH
            pygame.draw.line(self.screen, (50, 50, 60), (x, 0), (x, SCREEN_HEIGHT), 2)

    def draw(self) -> None:
        self.screen.fill((18, 18, 28))
        self._draw_grid()

        for obs in self.obstacles:
            obs.draw(self.screen)
        for col in self.collectibles:
            col.draw(self.screen)
        self.player.draw(self.screen)

        # HUD
        self.screen.blit(self.font.render(f"Score: {self.score}", True, (255, 255, 255)), (10, 10))
        self.screen.blit(
            self.font.render(f"Speed: {int(self._speed())}", True, (180, 180, 180)), (10, 46)
        )

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (0, 0))

            cx = SCREEN_WIDTH // 2
            cy = SCREEN_HEIGHT // 2
            self.screen.blit(
                self.big_font.render("GAME OVER", True, (220, 50, 50)),
                self.big_font.render("GAME OVER", True, (220, 50, 50)).get_rect(center=(cx, cy - 50)),
            )
            self.screen.blit(
                self.font.render(f"Score: {self.score}", True, (255, 255, 255)),
                self.font.render(f"Score: {self.score}", True, (255, 255, 255)).get_rect(center=(cx, cy + 10)),
            )
            self.screen.blit(
                self.font.render("R: リスタート", True, (180, 180, 180)),
                self.font.render("R: リスタート", True, (180, 180, 180)).get_rect(center=(cx, cy + 55)),
            )
