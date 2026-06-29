"""
================================================
models.py  ―  データアクセス層（Model）
================================================

【発表用説明】
このファイルは「データ層」を担当します。
SQLite データベースへの問い合わせ（CRUD操作）をすべてここにまとめています。

CRUD とは？
  Create（登録）/ Read（検索・取得）/ Update（更新）/ Delete（削除）
  データベース操作の基本4種類の頭文字です。

設計のポイント：
  app.py（ルーティング）からは直接SQLを書かず、
  このファイルの関数を呼び出す構造にしています。
  → 「関心の分離」により、コードが読みやすく保守しやすくなります。
"""

import datetime
from database import get_connection


# ==================================================
# 蔵書（BOOKS）関連
# ==================================================

def search_books(keyword="", author="", category=""):
    """
    蔵書を検索して結果リストを返す関数（FR-01, FR-02, FR-03対応）

    【発表用説明】
    SQL の LIKE 演算子を使い、部分一致検索を実現しています。
    例: keyword="Python" → タイトルや著者に "Python" を含む本を検索

    引数:
        keyword  : 書名・キーワードで絞り込む文字列
        author   : 著者名で絞り込む文字列
        category : カテゴリで絞り込む文字列

    戻り値:
        検索にマッチした蔵書のリスト（辞書形式）
    """
    conn = get_connection()
    cursor = conn.cursor()

    # WHERE 句を動的に組み立てる（AND検索 = FR-03）
    conditions = []
    params = []

    if keyword:
        # LIKE '%値%' で部分一致（前後の % がワイルドカード）
        conditions.append("(title LIKE ? OR isbn LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if author:
        conditions.append("author LIKE ?")
        params.append(f"%{author}%")
    if category:
        conditions.append("category LIKE ?")
        params.append(f"%{category}%")

    # 条件がある場合は WHERE 句として結合、なければ全件取得
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    sql = f"SELECT * FROM BOOKS {where} ORDER BY title"

    cursor.execute(sql, params)
    books = cursor.fetchall()
    conn.close()
    return books


def get_all_books():
    """全蔵書を取得する（管理画面用）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM BOOKS ORDER BY book_id")
    books = cursor.fetchall()
    conn.close()
    return books


def get_book_by_id(book_id):
    """指定IDの蔵書1件を取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM BOOKS WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    conn.close()
    return book


def add_book(isbn, title, author, category, total_copies):
    """
    蔵書を新規登録する（FR-15対応）

    新規登録時は available_copies（貸出可能冊数）= total_copies（総冊数）とする。
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO BOOKS (isbn, title, author, category, total_copies, available_copies) VALUES (?,?,?,?,?,?)",
        (isbn, title, author, category, total_copies, total_copies)
    )
    conn.commit()
    conn.close()


def delete_book(book_id):
    """蔵書を削除する（FR-15対応）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM BOOKS WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()


# ==================================================
# 利用者（MEMBERS）関連
# ==================================================

def get_all_members():
    """全利用者を取得する（管理画面・貸出登録画面用）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM MEMBERS ORDER BY member_id")
    members = cursor.fetchall()
    conn.close()
    return members


def get_member_by_id(member_id):
    """指定IDの利用者1件を取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM MEMBERS WHERE member_id = ?", (member_id,))
    member = cursor.fetchone()
    conn.close()
    return member


def add_member(name, email):
    """
    利用者を新規登録する（FR-16対応）

    registered_at に現在日時を自動でセットする。
    """
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO MEMBERS (name, email, registered_at) VALUES (?,?,?)",
        (name, email, now)
    )
    conn.commit()
    conn.close()


def delete_member(member_id):
    """利用者を削除する（FR-16対応）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM MEMBERS WHERE member_id = ?", (member_id,))
    conn.commit()
    conn.close()


# ==================================================
# 貸出（LOANS）関連
# ==================================================

def get_active_loan_count(member_id):
    """
    指定利用者の現在の貸出冊数を返す

    ビジネスルール「1人につき同時5冊まで」の確認に使用する。
    returned_at IS NULL = まだ返却されていない貸出レコード
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM LOANS WHERE member_id = ? AND returned_at IS NULL",
        (member_id,)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


def loan_book(book_id, member_id):
    """
    貸出を登録する（FR-05, FR-07対応）

    【発表用説明】
    処理の流れ：
      1. 貸出可能冊数（available_copies）が0でないか確認
      2. 利用者の現在の貸出冊数が上限（5冊）未満か確認
      3. LOANS テーブルに新規レコードを INSERT
      4. BOOKS の available_copies を 1 減らす（UPDATE）
      5. すべて成功したら commit（失敗したら rollback）

    戻り値:
        (成功: True, メッセージ) または (失敗: False, エラーメッセージ)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 蔵書の在庫確認
    cursor.execute("SELECT available_copies, title FROM BOOKS WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    if not book or book["available_copies"] <= 0:
        conn.close()
        return False, "この本は現在貸出できません（在庫なし）"

    # 利用者の貸出上限確認（ビジネスルール: 同時5冊まで）
    cursor.execute(
        "SELECT COUNT(*) FROM LOANS WHERE member_id = ? AND returned_at IS NULL",
        (member_id,)
    )
    if cursor.fetchone()[0] >= 5:
        conn.close()
        return False, "貸出上限（5冊）に達しています"

    # 延滞中の利用者は貸出停止（ビジネスルール: 7日以上延滞で停止）
    today = datetime.date.today().isoformat()
    cursor.execute(
        """SELECT COUNT(*) FROM LOANS
           WHERE member_id = ? AND returned_at IS NULL
           AND date(due_date, '+7 days') < ?""",
        (member_id, today)
    )
    if cursor.fetchone()[0] > 0:
        conn.close()
        return False, "延滞中の本があるため、新たな貸出はできません"

    # 貸出日・返却期限を設定（今日 + 14日 = FR-07）
    loaned_at = datetime.datetime.now().isoformat()
    due_date  = (datetime.date.today() + datetime.timedelta(days=14)).isoformat()

    # LOANS テーブルに記録を挿入
    cursor.execute(
        "INSERT INTO LOANS (book_id, member_id, loaned_at, due_date, returned_at) VALUES (?,?,?,?,NULL)",
        (book_id, member_id, loaned_at, due_date)
    )

    # 貸出可能冊数を 1 減らす
    cursor.execute(
        "UPDATE BOOKS SET available_copies = available_copies - 1 WHERE book_id = ?",
        (book_id,)
    )

    conn.commit()
    conn.close()
    return True, f"「{book['title']}」の貸出登録が完了しました。返却期限: {due_date}"


def return_book(book_id):
    """
    返却を登録する（FR-06対応）

    【発表用説明】
    処理の流れ：
      1. 指定の本の「未返却」レコードを LOANS から検索
      2. returned_at に現在日時を UPDATE（返却完了）
      3. BOOKS の available_copies を 1 増やす
      4. commit

    戻り値:
        (成功: True, メッセージ) または (失敗: False, エラーメッセージ)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 未返却のレコードを検索（returned_at IS NULL = まだ返却されていない）
    cursor.execute(
        """SELECT l.loan_id, b.title FROM LOANS l
           JOIN BOOKS b ON l.book_id = b.book_id
           WHERE l.book_id = ? AND l.returned_at IS NULL""",
        (book_id,)
    )
    loan = cursor.fetchone()
    if not loan:
        conn.close()
        return False, "この本の貸出記録が見つかりません"

    # 返却日時を記録
    returned_at = datetime.datetime.now().isoformat()
    cursor.execute(
        "UPDATE LOANS SET returned_at = ? WHERE loan_id = ?",
        (returned_at, loan["loan_id"])
    )

    # 貸出可能冊数を 1 増やす
    cursor.execute(
        "UPDATE BOOKS SET available_copies = available_copies + 1 WHERE book_id = ?",
        (book_id,)
    )

    conn.commit()
    conn.close()
    return True, f"「{loan['title']}」の返却登録が完了しました"


def get_overdue_list():
    """
    延滞中の貸出一覧を取得する（FR-12対応）

    【発表用説明】
    SQL の date() 関数と 'now' キーワードを使って、
    今日の日付と返却期限を比較しています。
    due_date < date('now') かつ returned_at IS NULL = 延滞中
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.date.today().isoformat()

    cursor.execute(
        """SELECT
               m.name        AS member_name,
               m.email       AS member_email,
               b.title       AS book_title,
               l.due_date,
               -- 延滞日数の計算: 今日 - 返却期限
               (julianday(?) - julianday(l.due_date)) AS overdue_days
           FROM LOANS l
           JOIN MEMBERS m ON l.member_id = m.member_id
           JOIN BOOKS   b ON l.book_id   = b.book_id
           WHERE l.returned_at IS NULL
             AND l.due_date < ?
           ORDER BY overdue_days DESC""",
        (today, today)
    )
    result = cursor.fetchall()
    conn.close()
    return result


def get_loan_history():
    """全貸出履歴を取得する（確認・管理用）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT l.loan_id, b.title, m.name, l.loaned_at, l.due_date, l.returned_at
           FROM LOANS l
           JOIN BOOKS b   ON l.book_id   = b.book_id
           JOIN MEMBERS m ON l.member_id = m.member_id
           ORDER BY l.loan_id DESC"""
    )
    result = cursor.fetchall()
    conn.close()
    return result
