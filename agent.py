import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from retriver import retrieve_policy

load_dotenv()
llm = ChatGoogleGenerativeAI(
    model = "gemini-3.5-flash-lite",
    google_api_key = os.environ["GEMINI_API_KEY"]
)
# Defining the tool: 
@tool
def propose_transfer(recipient_account : str , amount : int) -> str:
    """Propose sending money to another account. Don't execute the transaction."""
    return "propose"

# Tool to get account details.
@tool
def get_account_details() -> str:
    """Get the current user's account detail includeing account number and balance"""
    return "fetched"

# Interpret the reply: 
llm_with_tools = llm.bind_tools([propose_transfer , get_account_details])



def interpret(message):
    """Returns ('proposal', {...}) , ('account_details' , {}) or ('text', '...')"""
    policy_context = retrieve_policy(message)

    # System prompt defines when to call the tool.
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

    if policy_context:
        system += (
            "\n\nAnswer questions using the following "
            "HBL Terms and Conditions:\n\n"
            + policy_context
        )

    result = llm_with_tools.invoke([
        ("system", system),
        ("human", message),
    ])

    if result.tool_calls:
        tool_name = result.tool_calls[0]["name"]
        tool_args = result.tool_calls[0]["args"]
        return tool_name , tool_args


    content = result.content
    if isinstance(content, list):
        text = " ".join(
            block["text"] for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    else:
        text = content

    return "text", text