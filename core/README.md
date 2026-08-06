CORE: 
Contains all the buisness logic. 
It only knows about bank account and money. 

- models.py: It defines a user object in python's memory. Contains hash pasword, deposit, widraw, check_password and a property called balance_display.

- banking.py: This file knows the buisness rules. Contain log_in, sign_in, deposit, widraw, transfer and get_history. When the FastAPI wants someone to log_in it asks the Bank.log_in()

- storage.py: Only file in the project that is allowed to write SQL. It's entire job is translating between python object and rows in the database.

- __init__.py: It marks the folder as a python package from which you can import files.