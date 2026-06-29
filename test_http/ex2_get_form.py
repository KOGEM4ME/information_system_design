# ============================================================
# 演習2：GETフォーム
# ============================================================
# 【目標】フォームを送信するとURLに条件が付くことを確認する
# 【確認】送信後のURLが /search?keyword=xxx になることを見る
# ============================================================

from flask import Flask, request

app = Flask(__name__)

BOOKS = [
    {"title": "Pythonチュートリアル", "author": "Guido"},
    {"title": "データベース概論",     "author": "増永"},
    {"title": "Pythonデータ分析",     "author": "Wes"},
]


@app.route("/search")
def search():
    # ── 問題1 ──────────────────────────────────────
    # URLから keyword と author を取り出す
    # 未入力のときは空文字 "" にする

    keyword = request.args.get("keyword", "")  # request.??? を使う
    author  = request.args.get("author", "")


    # ── 問題2 ──────────────────────────────────────
    # keyword と author で BOOKS を絞り込む
    # 両方入力されていたら両方に一致するもの（AND検索）

    results = []
    for book in BOOKS:
        if keyword and keyword not in book["title"]:
            continue   # ③ 何を使って絞り込む？
        if author and author not in book["author"]:
            continue   # ④ 著者で絞り込むには？
        results.append(book)


    books_html = "".join(f"<li>『{b['title']}』</li>" for b in results) or "<li>なし</li>"

    return f"""
    <h1>蔵書検索</h1>

    <!-- 問題3：フォームの method を埋めてください -->
    <!-- GETフォームにするには？ -->
    <form method="GET" action="/search">
      書名: <input type="text" name="keyword" value="{keyword}">
      著者: <input type="text" name="author"  value="{author}">
      <button type="submit">検索</button>
    </form>

    <hr>
    <p>URLパラメータ: {dict(request.args)}</p>
    <ul>{books_html}</ul>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5001)
