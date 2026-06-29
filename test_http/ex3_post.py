# ============================================================
# 演習3：POST と PRGパターン
# ============================================================
# 【目標】
#   ① POSTでフォームデータを受け取る
#   ② PRGパターンで二重登録を防ぐ
# 【確認】
#   登録後に再読み込みしても二重登録されないことを確認する
# ============================================================

from flask import Flask, request, ____①____, ____②____, flash, get_flashed_messages
#                                  ①redirect  ②url_for  を import する

app = Flask(__name__)
app.secret_key = "test-secret"

registered = []


@app.route("/")
def index():
    messages = get_flashed_messages()
    msg_html = "".join(f'<p style="color:green">✅ {m}</p>' for m in messages)
    items_html = "".join(f"<li>{r}</li>" for r in registered) or "<li>なし</li>"

    return f"""
    <h1>登録フォーム</h1>
    {msg_html}

    <!-- 問題1：POSTフォームにする -->
    <form method="____③____" action="/register">
      名前: <input type="text" name="name">
      <button type="submit">登録</button>
    </form>
    <ul>{items_html}</ul>
    """


# ── 問題2 ──────────────────────────────────────
# /register は POST だけ受け付ける
# methods= を埋めてください

@app.route("/register", ____④____)
def register():

    # ── 問題3 ──────────────────────────────────────
    # POSTで送られたフォームのデータを取得する
    # GETのときは request.args だったが、POSTは？

    name = ____⑤____.get("name", "名無し")

    registered.append(name)

    # ── 問題4 ──────────────────────────────────────
    # flash でメッセージをセットして、index にリダイレクトする
    # PRGパターンの「R（Redirect）」

    flash(f"「{name}」を登録しました")
    return ____⑥____(____⑦____("index"))   # ⑥redirect  ⑦url_for


if __name__ == "__main__":
    app.run(debug=True, port=5001)
