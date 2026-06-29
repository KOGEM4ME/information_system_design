"""
================================================
step3_post.py  ―  POST の動きを確認する
================================================

【実験手順】
1. python step3_post.py で起動
2. http://127.0.0.1:5001/ を開く
3. フォームに入力して「登録」を押す
4. URLが変わらないことを確認する（データはURLに出ない）
5. ブラウザの「戻る」→「再読み込み」を試す
   → 「フォームを再送信しますか？」という警告が出る（POSTの二重送信問題）

【GETとの違いを確認する】
- GET: URL に ?name=xxx が付く → URLを見れば値が分かる
- POST: URL は /register のまま → URLを見ても値が分かからない
"""

from flask import Flask, request

app = Flask(__name__)

# 登録されたデータを一時保存するリスト（本来はDB）
registered = []

@app.route("/")
def index():
    # 登録済みデータを一覧表示
    items_html = "".join(
        f"<li>{i+1}. {item}</li>" for i, item in enumerate(registered)
    ) or "<li>まだ登録されていません</li>"

    return f"""
    <h1>登録フォーム（POSTの実験）</h1>

    <!--
      method="POST" → 送信してもURLは変わらない
      データはリクエストの「ボディ」に入る（URLには出ない）
    -->
    <form method="POST" action="/register">
      名前: <input type="text" name="name" placeholder="山田太郎">
      <button type="submit">登録</button>
    </form>

    <hr>
    <h2>登録済み一覧</h2>
    <ul>{items_html}</ul>
    """


@app.route("/register", methods=["POST"])
def register():
    # request.form = POSTで送られたデータ
    # request.args（GETパラメータ）とは別物
    name = request.form.get("name", "名無し")

    # データを追加
    registered.append(name)

    # ↓ ここが重要：POST後はそのままHTMLを返さず、レスポンスを返す
    # このままだと「再読み込み」で二重登録される
    return f"""
    <h1>登録完了（PRGなし版）</h1>
    <p>「{name}」を登録しました</p>
    <p>⚠️ このページを再読み込みすると同じデータが再登録されます！</p>
    <a href="/">戻る</a>
    <hr>
    <p>現在の登録数: {len(registered)}</p>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5001)
