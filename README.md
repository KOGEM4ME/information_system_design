# Vertical Dash — 情報システム設計 最終課題

## ゲーム概要

Geometry Dash 風の縦スクロールアクションゲーム。  
3列のレーンを A / D キーで左右に移動しながら障害物を避け、コインを集める。

```
┌──────┬──────┬──────┐
│  左  │  中  │  右  │  ← 3列レーン
│      │  🟦  │      │  ← プレイヤー（A/Dで移動）
│  🔴  │      │  🟡  │  ← 障害物(赤) / コイン(黄)
│      │  🔴  │      │
└──────┴──────┴──────┘
```

## 操作方法

| キー | 動作 |
|------|------|
| `A`  | 左のレーンへ移動 |
| `D`  | 右のレーンへ移動 |
| `R`  | ゲームオーバー後にリスタート |

## ゲームルール

- 障害物（赤）に当たるとゲームオーバー
- コイン（金）を取ると +10 点
- 生存時間に応じてスコアが加算される
- 時間経過とともにスピードが上昇する

## セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/KOGEM4ME/information_system_design
cd information_system_design

# 依存パッケージのインストール
pip install -r requirements.txt

# 起動
python main.py
```

## ディレクトリ構成

```
information_system_design/
├── main.py            # エントリポイント
├── requirements.txt
├── README.md
└── game/
    ├── __init__.py
    ├── player.py      # プレイヤークラス
    ├── obstacle.py    # 障害物クラス
    ├── collectible.py # コイン（取得アイテム）クラス
    └── world.py       # ゲームループ・スポーン管理
```

## 開発メンバー

| 名前 | 役割 |
|------|------|
|      |      |

## ブランチ運用

- `main` : 本番相当のブランチ。直接コミット禁止
- `feature/<機能名>` : 機能追加・変更用ブランチ

```bash
# 作業開始
git checkout main
git pull origin main
git checkout -b feature/<機能名>

# 作業完了後
git add .
git commit -m "feat: <変更内容>"
git push origin feature/<機能名>
```

## コミットメッセージ規則

| プレフィックス | 用途 |
|----------------|------|
| `feat:`     | 新機能の追加 |
| `fix:`      | バグ修正 |
| `docs:`     | ドキュメントの変更 |
| `refactor:` | リファクタリング |
