"""
================================================
step1_get.py  ―  GET の動きを確認する
================================================

【実験手順】
1. python step1_get.py で起動
2. ブラウザで以下を試す：
   http://127.0.0.1:5001/
   http://127.0.0.1:5001/hello
   http://127.0.0.1:5001/hello?name=太郎
   http://127.0.0.1:5001/hello?name=太郎&age=20
"""

from flask import Flask, request

app = Flask(__name__)

# =========================================
# 実験1：一番シンプルなルート
# =========================================
@app.route("/")
def index():
    # return で返した文字列がブラウザに表示される
    return "Hello! これがトップページです"


# =========================================
# 実験2：URLパラメータを受け取る（GET）
# =========================================
@app.route("/hello")
def hello():
    # request.args = URL の ? 以降のパラメータを辞書で取得
    # http://127.0.0.1:5001/hello?name=太郎 の場合
    # request.args = {"name": "太郎"}

    name = request.args.get("name", "名無し")  # なければ "名無し"
    age  = request.args.get("age",  "不明")

    # f文字列でHTMLを返す（テンプレートを使わない最小の例）
    return f"""
    <h1>こんにちは、{name}さん！</h1>
    <p>年齢: {age}</p>
    <hr>
    <p>URLのパラメータ全体: {dict(request.args)}</p>
    """


# =========================================
# 実験3：パスの中に変数を入れる
# =========================================
@app.route("/user/<user_id>")
def user(user_id):
    # <user_id> の部分が変数になる
    # http://127.0.0.1:5001/user/42 → user_id = "42"
    return f"ユーザーID: {user_id} のページです"


if __name__ == "__main__":
    # ポートを 5001 にして本番アプリ(5000)と混在しないようにする
    app.run(debug=True, port=5001)
