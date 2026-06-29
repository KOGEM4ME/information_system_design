# GET/POST 穴埋め演習

## ファイル一覧

| 問題 | 解答 | テーマ |
|------|------|--------|
| ex1_get.py | ans1_get.py | GETの基本・URLパラメータ |
| ex2_get_form.py | ans2_get_form.py | GETフォーム・AND検索 |
| ex3_post.py | ans3_post.py | POST・PRGパターン |

## 進め方

1. `ex1_get.py` を開いて `____①____` の部分を埋める
2. `python ex1_get.py` で起動してブラウザで確認
3. 動いたら次の問題へ、詰まったら `ans1_get.py` を見る

## 穴埋めのヒント早見表

| 状況 | 使うもの |
|------|----------|
| GETパラメータを取得 | `request.args.get("キー", "デフォルト")` |
| POSTデータを取得 | `request.form.get("キー", "デフォルト")` |
| POSTを受け付ける | `methods=["POST"]` または `methods=["GET","POST"]` |
| POST後にリダイレクト | `redirect(url_for("関数名"))` |
| 次ページにメッセージ | `flash("メッセージ")` |
