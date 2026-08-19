from core.models import User, hash_password
from logging_config import logger

class Bank:
    def __init__(self, storage):
        self.storage = storage

    def find(self, gmail):
        return self.storage.find_by_gmail(gmail)

    def find_by_account(self, account_number):
        return self.storage.find_by_account(account_number)

    def sign_up(self, username, gmail, password):
        if self.find(gmail):
            logger.warning(f"SIGNUP REJECTED | gmail={gmail} | reason:gmail already registered")
            raise ValueError("Gmail already taken")
        user = User(username, gmail, None, hash_password(password))
        created = self.storage.create(user)
        logger.info(f"SIGNUP | user_id={created.user_id} | username={username}")
        return created

    def log_in(self, gmail, password):
        user = self.find(gmail)
        if user is None or not user.check_password(password):
            logger.warning(f"LOGIN FAILED | gmail={gmail} | reason=invalid credentials")
            raise ValueError("Invalid Credentials")

        logger.info(f"LOGIN SUCCESS | user_id={user.user_id}")
        return user

    def deposit(self, user, amount):
        amount_cents = amount * 100
        user.deposit(amount_cents)
        self.storage.record_deposit(user, amount_cents)
        logger.info(f"DEPOSIT | user_id={user.user_id} | amount={amount_cents} cents | new_balance={user.balance}")
        return user

    def withdraw(self, user, amount):
        amount_cents = amount * 100
        try:
            user.widraw(amount_cents)
        except ValueError as e:
            logger.warning(f"WITHDRAWAL REJECTED | user_id={user.user_id} | amount={amount_cents} cents | reason={e}")
            raise
        
        self.storage.record_withdrawal(user, amount_cents)
        logger.info(f"WITHDRAWAL | user_id={user.user_id} | amount={amount_cents} cents | new_balance={user.balance}")
        return user

    def transfer(self, sender, recipient_account, amount):
        amount_cents = amount * 100
        recipient = self.find_by_account(recipient_account)
        if recipient is None:
            logger.warning(f"TRANSFER REJECTED | user_id={sender.user_id} | reason=no such account | target={recipient_account}")
            raise ValueError("No user with this account number")
        if recipient.user_id == sender.user_id:
            logger.warning(f"TRANSFER REJECTED | user_id={sender.user_id} | reason=self-transfer attempt")
            raise ValueError("Can't send amount to yourself")

        try:
            sender.widraw(amount_cents)
        except ValueError as e:
            logger.warning(f"TRANSFER REJECTED | user_id={sender.user_id} | amount={amount_cents} cents | reason={e}")
            raise

        recipient.deposit(amount_cents)
        self.storage.record_transfer(sender, recipient, amount_cents)
        logger.info(
        f"TRANSFER | sender={sender.user_id} | recipient={recipient.user_id} | "
        f"amount={amount_cents} cents | sender_new_balance={sender.balance}"
        )
        return recipient

    def get_history(self, user):
        return self.storage.history_for(user.user_id)

    def query_transactions(self , user , condition):
        return self.storage.query_transactions_filtered(user.user_id , condition)
    