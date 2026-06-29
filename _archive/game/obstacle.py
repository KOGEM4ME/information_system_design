"""
========================================================
obstacle.py  ―  障害物クラス
========================================================

【発表用説明】
画面上部からプレイヤーに向かって落下してくる障害物を管理するクラスです。

動作の仕組み：
  - 毎フレーム y座標を「速度 × 経過時間（dt）」だけ増やすことで下方向に移動します。
  - 時間ベースの計算（speed × dt）により、PCの処理速度が変わっても
    見た目上の移動速度が一定に保たれます。

オブジェクト指向設計のメリット：
  - 障害物を何個でも簡単に増やせます（Obstacle クラスのインスタンスを生成するだけ）。
  - 各障害物が自分自身の座標・速度を持つため、個別に動作させられます。
"""

import pygame

COLUMN_WIDTH = 120  # 1列あたりの幅（px）


class Obstacle:
    """落下する障害物を表すクラス"""

    HEIGHT = 40                  # 障害物の高さ（px）
    COLOR = (220, 50, 50)        # 赤色（R, G, B）

    def __init__(self, col: int, speed: float) -> None:
        """
        初期化

        Args:
            col:   出現する列番号（0=左, 1=中, 2=右）
            speed: 落下速度（px/秒）。ゲーム進行とともに World から増加させる。
        """
        self.col = col
        self.x = col * COLUMN_WIDTH + 5  # 列内で左右に5pxの余白をとる
        self.y = float(-self.HEIGHT)     # 画面外（上）からスタート
        self.speed = speed

    @property
    def rect(self) -> pygame.Rect:
        """衝突判定用の矩形。y は整数に変換（pygame.Rect は整数座標を要求）"""
        return pygame.Rect(self.x, int(self.y), COLUMN_WIDTH - 10, self.HEIGHT)

    def update(self, dt: float) -> None:
        """
        位置を更新（毎フレーム呼ばれる）

        Args:
            dt: 前フレームからの経過時間（秒）
        """
        # 速度（px/秒）× 時間（秒）= 移動量（px）
        self.y += self.speed * dt

    def draw(self, screen: pygame.Surface) -> None:
        """障害物を画面に描画する"""
        pygame.draw.rect(screen, self.COLOR, self.rect, border_radius=4)

    def is_off_screen(self, screen_height: int) -> bool:
        """
        障害物が画面外（下）に出たかどうかを返す

        Args:
            screen_height: ウィンドウの高さ
        Returns:
            画面外に出ていれば True（World 側でリストから削除するために使用）
        """
        return self.y > screen_height
