"""
========================================================
collectible.py  ―  コイン（取得アイテム）クラス
========================================================

【発表用説明】
プレイヤーが取得することでスコアを加算するコインを管理するクラスです。

Obstacle クラスとの設計上の共通点：
  - どちらも「列番号」「y座標」「速度」を持ち、update() で落下します。
  - 将来的に共通の基底クラス（FallingObject など）にまとめることで
    コードの重複をさらに減らせます（リファクタリングの余地）。

Obstacle との違い：
  - 当たると「ゲームオーバー」ではなく「スコア加算」になる点が異なります。
  - 見た目を円（circle）にすることで、障害物（四角）と直感的に区別できます。
"""

import pygame

COLUMN_WIDTH = 120  # 1列あたりの幅（px）


class Collectible:
    """取得するとスコアが増えるコインアイテムを表すクラス"""

    SIZE = 28                 # 円の直径（px）
    COLOR = (255, 215, 0)     # 金色（R, G, B）
    POINTS = 10               # 取得したときに加算されるスコア

    def __init__(self, col: int, speed: float) -> None:
        """
        初期化

        Args:
            col:   出現する列番号（0=左, 1=中, 2=右）
            speed: 落下速度（px/秒）
        """
        self.col = col
        # 列の中央に配置
        self.x = col * COLUMN_WIDTH + (COLUMN_WIDTH - self.SIZE) // 2
        self.y = float(-self.SIZE)  # 画面外（上）からスタート
        self.speed = speed

    @property
    def rect(self) -> pygame.Rect:
        """
        衝突判定用の矩形

        見た目は円だが、衝突判定は四角（rect）で行うのが pygame の慣例です。
        完全な円形判定より処理が軽いため、ゲームでは一般的な手法です。
        """
        return pygame.Rect(self.x, int(self.y), self.SIZE, self.SIZE)

    def update(self, dt: float) -> None:
        """
        位置を更新（毎フレーム呼ばれる）

        Args:
            dt: 前フレームからの経過時間（秒）
        """
        self.y += self.speed * dt

    def draw(self, screen: pygame.Surface) -> None:
        """コインを円として画面に描画する"""
        # 円の中心座標を計算
        center = (self.x + self.SIZE // 2, int(self.y) + self.SIZE // 2)
        pygame.draw.circle(screen, self.COLOR, center, self.SIZE // 2)

    def is_off_screen(self, screen_height: int) -> bool:
        """
        コインが画面外（下）に出たかどうかを返す

        Returns:
            画面外に出ていれば True（取得されずに通過した場合、World 側で削除）
        """
        return self.y > screen_height
