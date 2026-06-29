"""
================================================
step2_get_form.py  ―  GETフォームの動きを確認する
================================================

【実験手順】
1. python step2_get_form.py で起動
2. http://127.0.0.1:5001/ を開く
3. フォームに入力して「検索」を押す
4. URLが変わることを確認する → ?keyword=xxx&author=yyy

【着目ポイント】
- フォームを送信するとURLに条件が付く
- ブラウザの「戻る」で検索条件が残る
- URLをコピーして貼り付けると同じ結果になる（共有できる）
"""

from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def index():
    # フォームが送信されると同じ / にGETリクエストが来る
    keyword = request.args.get("keyword", "")
    author  = request.args.get("author",  "")

    # ダミーの蔵書データ（本来はDBから取得）
    all_books = [
        {"title": "Pythonチュートリアル", "author": "Guido"},
        {"title": "データベース概論",     "author": "増永"},
        {"title": "Pythonデータ分析",     "author": "Wes"},
    ]

    # 検索フィルタリング（models.search_books() と同じ考え方）
    results = []
    for book in all_books:
        if keyword and keyword not in book["title"]:
            continue  # keywordが入力されていてタイトルに含まれなければスキップ
        if author and author not in book["author"]:
            continue
        results.append(book)

    # HTML を直接文字列で返す（テンプレートなしの最小例）
    books_html = "".join(
        f"<li>『{b['title']}』― {b['author']}</li>" for b in results
    ) or "<li>該当なし</li>"

    return f"""
    <h1>蔵書検索（GETフォームの実験）</h1>

    <!--
      method="GET" → 送信するとURLに ?keyword=xxx が付く
      action="/"   → このページ自身に送信
    -->
    <form method="GET" action="/">
      書名: <input type="text" name="keyword" value="{keyword}">
      著者: <input type="text" name="author"  value="{author}">
      <button type="submit">検索</button>
    </form>

    <hr>
    <p>現在のURLパラメータ: <code>{dict(request.args)}</code></p>
    <p>検索結果 ({len(results)}件):</p>
    <ul>{books_html}</ul>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5001)
