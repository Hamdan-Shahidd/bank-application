import random
import sqlite3
import hashlib, os, hmac
from pathlib import Path



def hash_password(password):
    salt = os.urandom(16)
    h = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{salt.hex()}:{h.hex()}"

class User:
    def __init__(self,username,gmail,account_number,password,balance=0,user_id=None):
        self.user_id = user_id
        self.username = username
        self.gmail = gmail
        self.account_number = account_number
        self.password = password
        self.balance = balance

    def check_password(self, password):
        salt_hex, hash_hex = self.password.split(":")
        h = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1)
        return hmac.compare_digest(h.hex(), hash_hex)
    
    def deposit(self , ammount):
        if ammount<=0:
            raise ValueError("Ammount must be greater than 0.")
        self.balance+=ammount

    def widraw(self , ammount):
        if ammount<=0:
            raise ValueError("Ammount must be greater than 0.")
        if ammount > self.balance:
            raise ValueError("Ammount greater than available balance.")
        self.balance-=ammount

# Below is tge SQLite storage class.(UNDERSTAND)
class SqliteStorage:
    def __init__(self, path="bank.db"):
        self.conn = sqlite3.connect(path)
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

class Bank:
    def __init__(self , storage):
        self.storage = storage

    def find(self , gmail):
        return self.storage.find_by_gmail(gmail)

    def find_by_account(self , account_number):
        return self.storage.find_by_account(account_number)

    def sign_up(self , username , gmail , password):
        if self.find(gmail):
            raise ValueError("Gmail already taken")

        user = User(username , gmail , None , hash_password(password))
        return self.storage.create(user)
    
    def log_in(self , username , password):
        user = self.find(username)
        if user is None or not user.check_password(password):
            raise ValueError("Invalid Credentials")
        return user

    def transfer(self , sender , recipient_account , amount):
        recipient = self.find_by_account(recipient_account)
        if recipient is None:
            raise ValueError("Mo user with this credentials")
        if recipient.user_id == sender.user_id:
            raise ValueError("Can't send ammount to yourself")
        sender.widraw(amount)
        recipient.deposit(amount)
        self.storage.update(sender , recipient)
        return recipient
    def deposit(self, user, amount):
        user.deposit(amount)
        self.storage.update(user)
        return user

class App:
    def __init__(self , bank):
        self.bank = bank

    def run(self):
        while True:
            option = input("\nSelect the option: 1. Sign up 2. Log in 3. Exit")
            match option:
                case "1":
                    self.sign_up_screen()
                case "2":
                    self.log_in_screen()
                case "3":
                    print("Goodbye")
                    break
                case _:
                    print("Please chose 1, 2, or 3")

    def sign_up_screen(self):
        username = input("Enter your username: ")
        gmail = input("Enter your gmail: ")
        password = input("Enter your password: ")
        try:
            user = self.bank.sign_up(username,gmail,password)
        except (ValueError , RuntimeError) as v:
            print(v)
            return
        print(f"User created successfully. Your account number is {user.account_number}")

    def log_in_screen(self):
        gmail = input("Enter your gmail: ")
        pin = input("Enter your pasword: ")
        try:
            user = self.bank.log_in(gmail , pin)
        except ValueError as v:
            print(v)
            return
        print("Looged in successfully")
        self.account_menu(user)

    def account_menu(self , user):
        while True:
            choice = input("\nChoose the option: \n1.Check Balance \n2.Deposit Money \n3.Transfer Funds \n4.Log out")
            match choice:
                case "1":
                    print(f"Balance: {user.balance}")
                case "2":
                    self.deposit_screen(user)
                case "3":
                    self.transfer_screen(user)
                case "4":
                    print("Logging out")
                    return
                case _:
                    print("Choose the right option 1,2,3 or 4")

    def ask_ammount(self , question):
        amount = input(question)
        if not amount.isdecimal() or int(amount) == 0:
            print("Enter the value greater than 0.")
            return None
        return int(amount)

    def deposit_screen(self, user):
        amount = self.ask_ammount("Enter the amount to deposit: ")
        if amount is None:
            return
        try:
            self.bank.deposit(user, amount)
        except ValueError as e:
            print(e)
            return
        print(f"{amount} deposited successfully")

    def transfer_screen(self,user):
        recipient_account = input("Enter the recipients account number: ")
        amount = self.ask_ammount("Enter the amount: ")
        if amount is None:
            return
        try:
            self.bank.transfer(user,recipient_account ,amount)
        except ValueError as e:
            print(e)
            return
        print(f"Ammount Transfered successfully to {recipient_account}")

App(Bank(SqliteStorage())).run()
