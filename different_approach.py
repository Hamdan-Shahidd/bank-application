while True:
    option = input("Select the option: 1. Sign up 2. Log in ")
    match option:
        case "1":
            username = input("Enter username? ")
            gmail = input("Enter gmail? ")
            account_number = input("Enter account number? ")
            password = input("Enter password? ")
            balance = 0
            with open("users.txt", "a") as file:
                file.write(f"{username},{gmail},{account_number},{password},{balance}\n")
            print("User created successfully\n")

        case "2":
            name = input("Enter your name? ")
            pin = input("Enter the pin? ")
            logged_in = False
            with open("users.txt", "r") as file:
                users = file.readlines()

            for i in range(len(users)):
                user, gmail, num, pw, bal = users[i].strip().split(",")
                bal = int(bal)

                if name == user and pin == pw:
                    print("Logged in successfully")
                    logged_in = True

                    while True:
                        choice = input(
                            "Choose one of the following: "
                            "\n1. Check Balance"
                            "\n2. Deposit Money"
                            "\n3. Transfer Funds"
                            "\n4. Log out\n"
                        )

                        if choice == "1":
                            print(f"Balance: {bal}")

                        elif choice == "2":
                            amount = input("Enter the amount to deposit: ")
                            if not amount.isdigit() or int(amount) == 0:
                                print("Enter a whole number greater than zero.")
                                continue

                            bal += int(amount)
                            users[i] = f"{user},{gmail},{num},{pw},{bal}\n"
                            with open("users.txt", "w") as file:
                                file.writelines(users)
                            print(f"{amount} deposited successfully")

                        elif choice == "3":
                            recipient_name = input("Enter the account number to send to: ")
                            amount = input("Enter the amount: ")

                            if not amount.isdigit() or int(amount) == 0:
                                print("Enter a whole number greater than zero.")
                                continue

                            amount = int(amount)

                            if recipient_name == user:
                                print("You cannot transfer to yourself.")
                                continue
                            if amount > bal:
                                print("Insufficient funds.")
                                continue

                            recipient_index = -1
                            for j in range(len(users)):
                                if users[j].strip().split(",")[0] == recipient_name:
                                    recipient_index = j
                                    break

                            if recipient_index == -1:
                                print("No user with that account number")
                                continue

                            bal -= amount
                            users[i] = f"{user},{gmail},{num},{pw},{bal}\n"

                            r_user, r_gmail, r_num, r_pw, r_bal = users[recipient_index].strip().split(",")
                            r_bal = int(r_bal) + amount
                            users[recipient_index] = f"{r_user},{r_gmail},{r_num},{r_pw},{r_bal}\n"

                            with open("users.txt", "w") as file:
                                file.writelines(users)

                            print("Amount transferred successfully.")

                        elif choice == "4":
                            print("Logging out")
                            break

                        else:
                            print("Invalid choice, choose from 1, 2, 3 or 4")

                    break

            if not logged_in:
                print("Invalid credentials")

        case _:
            print("Please choose 1 or 2.")