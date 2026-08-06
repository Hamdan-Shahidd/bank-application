from models import User , hash_password

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

    def deposit(self, user, amount_in_units):
        amount_cents = amount_in_units * 100
        user.deposit(amount_cents)
        self.storage.record_deposit(user, amount_cents)
        return user

    def withdraw(self, user, amount_in_units):
        amount_cents = amount_in_units * 100
        user.widraw(amount_cents)
        self.storage.record_withdrawal(user, amount_cents)
        return user

    def transfer(self, sender, recipient_account, amount_in_units):
        amount_cents = amount_in_units * 100
        recipient = self.find_by_account(recipient_account)
        if recipient is None:
            raise ValueError("No user with this account number")
        if recipient.user_id == sender.user_id:
            raise ValueError("Can't send amount to yourself")
        sender.widraw(amount_cents)
        recipient.deposit(amount_cents)
        self.storage.record_transfer(sender, recipient, amount_cents)
        return recipient

    def get_history(self, user):
        return self.storage.history_for(user.user_id)