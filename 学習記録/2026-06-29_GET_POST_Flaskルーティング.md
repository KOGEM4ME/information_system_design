# GET・POST・Flaskルーティング 学習記録

**日付:** 2026年6月29日  
**対象コード:** `図書館貸し出しシステム/app.py` / `templates/search.html` / `templates/loan.html`

---

## GET とは：URLでデータを運ぶ通信

```
http://127.0.0.1:5000/search?keyword=Python&author=Guido
                              ↑
                         クエリパラメータ（URLにデータが乗っている）
```

URLを見れば何を検索したか分かる。共有・ブックマークができる。

### 実装手順

```python
# 手順①：ルートだけ作る
@app.route("/search")
def search():
    return "検索ページです"

# 手順②：URLパラメータを受け取る
@app.route("/search")
def search():
    keyword = request.args.get("keyword", "")  # ?keyword=xxx を取得
    author  = request.args.get("author",  "")

# 手順③：DBを検索してHTMLを返す
@app.route("/search")
def search():
    keyword = request.args.get("keyword", "").strip()
    books   = models.search_books(keyword, author)
    return render_template("search.html", books=books, keyword=keyword)
```

### HTMLフォーム（GET）

```html
<form method="GET" action="/search">
  <input type="text" name="keyword">
  <button type="submit">検索</button>
</form>
<!-- 送信すると → /search?keyword=Python というURLになる -->
```

---

## POST とは：ボディでデータを運ぶ通信

```
GETだったら → /loan?member_id=1&book_id=2  （URLに個人情報が露出）
POSTだったら → /loan  （データはURLに出ない）
```

データを「変更する」操作（貸出・返却・登録・削除）に使う。

### 実装手順

```python
# 手順①：GET と POST 両方受け取る
@app.route("/loan", methods=["GET", "POST"])
#                   ↑ 書かないとPOSTで405エラーになる
def loan():
    if request.method == "POST":
        pass  # POST処理
    return render_template("loan.html")

# 手順②：POSTデータを受け取る
    member_id = request.form.get("member_id")  # request.form（POSTはここ）
    book_id   = request.form.get("book_id")
    # GETは request.args、POSTは request.form

# 手順③：処理してリダイレクト（PRGパターン）
    success, message = models.loan_book(book_id, member_id)
    flash(message)
    return redirect(url_for("loan"))  # POST後は必ずリダイレクト
```

---

## PRGパターン（Post-Redirect-Get）

### なぜ必要か

```
POST後にHTMLをそのまま返す → 再読み込みで同じPOSTが2回送られる
                           → 同じ本が2回貸出登録される！
```

### PRGの流れ

```
ブラウザ         Flask
   │  POST /loan   │  貸出処理
   │ ────────────▶ │
   │  302 Redirect │
   │ ◀──────────── │
   │  GET /loan    │  フォームを表示
   │ ────────────▶ │
   │  200 OK       │
   │ ◀──────────── │
```

再読み込みは「GETをもう一度」なので安全。

---

## GET と POST の使い分けまとめ

| | GET | POST |
|---|---|---|
| データの場所 | URLの `?` 以降 | リクエストボディ（見えない） |
| 用途 | 見る・検索する | 変更・追加・削除する |
| URLの共有 | できる | できない |
| コード | `request.args.get()` | `request.form.get()` |
| 例 | `/search?keyword=Python` | 貸出登録・返却登録 |
