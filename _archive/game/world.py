"""
========================================================
world.py  ―  ゲーム全体の管理クラス
========================================================

【発表用説明】
ゲームの「司令塔」にあたるクラスです。以下の責務をまとめて担います。

  1. オブジェクト管理：プレイヤー・障害物・コインのリストを保持
  2. スポーン（出現）管理：一定時間ごとに障害物とコインを生成
  3. 衝突判定：プレイヤーと障害物/コインが重なっているかチェック
  4. スコア計算：コイン取得 + 生存時間に応じてスコアを加算
  5. 難易度調整：時間経過に応じて落下速度を上昇させる
  6. 描画：すべてのオブジェクトと HUD（スコア表示）を描画

ソフトウェア設計の観点：
  各クラス（Player/Obstacle/Collectible）は「自分自身のこと」だけを知っています。
  World が「全体のこと」を知り、それらを組み合わせることで
  「関心の分離（Separation of Concerns）」を実現しています。
"""

import random

import pygame

from game.collectible import Collectible
from game.obstacle import Obstacle
from game.player import Player

# ========== 定数 ==========
COLUMNS = 3          # レーンの数
COLUMN_WIDTH = 120   # 1列の幅（px）
SCREEN_WIDTH = 360   # ウィンドウ幅（= COLUMNS × COLUMN_WIDTH）
SCREEN_HEIGHT = 640  # ウィンドウ高さ

BASE_SPEED = 200        # ゲーム開始時の落下速度（px/秒）
SPEED_RAMP = 15         # 毎秒加算される速度増加量（px/秒²）
OBSTACLE_INTERVAL = 1.5  # 障害物を出現させる間隔（秒）
COLLECTIBLE_INTERVAL = 2.0  # コインを出現させる間隔（秒）


class World:
    """ゲーム全体の状態を管理するクラス"""

    def __init__(self, screen: pygame.Surface) -> None:
        """
        初期化

        Args:
            screen: 描画対象の pygame サーフェス（ウィンドウ）
        """
        self.screen = screen

        # フォントの準備（SysFont は OS のシステムフォントを使用）
        self.font = pygame.font.SysFont(None, 36)       # 通常サイズ（スコア表示用）
        self.big_font = pygame.font.SysFont(None, 72)   # 大サイズ（GAME OVER 表示用）

        self.reset()  # ゲーム状態を初期化

    def reset(self) -> None:
        """ゲームをリセットして最初の状態に戻す（リスタート時にも呼ばれる）"""

        self.player = Player(SCREEN_HEIGHT)   # プレイヤーを生成

        # 障害物・コインのリスト（ゲーム中に動的に追加・削除される）
        self.obstacles: list[Obstacle] = []
        self.collectibles: list[Collectible] = []

        self.score = 0          # 現在のスコア
        self.elapsed = 0.0      # ゲーム開始からの経過時間（秒）

        # スポーン用タイマー（一定時間が経つとオブジェクトを出現させる）
        self.obstacle_timer = 0.0
        self.collectible_timer = 0.0

        self.state = "start"  # ゲームの状態（"start" / "playing" / "game_over"）
        # スタート画面を追加した

    # ========== 速度計算 ==========

    def _speed(self) -> float:
        """
        現在の落下速度を計算して返す

        経過時間に比例して速度が上昇し、ゲームが難しくなります。
        式: 初期速度 + 加速度 × 経過時間
        """
        return BASE_SPEED + SPEED_RAMP * self.elapsed

    # ========== イベント処理 ==========

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        キー入力などのイベントを処理する

        ゲームオーバー中は R キーのリスタートのみ受け付けます。

        Args:
            event: pygame が検出したイベント
        """
        if self.state == "start":
            # エンターキーでゲーム開始
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.state = "playing"
            return
        if self.state == "game_over":
            # R キーでリスタート
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        # 通常プレイ中はプレイヤーにイベントを渡す
        self.player.handle_event(event)

    # ========== スポーン（オブジェクト出現） ==========

    def _spawn_obstacle(self) -> None:
        """
        ランダムな列に障害物を1つ生成してリストに追加する

        random.randint(0, 2) で 0/1/2 のどれかをランダムに選びます。
        """
        col = random.randint(0, COLUMNS - 1)
        self.obstacles.append(Obstacle(col, self._speed()))

    def _spawn_collectible(self) -> None:
        """ランダムな列にコインを1つ生成してリストに追加する"""
        col = random.randint(0, COLUMNS - 1)
        self.collectibles.append(Collectible(col, self._speed()))

    # ========== 更新（毎フレーム呼ばれる） ==========

    def update(self, dt: float) -> None:
        """
        ゲーム状態を1フレーム分進める

        処理の流れ：
          1. 経過時間を加算して速度を更新
          2. タイマーを進め、一定時間ごとにオブジェクトをスポーン
          3. 全オブジェクトの位置を更新
          4. 画面外に出たオブジェクトを削除
          5. 衝突判定
          6. スコアを加算

        Args:
            dt: 前フレームからの経過時間（秒）
        """
        if self.state != "playing":
            return  # ゲームオーバー中，スタート画面では更新しない
        
        # 以下self.state == "playing" の場合のみ処理される               

        # 経過時間を積算（速度計算に使用）
        self.elapsed += dt
        speed = self._speed()

        # --- スポーンタイマーを進める ---
        self.obstacle_timer += dt
        self.collectible_timer += dt

        if self.obstacle_timer >= OBSTACLE_INTERVAL:
            self._spawn_obstacle()
            self.obstacle_timer = 0.0  # タイマーリセット

        if self.collectible_timer >= COLLECTIBLE_INTERVAL:
            self._spawn_collectible()
            self.collectible_timer = 0.0

        # --- 全オブジェクトの速度を現在値に同期して位置を更新 ---
        for obj in self.obstacles + self.collectibles:
            obj.speed = speed  # 速度を最新値に更新
            obj.update(dt)

        # --- 画面外に出たオブジェクトをリストから削除（メモリ節約）---
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen(SCREEN_HEIGHT)]
        self.collectibles = [c for c in self.collectibles if not c.is_off_screen(SCREEN_HEIGHT)]

        # --- 衝突判定 ---
        player_rect = self.player.rect

        # 障害物との衝突 → ゲームオーバー
        for obs in self.obstacles:
            if player_rect.colliderect(obs.rect):
                self.state = "game_over"
                return  # 以降の処理をスキップ

        # コインとの衝突 → スコア加算・コイン削除
        taken = [c for c in self.collectibles if player_rect.colliderect(c.rect)]
        for c in taken:
            self.score += c.POINTS        # スコアに POINTS（10点）を加算
            self.collectibles.remove(c)  # 取得済みコインをリストから削除

        # --- 生存スコア（時間が経つほど加算される）---
        # 1秒間に5点加算される計算（dt × 5）
        self.score += int(dt * 5)

    # ========== 描画 ==========

    def _draw_grid(self) -> None:
        """列を区切る縦線を描画する（視覚的なレーン表示）"""
        for i in range(1, COLUMNS):
            x = i * COLUMN_WIDTH
            pygame.draw.line(self.screen, (50, 50, 60), (x, 0), (x, SCREEN_HEIGHT), 2)

    def draw(self) -> None:
        """ゲーム画面全体を描画する（毎フレーム呼ばれる）"""
        if self.state == "start":
            # スタート画面の描画
            self.screen.fill((18, 18, 28))  # 背景色

            cx = SCREEN_WIDTH // 2   # 画面中央のx座標
            cy = SCREEN_HEIGHT // 2  # 画面中央のy座標

            # 「Press Enter to Start」テキスト
            start_surf = self.font.render("Press Enter to Start", True, (200, 200, 200))
            self.screen.blit(start_surf, start_surf.get_rect(center=(cx, cy)))

            return  # スタート画面ではそれ以降の描画は行わない

        # 背景を暗い色で塗りつぶす（前フレームの描画を消去）
        self.screen.fill((18, 18, 28))

        # レーンの区切り線を描画
        self._draw_grid()

        # 障害物を描画
        for obs in self.obstacles:
            obs.draw(self.screen)

        # コインを描画
        for col in self.collectibles:
            col.draw(self.screen)

        # プレイヤーを描画
        self.player.draw(self.screen)

        # --- HUD（ヘッドアップディスプレイ）：スコアと速度を左上に表示 ---
        self.screen.blit(
            self.font.render(f"Score: {self.score}", True, (255, 255, 255)),
            (10, 10)
        )
        self.screen.blit(
            self.font.render(f"Speed: {int(self._speed())}", True, (180, 180, 180)),
            (10, 46)
        )

        # --- ゲームオーバー画面 ---
        if self.state == "game_over":
            # 半透明の黒いオーバーレイを重ねて画面を暗くする
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))  # 最後の値（140）が透明度（0=透明, 255=不透明）
            self.screen.blit(overlay, (0, 0))

            cx = SCREEN_WIDTH // 2   # 画面中央のx座標
            cy = SCREEN_HEIGHT // 2  # 画面中央のy座標

            # 「GAME OVER」テキスト
            go_surf = self.big_font.render("GAME OVER", True, (220, 50, 50))
            self.screen.blit(go_surf, go_surf.get_rect(center=(cx, cy - 50)))

            # 最終スコア
            sc_surf = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(sc_surf, sc_surf.get_rect(center=(cx, cy + 10)))

            # リスタート案内
            rs_surf = self.font.render("R: リスタート", True, (180, 180, 180))
            self.screen.blit(rs_surf, rs_surf.get_rect(center=(cx, cy + 55)))
