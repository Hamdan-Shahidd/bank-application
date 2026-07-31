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