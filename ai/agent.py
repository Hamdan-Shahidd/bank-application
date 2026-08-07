import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from ai.retriever import retrieve_policy

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.environ["GEMINI_API_KEY"],
)


@tool
def propose_transfer(recipient_account: str, amount: int) -> str:
    """Propose sending money to another account. Does not execute the transfer."""
    return "proposed"


@tool
def get_account_details() -> str:
    """Get the current user's account details including account number and balance."""
    return "fetched"

@tool
def query_transactions(condition : str) -> str:
    """
    Query the user's own transaction history using a SQL-WHERE clause fragment.
    Only these column names are allowed: amount , kind , created_at , sender_id , recipient_id
    kind must be one of: 'deposit' , 'withdrawal' , 'transfer'.
    amount is stored in cents (multiply rupee amounts by 100).
    Do not write SELECT, table names, or any user filter — those are handled automatically.
    Example for "deposits over 500 last month":
    "kind = 'deposit' AND amount > 50000 AND created_at >= date('now', '-30 days')"
    """
    return "queried"


llm_with_tools = llm.bind_tools([propose_transfer , get_account_details , query_transactions ])

system = (
    "You are a banking assistant for HBL. "
    "If the user wants to send money, call propose_transfer. "
    "If the user asks for their account details, account number, or balance, call get_account_details. "
    "Answer ONLY from the HBL Terms and Conditions provided below. "
    "If the answer is not explicitly stated in the context, respond: "
    "'I don't have that information in the HBL terms.' "
    "Never say a transfer is complete — it requires confirmation. "
    "For anything unrelated to banking, say: "
    "'I can only help with banking questions.'"
)

# For terms RAG
def interpret(message):
    """Returns (tool_name, args) or ('text', '...')"""
    policy_context = retrieve_policy(message)

    full_system = system
    if policy_context:
        full_system += (
            "\n\nAnswer questions using the following "
            "HBL Terms and Conditions:\n\n"
            + policy_context
        )

    result = llm_with_tools.invoke([
        ("system", full_system),
        ("human", message),
    ])

    if result.tool_calls:
        tool_name = result.tool_calls[0]["name"]
        tool_args = result.tool_calls[0]["args"]
        return tool_name, tool_args

    content = result.content
    if isinstance(content, list):
        text = " ".join(
            block["text"] for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    else:
        text = content

    return "text", text

# For SQL Agent: Turn raw rows coming from tables into sentences. 
def summarize_results(question, rows):
    if not rows:
        return "No matching transactions found."

    rows_text = "\n".join(
        f"{r['created_at']}: {r['kind']} of PKR {r['amount']/100:.2f}"
        for r in rows
    )

    result = llm.invoke([
        ("system", "Summarize these transaction records to answer the user's "
                   "question in one or two plain sentences. Don't list every "
                   "row individually unless there are 3 or fewer."),
        ("human", f"Question: {question}\n\nRecords:\n{rows_text}"),
    ])

    content = result.content
    if isinstance(content, list):
        return " ".join(
            b["text"] for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return content
