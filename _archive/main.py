"""
========================================================
Vertical Dash  ―  メインエントリポイント
========================================================

【発表用説明】
このファイルはプログラムの起動口（エントリポイント）です。
pygame を初期化し、ウィンドウを作成してゲームループを回します。

ゲームループとは？
  while True:
      1. キー入力などのイベントを取得
      2. ゲームの状態を更新（オブジェクトの移動・衝突判定）
      3. 画面を描画
  この3ステップを1秒間に60回繰り返すことで滑らかなアニメーションを実現します。
  これは「フレームレート60fps」と呼ばれます。
"""

import sys

import pygame

from game.world import World  # ゲーム全体を管理するクラスをインポート

# ウィンドウサイズの定数（3列 × 120px = 360px 幅）
SCREEN_WIDTH = 360
SCREEN_HEIGHT = 640
FPS = 60  # 1秒あたりの描画回数


def main() -> None:
    """ゲームの初期化・起動・メインループを担う関数"""

    # pygameライブラリ全体を初期化（音声・グラフィック等のサブシステムを起動）
    pygame.init()

    # ゲームウィンドウを作成
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Vertical Dash")  # ウィンドウタイトル

    # フレームレートを制御するクロックオブジェクト
    clock = pygame.time.Clock()

    # ゲーム本体（World）を生成
    world = World(screen)

    # ========== メインループ ==========
    while True:
        # 前フレームからの経過時間をミリ秒で取得し、秒に変換（dt = delta time）
        # dt を使うことで、PCの処理速度に関わらず一定速度で動かせる
        dt = clock.tick(FPS) / 1000.0

        # --- イベント処理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # ウィンドウの×ボタンが押された
                pygame.quit()
                sys.exit()
            world.handle_event(event)  # キー入力などをWorldに渡す

        # --- 状態更新（移動・衝突判定・スコア計算）---
        world.update(dt)

        # --- 描画 ---
        world.draw()
        pygame.display.flip()  # 描画結果をディスプレイに反映（ダブルバッファリング）


# このファイルを直接実行したときだけ main() を呼ぶ
# （他のファイルからインポートされたときは呼ばない）
if __name__ == "__main__":
    main()
