import sqlite3
import random
import threading
from pathlib import Path
from models import User

# Below is tge SQLite storage class.(UNDERSTAND)
class SqliteStorage:
    def __init__(self, path="bank.db"):
        self.path = path
        self._local = threading.local()
        conn = self._connect()
        schema = Path(__file__).parent / "schema.sql"
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
    
    def load_all(self):
        # fetchall() pulls every row into  the list and then each row is rebuld into a USER object
        rows = self.conn.execute("SELECT * FROM users").fetchall()
        # These are positional matching user.__init__(username,gmail,account_number,password,balance,user_id)
        # Hydration step: Converting database tuples into User Objects
        return [
            User(r["username"], r["gmail"], r["account_number"],
                 r["password"], r["balance"], r["id"])
            for r in rows
        ]
    # Attemopy is a retry budget
    def create(self, user, attempts=5):
        # generates a 10 digit number. No pre-check that it is free (daatabse decides)
        for _ in range(attempts):
            user.account_number = str(random.randint(10**9, 10**10 - 1))
            # ? are values passed as placeholders
            try:
                with self.conn:
                    cur = self.conn.execute(
                        "INSERT INTO users (username, gmail, account_number, password, balance)"
                        " VALUES (?, ?, ?, ?, ?)",
                        (user.username, user.gmail, user.account_number,
                         user.password, user.balance),
                    )
                # lastrowid just reports the id your sql auto-ass
                user.user_id = cur.lastrowid
                return user
            except sqlite3.IntegrityError:
                continue
        # Raised when a unique or not-null constraint is voilated
        raise RuntimeError("Could not allocate an account number")

    # Perform both function for update(user) from a deposit and update(sender,recipient) from transfer.
    def update(self, *users):
        with self.conn:
            for user in users:
                self.conn.execute(
                    "UPDATE users SET balance = ? WHERE id = ?",
                    (user.balance, user.user_id),
                )

    def _to_user(self, row):
        return User(
            username=row["username"],
            gmail=row["gmail"],
            account_number=row["account_number"],
            password=row["password"],
            balance=row["balance"],
            user_id=row["id"],
        )

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

    