# ============================================================
# 解答1：GETの基本
# ============================================================

from flask import Flask, request   # ①

app = Flask(__name__)


@app.route("/")                    # ②
def index():
    return "トップページです"


@app.route("/hello")
def hello():
    name = request.args.get("name", "名無し")   # ③④ request.args がGETパラメータ
    age  = request.args.get("age",  "不明")     # ⑤

    return f"<h1>こんにちは、{name}さん！年齢: {age}</h1>"


# ── 解説 ──────────────────────────────────────
# ① request をimportしないと request.args が使えない
# ② @app.route("/") のパスがURLのパスに対応する
# ③④ GETパラメータは request.args（argsはargumentsの略）
# ⑤ .get("キー", "デフォルト値") で、キーがなければデフォルトを返す

if __name__ == "__main__":
    app.run(debug=True, port=5001)
