import random
import sqlite3
import threading
from pathlib import Path
from core.models import User
from logging_config import logger
import re

"""
Their are ALLOWED_COLUMNS which can be referenced.
Any keyword that can write, modify or nest another query inside it's fragment is not allowed.
SELECT is banned to block sub-query attacks like union select. 
"""
ALLOWED_COLUMNS = {"amount" , "kind" , "created_at" , "sender_id" , "recipient_id"}
SAFE_KEYWORDS = {
    "AND", "OR", "NOT", "LIKE", "BETWEEN", "IN", "NULL", "IS",
    "DATE", "NOW", "START", "OF", "DAY", "DAYS", "MONTH", "MONTHS",
    "YEAR", "YEARS", "WEEK", "WEEKS",
}
FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|ATTACH|PRAGMA|CREATE|REPLACE|VACUUM|UNION|SELECT)\b",
    re.IGNORECASE,
)

def _validate_condition(fragment: str) -> bool:
    """
    Returns True only if the fragment is safe to embed in the WHERE clause.
    """
    if not fragment or ";" in fragment:
        logger.warning(f"SQL VALIDATOR REJECTED | reason=semicolon or empty | fragment={fragment!r}")
        return False

    stripped = re.sub(r"date\s*\([^()]*\)", "", fragment, flags=re.IGNORECASE)

    if "(" in stripped or ")" in stripped:
        logger.warning(f"SQL VALIDATOR REJECTED | reason=stray paarantheses | fragment={fragment!r}")
        return False

    if FORBIDDEN.search(fragment):
        logger.warning(f"SQL VALIDATOR REJECTED | reason=forbidden keyword | fragment={fragment!r}")
        return False

    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", fragment)
    for tok in tokens:
        if tok.upper() in SAFE_KEYWORDS:
            continue
        if tok in ALLOWED_COLUMNS:
            continue
        if tok in {"deposit", "withdrawal", "transfer"}:
            continue
        logger.warning(f"SQL VALIDATOR REJECTED | reason=unrecognized token '{tok}' | fragment={fragment!r}")
        return False
    return True


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

    """
    Used for Query Agent: 
    {condition} is the only part in the query where LLM plays a part. 
    """
    def query_transactions_filtered(self , user_id , condition):
        if not condition or not condition.strip():
            condition = "1=1"
        if not _validate_condition(condition):
            raise ValueError("This filter is not allowed")

        logger.info(f"SQL QUERY ACCEPTED | user_id={user_id} | condition={condition!r}")
        sql = f"""
            SELECT amount , kind , created_at , sender_id , recipient_id
            FROM transactions
            WHERE (sender_id = ? OR recipient_id = ?)
            AND ({condition})
            ORDER BY created_at DESC
            LIMIT 50
        """
        rows = self.conn.execute(sql, (user_id, user_id)).fetchall()
        return [dict(r) for r in rows]