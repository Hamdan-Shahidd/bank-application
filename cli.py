from banking import Bank
from storage import SqliteStorage
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

if __name__ == "__main__":
    App(Bank(SqliteStorage())).run()