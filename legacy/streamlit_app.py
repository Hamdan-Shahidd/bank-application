# Phase 07 remaining.
import sys
import streamlit as st
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.banking import Bank
from core.storage import SqliteStorage
from ai.agent import interpret

st.set_page_config(page_title="Bank", page_icon="🏦")

@st.cache_resource # Without thi the return statement will run everytime, opening a new database connection everytime a user clicks.
def get_bank():
    return Bank(SqliteStorage())

bank = get_bank()
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "pending" not in st.session_state: 
    st.session_state.pending = None

if st.session_state.user_id is None:
    st.subheader("Welcome")
    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        gmail = st.text_input("Email", key="login_gmail")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Log in"):
            try:
                user = bank.log_in(gmail, password)
                st.session_state.user_id = user.user_id
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    with tab_signup:
        username = st.text_input("Username", key="su_name")
        su_gmail = st.text_input("Email", key="su_gmail")
        su_pw = st.text_input("Password", type="password", key="su_pw")
        if st.button("Create account"):
            try:
                user = bank.sign_up(username, su_gmail, su_pw)
                st.success(f"Account created. Your account number is {user.account_number}")
            except (ValueError, RuntimeError) as e:
                st.error(str(e))

    st.stop()

user = bank.storage.find_by_id(st.session_state.user_id)
if user is None:
    st.session_state.user_id = None
    st.rerun()

st.title(f"Hello, {user.username}")

col1, col2 = st.columns(2)
col1.metric("Balance", user.balance)
col2.metric("Account number", user.account_number)

if st.button("Log out"):
    st.session_state.user_id = None
    st.session_state.pending = None
    st.rerun()

st.divider()
tab_deposit, tab_transfer = st.tabs(["Deposit", "Transfer"])

with tab_deposit:
    with st.form("deposit_form"):
        amount = st.number_input("Amount", min_value=1, step=1, key="dep_amt")
        if st.form_submit_button("Deposit"):
            try:
                bank.deposit(user, int(amount))
                st.success(f"{int(amount)} deposited")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

with tab_transfer:
    with st.form("transfer_form"):
        account = st.text_input("Recipient account number")
        amount = st.number_input("Amount", min_value=1, step=1, key="tr_amt")
        if st.form_submit_button("Send"):
            try:
                bank.transfer(user, account, int(amount))
                st.success("Transfer complete")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
st.divider()
st.subheader("Assistant")

#  Agent Part: 
msg = st.chat_input("Ask about your account or bank policy")

if msg:
    kind, payload = interpret(msg)

    if kind == "propose_transfer":
        st.session_state.pending = payload

    elif kind == "get_account_details":
        # User comes from session — model never touches this
        st.info(
            f"**Account Details**\n\n"
            f"- **Name:** {user.username}\n"
            f"- **Account Number:** {user.account_number}\n"
            f"- **Balance:** {user.balance}"
        )

    else:
        st.info(payload)

if st.session_state.pending:
    p = st.session_state.pending
    st.warning(f"Send {p['amount']} to account {p['recipient_account']}?")

    c1, c2 = st.columns(2)
    if c1.button("Confirm"):
        pending = st.session_state.pending
        st.session_state.pending = None
        try:
            bank.transfer(user, pending["recipient_account"], int(pending["amount"]))
            st.success("Transfer complete")
        except ValueError as e:
            st.error(str(e))
        st.rerun()

    if c2.button("Cancel"):
        st.session_state.pending = None
        st.rerun()
