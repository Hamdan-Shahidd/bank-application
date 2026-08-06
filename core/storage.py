import random
import sqlite3
import threading
from pathlib import Path
from core.models import User


class SqliteStorage:
    def __init__(self, path=None):
        if path is None:
            path = str(Path(__file__).parent.parent / "data" / "bank.db")
        self.path = path
        self._local = threading.local()

        conn = self._connect()
        schema = Path(__file__).parent.parent / "schema.sql"
        with open(schema) as f:
            conn.executescript(f.read())

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @property
    def conn(self):
        if not hasattr(self._local, "conn"):
            self._local.conn = self._connect()
        return self._local.conn

    def _to_user(self, row):
        return User(
            username=row["username"],
            gmail=row["gmail"],
            account_number=row["account_number"],
            password=row["password"],
            balance=row["balance"],
            user_id=row["id"],
        )

    def create(self, user, attempts=5):
        for _ in range(attempts):
            user.account_number = str(random.randint(10**9, 10**10 - 1))
            try:
                with self.conn:
                    cur = self.conn.execute(
                        "INSERT INTO users (username, gmail, account_number, password, balance)"
                        " VALUES (?, ?, ?, ?, ?)",
                        (user.username, user.gmail, user.account_number,
                         user.password, user.balance),
                    )
                user.user_id = cur.lastrowid
                return user
            except sqlite3.IntegrityError:
                continue
        raise RuntimeError("Could not allocate an account number")

    def find_by_gmail(self, gmail):
        row = self.conn.execute(
            "SELECT * FROM users WHERE gmail = ?", (gmail,)).fetchone()
        return self._to_user(row) if row else None

    def find_by_account(self, account_number):
        row = self.conn.execute(
            "SELECT * FROM users WHERE account_number = ?", (account_number,)).fetchone()
        return self._to_user(row) if row else None

    def find_by_id(self, user_id):
        row = self.conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._to_user(row) if row else None

    def record_deposit(self, user, amount):
        with self.conn:
            self.conn.execute(
                "UPDATE users SET balance = ? WHERE id = ?",
                (user.balance, user.user_id)
            )
            self.conn.execute(
                "INSERT INTO transactions (sender_id, recipient_id, amount, kind)"
                " VALUES (NULL, ?, ?, 'deposit')",
                (user.user_id, amount)
            )

    def record_withdrawal(self, user, amount):
        with self.conn:
            self.conn.execute(
                "UPDATE users SET balance = ? WHERE id = ?",
                (user.balance, user.user_id)
            )
            self.conn.execute(
                "INSERT INTO transactions (sender_id, recipient_id, amount, kind)"
                " VALUES (?, NULL, ?, 'withdrawal')",
                (user.user_id, amount)
            )

    def record_transfer(self, sender, recipient, amount):
        with self.conn:
            self.conn.execute(
                "UPDATE users SET balance = ? WHERE id = ?",
                (sender.balance, sender.user_id)
            )
            self.conn.execute(
                "UPDATE users SET balance = ? WHERE id = ?",
                (recipient.balance, recipient.user_id)
            )
            self.conn.execute(
                "INSERT INTO transactions (sender_id, recipient_id, amount, kind)"
                " VALUES (?, ?, ?, 'transfer')",
                (sender.user_id, recipient.user_id, amount)
            )

    def history_for(self, user_id, limit=20):
        rows = self.conn.execute(
            "SELECT * FROM transactions"
            " WHERE sender_id = ? OR recipient_id = ?"
            " ORDER BY created_at DESC LIMIT ?",
            (user_id, user_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]