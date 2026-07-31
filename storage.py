import sqlite3
import random
from pathlib import Path
from models import User

# Below is tge SQLite storage class.(UNDERSTAND)
class SqliteStorage:
    def __init__(self, path="bank.db"):
        self.conn = sqlite3.connect(path , check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        schema = Path(__file__).parent / "schema.sql"
        with open(schema) as f:
            self.conn.executescript(f.read())

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