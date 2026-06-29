"""
================================================
database.py  ―  データベース初期化モジュール
================================================

【発表用説明】
このファイルはシステム起動時に一度だけ実行され、
SQLite データベースと4つのテーブルを作成します。

SQLite とは？
  - ファイル1つで動作する軽量データベース
  - Python 標準ライブラリに含まれており、追加インストール不要
  - 今回は library.db というファイルに全データを保存する

3層アーキテクチャにおける位置づけ：
  このファイルは「データ層」の初期化を担います。
"""

import sqlite3  # Python 標準の SQLite ライブラリ
import os

# データベースファイルのパス（このファイルと同じフォルダに作成される）
DB_PATH = os.path.join(os.path.dirname(__file__), "library.db")


def get_connection():
    """
    データベースへの接続を返す関数

    sqlite3.Row を指定することで、カラム名でデータを取り出せるようになる。
    例: row["title"] のようにアクセス可能（row[0] より分かりやすい）
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 辞書のようにカラム名でアクセスできる設定
    return conn


def init_db():
    """
    データベースとテーブルを初期化する関数

    【発表用説明】
    CREATE TABLE IF NOT EXISTS を使うことで、
    すでにテーブルが存在する場合はスキップされ、
    何度実行しても安全に動作します。

    テーブル設計は要求定義書 §6 のDB設計に基づいています。
    """
    conn = get_connection()
    cursor = conn.cursor()  # SQL文を実行するためのカーソルオブジェクト

    # ==========================================
    # BOOKS テーブル（蔵書情報）
    # ==========================================
    # 要求定義書 FR-15: 管理者は蔵書を登録・編集・削除できる
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BOOKS (
            book_id         INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主キー（自動採番）
            isbn            TEXT,                               -- 国際標準図書番号
            title           TEXT NOT NULL,                      -- 書名（必須）
            author          TEXT NOT NULL,                      -- 著者名（必須）
            category        TEXT,                               -- 分類（例: 情報工学, 数学）
            total_copies    INTEGER NOT NULL DEFAULT 1,         -- 総冊数
            available_copies INTEGER NOT NULL DEFAULT 1        -- 現在の貸出可能冊数
        )
    """)

    # ==========================================
    # MEMBERS テーブル（利用者情報）
    # ==========================================
    # 要求定義書 FR-16: 管理者は利用者を登録・編集・削除できる
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MEMBERS (
            member_id       INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主キー（自動採番）
            name            TEXT NOT NULL,                      -- 氏名（必須）
            email           TEXT NOT NULL UNIQUE,              -- メールアドレス（重複不可）
            registered_at   TEXT NOT NULL                       -- 登録日時（ISO形式の文字列）
        )
    """)

    # ==========================================
    # LOANS テーブル（貸出・返却記録）
    # ==========================================
    # 要求定義書 FR-05, 06, 07: 貸出・返却登録と返却期限の自動設定
    # BOOKS と MEMBERS を外部キーで参照（リレーション）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS LOANS (
            loan_id         INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主キー
            book_id         INTEGER NOT NULL,                   -- どの本か（外部キー）
            member_id       INTEGER NOT NULL,                   -- 誰が借りたか（外部キー）
            loaned_at       TEXT NOT NULL,                      -- 貸出日時
            due_date        TEXT NOT NULL,                      -- 返却期限（貸出日 + 14日）
            returned_at     TEXT,                               -- 返却日時（NULLなら未返却）
            FOREIGN KEY (book_id)   REFERENCES BOOKS(book_id),
            FOREIGN KEY (member_id) REFERENCES MEMBERS(member_id)
        )
    """)

    # ==========================================
    # RESERVATIONS テーブル（予約情報）
    # ==========================================
    # 要求定義書 FR-09: 利用者は貸出中の蔵書を予約できる
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RESERVATIONS (
            reservation_id  INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主キー
            book_id         INTEGER NOT NULL,                   -- 予約する本（外部キー）
            member_id       INTEGER NOT NULL,                   -- 予約した利用者（外部キー）
            reserved_at     TEXT NOT NULL,                      -- 予約日時
            FOREIGN KEY (book_id)   REFERENCES BOOKS(book_id),
            FOREIGN KEY (member_id) REFERENCES MEMBERS(member_id)
        )
    """)

    # サンプルデータを挿入（テーブルが空の場合のみ）
    cursor.execute("SELECT COUNT(*) FROM BOOKS")
    if cursor.fetchone()[0] == 0:
        _insert_sample_data(cursor)

    conn.commit()   # 変更をデータベースファイルに書き込む
    conn.close()    # 接続を閉じてリソースを解放
    print("データベースの初期化が完了しました。")


def _insert_sample_data(cursor):
    """
    動作確認用のサンプルデータを挿入する関数

    アンダースコア始まりの関数名は「このモジュール内だけで使う内部関数」を意味する慣習。
    """
    # サンプル蔵書
    books = [
        ("978-4-621-06504-5", "アルゴリズムとデータ構造",   "茨木俊秀",   "情報工学", 3, 3),
        ("978-4-274-06514-0", "Pythonチュートリアル",         "Guido van Rossum", "プログラミング", 2, 1),
        ("978-4-621-30637-2", "データベース概論",             "増永良文",   "情報工学", 2, 2),
        ("978-4-000-05115-4", "ソフトウェア工学",             "玉井哲雄",   "情報工学", 1, 0),
        ("978-4-621-06528-1", "コンピュータネットワーク",     "竹下隆史",   "ネットワーク", 2, 2),
    ]
    cursor.executemany(
        "INSERT INTO BOOKS (isbn, title, author, category, total_copies, available_copies) VALUES (?,?,?,?,?,?)",
        books
    )

    # サンプル利用者
    import datetime
    now = datetime.datetime.now().isoformat()
    members = [
        ("山田 太郎", "yamada@example.ac.jp",  now),
        ("鈴木 花子", "suzuki@example.ac.jp",  now),
        ("田中 次郎", "tanaka@example.ac.jp",  now),
    ]
    cursor.executemany(
        "INSERT INTO MEMBERS (name, email, registered_at) VALUES (?,?,?)",
        members
    )

    # サンプル貸出（山田が「Pythonチュートリアル」を借り中、期限切れ）
    import datetime
    loaned = (datetime.date.today() - datetime.timedelta(days=20)).isoformat()
    due    = (datetime.date.today() - datetime.timedelta(days=6)).isoformat()
    cursor.execute(
        "INSERT INTO LOANS (book_id, member_id, loaned_at, due_date, returned_at) VALUES (2, 1, ?, ?, NULL)",
        (loaned, due)
    )
