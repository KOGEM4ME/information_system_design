"""
================================================
app.py  ―  Flaskアプリケーション（プレゼンテーション層）
================================================

【発表用説明】
このファイルはシステムの「入口」です。
ブラウザからのリクエストを受け取り、適切な画面を返す役割を担います。

Flask とは？
  Python で Web アプリを作るための軽量フレームワーク。
  「ルーティング」= URL と処理を結びつける仕組みを提供します。

3層アーキテクチャにおける位置づけ：
  このファイルは「プレゼンテーション層」と「アプリケーション層」を担います。
  - URL を受け取り（プレゼンテーション層）
  - models.py の関数を呼び出してビジネスロジックを実行（アプリケーション層）
  - 結果を HTML テンプレートに渡して表示（プレゼンテーション層）

起動方法:
  python app.py
  → http://127.0.0.1:5000 でアクセスできる
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db
import models

# Flask アプリケーションのインスタンスを生成
# __name__ により、このファイルがあるディレクトリを基準にテンプレートを探す
app = Flask(__name__)

# flash（通知メッセージ）を使うためにシークレットキーが必要
# 本番環境では推測されにくいランダムな文字列にすること
app.secret_key = "library-system-secret-2026"


# ==================================================
# トップページ
# ==================================================

@app.route("/")
def index():
    """トップページ → 蔵書検索ページへリダイレクト"""
    return redirect(url_for("search"))


# ==================================================
# 蔵書検索（FR-01, FR-02, FR-03）
# ==================================================

@app.route("/search")
def search():
    """
    蔵書検索ページ

    【発表用説明】
    GET パラメータ（URL の ?keyword=xxx&author=yyy）を受け取り、
    models.search_books() でデータベースを検索して結果を表示します。

    URL 例: /search?keyword=Python&author=&category=
    """
    # URL パラメータから検索条件を取得（未入力は空文字列）
    keyword  = request.args.get("keyword",  "").strip()
    author   = request.args.get("author",   "").strip()
    category = request.args.get("category", "").strip()

    # 何か入力があれば検索、なければ全件表示
    books = models.search_books(keyword, author, category)

    return render_template(
        "search.html",
        books=books,
        keyword=keyword,
        author=author,
        category=category
    )


# ==================================================
# 貸出登録（FR-05, FR-07）
# ==================================================

@app.route("/loan", methods=["GET", "POST"])
def loan():
    """
    貸出登録ページ

    【発表用説明】
    HTTP メソッドが2種類あります：
      GET  → 貸出登録フォームを表示する
      POST → フォームの送信内容を処理して貸出登録を実行する

    この「GET でフォーム表示、POST でデータ処理」のパターンは
    Web アプリ開発の基本的な設計パターンです。
    """
    members = models.get_all_members()  # フォームのプルダウン用
    books   = models.get_all_books()    # フォームのプルダウン用

    if request.method == "POST":
        # フォームから利用者IDと蔵書IDを受け取る
        member_id = request.form.get("member_id")
        book_id   = request.form.get("book_id")

        # models 層に貸出処理を依頼
        success, message = models.loan_book(book_id, member_id)

        # flash() で次のページに通知メッセージを渡す
        flash(message, "success" if success else "danger")

        # PRG パターン: POST 後は GET にリダイレクトして二重送信を防ぐ
        return redirect(url_for("loan"))

    return render_template("loan.html", members=members, books=books)


# ==================================================
# 返却登録（FR-06）
# ==================================================

@app.route("/return", methods=["GET", "POST"])
def return_book():
    """
    返却登録ページ

    職員が蔵書IDを入力して返却処理を行います。
    """
    books = models.get_all_books()

    if request.method == "POST":
        book_id = request.form.get("book_id")
        success, message = models.return_book(book_id)
        flash(message, "success" if success else "danger")
        return redirect(url_for("return_book"))

    return render_template("return.html", books=books)


# ==================================================
# 延滞一覧（FR-12）
# ==================================================

@app.route("/overdue")
def overdue():
    """
    延滞一覧ページ

    【発表用説明】
    models.get_overdue_list() が SQL で延滞日数を計算して返します。
    職員はこの画面で延滞者を一目で確認できます。
    """
    overdue_list = models.get_overdue_list()
    return render_template("overdue.html", overdue_list=overdue_list)


# ==================================================
# 管理画面：蔵書管理（FR-15）
# ==================================================

@app.route("/admin/books", methods=["GET", "POST"])
def admin_books():
    """蔵書の一覧表示・新規登録"""
    if request.method == "POST":
        isbn         = request.form.get("isbn", "")
        title        = request.form.get("title", "")
        author       = request.form.get("author", "")
        category     = request.form.get("category", "")
        total_copies = int(request.form.get("total_copies", 1))

        models.add_book(isbn, title, author, category, total_copies)
        flash(f"「{title}」を登録しました", "success")
        return redirect(url_for("admin_books"))

    books = models.get_all_books()
    return render_template("admin_books.html", books=books)


@app.route("/admin/books/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    """蔵書を削除する"""
    models.delete_book(book_id)
    flash("蔵書を削除しました", "success")
    return redirect(url_for("admin_books"))


# ==================================================
# 管理画面：利用者管理（FR-16）
# ==================================================

@app.route("/admin/members", methods=["GET", "POST"])
def admin_members():
    """利用者の一覧表示・新規登録"""
    if request.method == "POST":
        name  = request.form.get("name", "")
        email = request.form.get("email", "")

        models.add_member(name, email)
        flash(f"利用者「{name}」を登録しました", "success")
        return redirect(url_for("admin_members"))

    members = models.get_all_members()
    return render_template("admin_members.html", members=members)


@app.route("/admin/members/delete/<int:member_id>", methods=["POST"])
def delete_member(member_id):
    """利用者を削除する"""
    models.delete_member(member_id)
    flash("利用者を削除しました", "success")
    return redirect(url_for("admin_members"))


# ==================================================
# アプリケーション起動
# ==================================================

if __name__ == "__main__":
    # アプリ起動時にデータベースを初期化（テーブルが無ければ作成）
    init_db()

    # debug=True にすることで、コード変更時に自動リロードされる（開発時便利）
    # 本番環境では debug=False にすること
    app.run(debug=True)
