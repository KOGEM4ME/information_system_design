# Python文法とHTML基礎 — 演習2で分かっていなかった箇所

**日付:** 2026年6月29日  
**きっかけ:** test_http/ex2_get_form.py の演習中に詰まった

---

## 1. BOOKSリストはただのPython（Flaskは関係ない）

```python
BOOKS = [
    {"title": "Pythonチュートリアル", "author": "Guido"},
    {"title": "データベース概論",     "author": "増永"},
]
```

演習2でFlask固有の仕組みが出てくるのは1か所だけ：

| コード | 種類 |
|--------|------|
| `BOOKS = [{"title": ...}]` | 普通のPythonリスト |
| `for book in BOOKS:` | 普通のPythonループ |
| `if keyword not in book["title"]` | 普通のPython条件式 |
| `request.args.get("keyword", "")` | **Flaskの機能** |
| `@app.route("/search")` | **Flaskの機能** |

---

## 2. f文字列（f"..."）

`f` を先頭に付けると `{}` の中に変数を埋め込める。

```python
title = "Python入門"

f"<li>{title}</li>"        # → "<li>Python入門</li>"

b = {"title": "Python入門"}
f"<li>『{b['title']}』</li>"  # → "<li>『Python入門』</li>"
```

複数行は `f"""..."""` を使う：

```python
return f"""
<h1>{title}</h1>
<p>{author}</p>
"""
```

---

## 3. `b` がどこで定義されているか（ジェネレータ式）

**疑問：** `f"<li>{b['title']}</li>" for b in results` の `b` はどこで定義？

**答え：** 右の `for b in results` が `b` の定義。右から左に読む。

```python
# 普通のforループと同じ意味
items = []
for b in results:           # ← b はここで定義される
    items.append(f"<li>{b['title']}</li>")

# 1行で書くと（ジェネレータ式）
items = (f"<li>{b['title']}</li>"  for b in results)
#        ↑ bを使う処理             ↑ bの定義（右が先）
```

読む順番：**② `for b in results` でbを定義 → ① bで文字列を作る**

---

## 4. `"".join()` の使い方

リストの要素を1つの文字列に連結する。

```python
items = ["<li>Python</li>", "<li>DB概論</li>"]

"".join(items)     # → "<li>Python</li><li>DB概論</li>"  （区切りなし）
", ".join(items)   # → "<li>Python</li>, <li>DB概論</li>" （カンマ区切り）
```

---

## 5. `or` の使い方（空文字はFalse）

```python
# results が空のとき join の結果は "" （空文字）
"" or "<li>なし</li>"               # → "<li>なし</li>"

# results に中身があるとき
"<li>Python</li>" or "<li>なし</li>" # → "<li>Python</li>"
```

Pythonでは空文字 `""` は `False` 扱い。`or` は左が False のとき右を返す。

### まとめ（全部つなげると）

```python
books_html = "".join(f"<li>『{b['title']}』</li>" for b in results) or "<li>なし</li>"
# resultsに本がある → "<li>『Python入門』</li><li>『DB概論』</li>"
# resultsが空       → "<li>なし</li>"
```

---

## 6. returnの後のHTMLフォーム解説

### フォームタグ

```html
<form method="GET" action="/search">
```

- `method="GET"` → 送信するとURLに `?keyword=xxx` が付く
- `action="/search"` → `/search` に送信する

### input タグ

```html
<input type="text" name="keyword" value="{keyword}">
```

- `name="keyword"` → URLパラメータのキー名（`?keyword=xxx` の `keyword` 部分）
- `value="{keyword}"` → 検索後に入力欄に前の値を残す

### `dict(request.args)` の変換

```python
# /search?keyword=Python のとき
request.args        # → ImmutableMultiDict（Flaskの独自型）
dict(request.args)  # → {'keyword': 'Python'}（見やすい辞書）
```

### `<ul>` と `<li>`

```html
<ul>
  <li>Python入門</li>
  <li>DB概論</li>
</ul>
```

- `<ul>` = リストの外枠
- `<li>` = 各行（ブラウザが箇条書きとして表示）

---

## 演習2の全体の流れ

```
① keyword, author を URL から取り出す（request.args）
② BOOKSリストを絞り込んで results に入れる（普通のPython）
③ results を <li>タグのHTML文字列に変換して books_html に入れる
④ return で フォーム + 結果一覧のHTMLを文字列として返す
⑤ ブラウザが受け取ってページとして表示する
```
