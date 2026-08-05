from retriver import retrieve_policy
questions = [
    "what happens if my account is inoperative?" ,
    "how do I close my account?",
    "are their charges for ATM widrawals?",
    "who invented electricity?"
]
for q in questions:
    print(f"\nQ: {q}")
    print(retrieve_policy(q))
    print("-"*40)