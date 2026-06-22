"""
========================================================
player.py  ―  プレイヤークラス
========================================================

【発表用説明】
プレイヤーキャラクターの状態と動作を管理するクラスです。

設計のポイント：
  - 画面を3列（左/中/右）に分割し、プレイヤーは「何列目にいるか」だけを管理します。
  - 座標（x）は列番号から自動計算するため、位置のズレが生じません。
  - A/D キーを押すと列番号を ±1 するだけで移動が完結します。

このような「状態を最小限に保つ設計」はバグを減らし、コードを読みやすくします。
"""

import pygame

COLUMNS = 3         # レーン（列）の総数
COLUMN_WIDTH = 120  # 1列あたりの幅（px）。360px ÷ 3列 = 120px


class Player:
    """プレイヤーキャラクターを表すクラス"""

    WIDTH = 60    # プレイヤーの横幅（px）
    HEIGHT = 60   # プレイヤーの縦幅（px）
    COLOR = (0, 200, 255)  # 水色（R, G, B）

    def __init__(self, screen_height: int) -> None:
        """
        初期化

        Args:
            screen_height: ウィンドウの高さ。プレイヤーを画面下部に配置するために使用。
        """
        self.col = 1  # 初期位置は中央列（0=左, 1=中, 2=右）

        # y座標は固定（画面下部から少し上）
        self.y = screen_height - self.HEIGHT - 20

    @property
    def x(self) -> int:
        """
        列番号から実際のx座標を計算するプロパティ

        列の中央にプレイヤーが来るように計算します。
        例：列1（中央）→ 1×120 + (120-60)//2 = 150
        """
        return self.col * COLUMN_WIDTH + (COLUMN_WIDTH - self.WIDTH) // 2

    @property
    def rect(self) -> pygame.Rect:
        """
        衝突判定に使う矩形（長方形）を返すプロパティ

        pygame.Rect は位置とサイズを持つ便利なオブジェクトで、
        .colliderect() メソッドで別の Rect との衝突を簡単に判定できます。
        """
        return pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        キー入力を受け取り、列を移動する

        Args:
            event: pygame が検出したイベント（キー押下など）
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a and self.col > 0:
                # A キー → 左の列へ（すでに左端なら移動しない）
                self.col -= 1
            elif event.key == pygame.K_d and self.col < COLUMNS - 1:
                # D キー → 右の列へ（すでに右端なら移動しない）
                self.col += 1

    def draw(self, screen: pygame.Surface) -> None:
        """
        プレイヤーを画面に描画する

        Args:
            screen: 描画対象の pygame サーフェス（ウィンドウ）
        """
        # border_radius で角を丸くして見た目を改善
        pygame.draw.rect(screen, self.COLOR, self.rect, border_radius=8)
