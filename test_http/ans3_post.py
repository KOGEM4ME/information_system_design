# ============================================================
# 解答3：POST と PRGパターン
# ============================================================

from flask import Flask, request, redirect, url_for, flash, get_flashed_messages
#                                  ①redirect  ②url_for

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
    <form method="POST" action="/register">   <!-- ③ POST フォーム -->
      名前: <input type="text" name="name">
      <button type="submit">登録</button>
    </form>
    <ul>{items_html}</ul>
    """


@app.route("/register", methods=["POST"])    # ④ POSTだけ受け付ける
def register():
    name = request.form.get("name", "名無し")  # ⑤ POSTは request.form

    registered.append(name)

    flash(f"「{name}」を登録しました")
    return redirect(url_for("index"))          # ⑥redirect  ⑦url_for


# ── 解説 ──────────────────────────────────────
# ① ②  redirect と url_for は flask からimportが必要
# ③    method="POST" にするとデータがURLに出ない
# ④    methods=["POST"] でPOSTのみ受け付ける
#       書かないとGETしか受け付けず405エラーになる
# ⑤    POSTのデータは request.form（GETは request.args）
# ⑥ ⑦ redirect(url_for("関数名")) でPRGパターンを実現
#       url_for("index") = "index" 関数のURL = "/"

if __name__ == "__main__":
    app.run(debug=True, port=5001)
