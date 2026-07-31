name = input("Enter your name? ")
gmail = input("Enter your gmail? ")
card_number = input("Please enter your card number? ")
password = input("Please enter your password? ")
balance = "0"
with open("users.txt" , "a") as file:
    file.write(f"{name},{gmail},{card_number},{password},{balance}\n")
print("User information saved!")

username = input("Enter your username? ")
pin = input("Enter your password? ")
logged_in = False

with open("users.txt" , "r") as file:
    users = file.readlines()
for i in range(len(users)):
    user,gmail,card_number,pw,balance = users[i].strip().split(",")
    if username == user and pin == pw:
        logged_in = True
        while True:
            print("1. Check Balance: \n")
            print("2. Deposit Money: \n")
            print("3. Log out: \n")
            option = input("Choose the option")
            if option == "1":
                print(f"The balance is {balance}")
            elif option == "2":
                deposited_ammount = input("Enter the ammount to be deposited")
                if not deposited_ammount.isdigit():
                    print("The entered ammount is not a digit.")
                    continue
                balance = str(int(balance) + int(deposited_ammount))
                users[i]=f"{name},{gmail},{card_number},{pw},{balance}\n"
                with open("users.txt" , "w") as file:
                    file.writelines(users)
                print("Money deposited")
            elif option == "3":
                print("Logged out")
                break
            else:
                print("Choose option 1, 2 or 3")
if not logged_in:
    print("Invalid credentials")
