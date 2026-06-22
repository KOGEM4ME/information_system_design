# 情報システム設計 最終課題

## 概要

本リポジトリは情報システム設計の最終課題における共同開発用リポジトリです。

## 開発メンバー

| 名前 | 役割 |
|------|------|
|      |      |

## セットアップ

```bash
# リポジトリのクローン
git clone <リポジトリURL>
cd information_system_design
```

## ブランチ運用

- `main` : 本番相当のブランチ。直接コミット禁止
- `feature/<機能名>` : 機能追加・変更用ブランチ

### 開発フロー

1. `main` から `feature/xxx` ブランチを作成
2. 機能を実装してコミット
3. `main` へのプルリクエストを作成
4. レビュー後にマージ

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
| `feat:`   | 新機能の追加 |
| `fix:`    | バグ修正 |
| `docs:`   | ドキュメントの変更 |
| `refactor:` | リファクタリング |

## ディレクトリ構成

```
information_system_design/
├── README.md
└── (追加予定)
```
