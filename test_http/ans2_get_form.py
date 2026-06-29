# ============================================================
# 解答2：GETフォーム
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
    keyword = request.args.get("keyword", "")   # ① request.args.get()
    author  = request.args.get("author",  "")   # ②

    results = []
    for book in BOOKS:
        if keyword and keyword not in book["title"]:  # ③ keyword で絞り込む
            continue
        if author and author not in book["author"]:   # ④ book["author"] と比較
            continue
        results.append(book)

    books_html = "".join(f"<li>『{b['title']}』</li>" for b in results) or "<li>なし</li>"

    return f"""
    <h1>蔵書検索</h1>
    <form method="GET" action="/search">    <!-- ⑤ GET フォーム -->
      書名: <input type="text" name="keyword" value="{keyword}">
      著者: <input type="text" name="author"  value="{author}">
      <button type="submit">検索</button>
    </form>
    <hr>
    <p>URLパラメータ: {dict(request.args)}</p>
    <ul>{books_html}</ul>
    """


# ── 解説 ──────────────────────────────────────
# ① ② GETのパラメータは request.args から取る
#        POSTのデータは request.form から取る（演習3で確認）
# ③ ④  keyword が空文字のときは絞り込まない（条件なし = 全件）
# ⑤    method="GET" にするとURLに ?keyword=xxx が付く

if __name__ == "__main__":
    app.run(debug=True, port=5001)
