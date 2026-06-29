"""
================================================
step4_prg.py  ―  PRGパターンで二重送信を防ぐ
================================================

【実験手順】
1. python step4_prg.py で起動
2. http://127.0.0.1:5001/ を開く
3. フォームに入力して「登録」を押す
4. 登録完了後にブラウザの「再読み込み」を試す
   → 今度は「フォームを再送信しますか？」が出ない！
   → 再読み込みしても二重登録されない

【step3との違い】
step3: POST → HTMLを直接返す（再読み込みで二重送信）
step4: POST → redirect → GET（再読み込みはGETなので安全）

【図書館システムとの対応】
app.py の loan() 関数と同じ構造：
  if request.method == "POST":
      models.loan_book(...)
      return redirect(url_for("loan"))  ← ここがPRG
"""

from flask import Flask, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "test-secret"  # flash() を使うために必要

registered = []


@app.route("/")
def index():
    items_html = "".join(
        f"<li>{i+1}. {item}</li>" for i, item in enumerate(registered)
    ) or "<li>まだ登録されていません</li>"

    # flash メッセージを取得して表示
    # get_flashed_messages() は一度読むと消える（次の再読み込みでは出ない）
    from flask import get_flashed_messages
    messages = get_flashed_messages()
    msg_html = "".join(f'<p style="color:green">✅ {m}</p>' for m in messages)

    return f"""
    <h1>登録フォーム（PRGパターン版）</h1>
    {msg_html}

    <form method="POST" action="/register">
      名前: <input type="text" name="name" placeholder="山田太郎">
      <button type="submit">登録</button>
    </form>

    <hr>
    <h2>登録済み一覧（{len(registered)}件）</h2>
    <ul>{items_html}</ul>
    """


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "名無し")
    registered.append(name)

    # flash() = 「次のページに一度だけ表示するメッセージ」をセット
    flash(f"「{name}」を登録しました")

    # POST処理後は redirect でGETに切り替える（PRGパターン）
    # これにより再読み込み = GETになるので二重送信が起きない
    return redirect(url_for("index"))
    #               ↑ "index" = @app.route("/") の関数名


if __name__ == "__main__":
    app.run(debug=True, port=5001)
