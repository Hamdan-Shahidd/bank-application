import hashlib, os, hmac

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

    @property
    def balance_display(self):
        """Balance formatted as PKR 10.00"""
        return f"PKR {self.balance / 100:.2f}"