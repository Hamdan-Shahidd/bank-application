from fastapi import APIRouter, Depends, HTTPException
from api.schemas import AssistantRequest, ConfirmRequest, AssistantResponse, MessageResponse , DepositConfirmRequest , WithdrawConfirmRequest
from api.auth import current_user
from api.main import bank
from ai.agent import interpret , summarize_results
from core.market import get_crypto_prices as fetch_crypto_prices
from core.weather import get_weather as fetch_weather
from ai.agent import compose_email_body
from core.web_search import web_search as run_web_search
router = APIRouter()
from core.imagegen import generate_image as run_image_gen

@router.post("/assistant", response_model=AssistantResponse)
def assistant(body: AssistantRequest, user=Depends(current_user)):
    kind, payload = interpret(body.message)

    if kind == "propose_transfer":
        return AssistantResponse(kind="proposal", proposal=payload)

    elif kind == "get_account_details":
        details = {
            "username": user.username,
            "account_number": user.account_number,
            "balance": user.balance,
        }
        return AssistantResponse(kind="account_details", details=details)

    elif kind == "get_weather_info":
        city = payload.get("city", "")
        result = fetch_weather(city=city)
        return AssistantResponse(kind="weather_info", details=result)

    elif kind == "get_crypto_prices":
        symbol = payload.get("symbol", "")
        result = fetch_crypto_prices(symbol=symbol)
        return AssistantResponse(kind="crypto_prices", details=result)

    elif kind == "propose_deposit":
        return AssistantResponse(kind="proposal_deposit", proposal=payload)

    elif kind == "propose_withdrawal":
        return AssistantResponse(kind="proposal_withdrawal", proposal=payload)

    elif kind == "compose_email":
        recipient = payload.get("recipient", "")
        purpose = payload.get("purpose", "")
        tone = payload.get("tone", "professional")
        draft = compose_email_body(recipient, purpose, tone)
        return AssistantResponse(kind="email_draft", details={
            "recipient": recipient,
            "subject": draft["subject"],
            "body": draft["body"],
            "tone": tone,
        })

    elif kind == "web_search_tool":
        query = payload.get("query", "")
        topic = payload.get("topic", "general")
        result = run_web_search(user.user_id, query, topic)
        return AssistantResponse(kind="web_search", details=result)

    elif kind == "generate_image_tool":
        prompt = payload.get("prompt", "")
        result = run_image_gen(user.user_id, prompt)
        return AssistantResponse(kind="generated_image", details=result)
    
    # For SQL Agent
    elif kind == "query_transactions":
        condition = payload.get("condition", "")
        try:
            rows = bank.query_transactions(user, condition)
            answer = summarize_results(body.message, rows)
            return AssistantResponse(kind="text", text=answer)
        except ValueError:
            return AssistantResponse(kind="text", text="I can't run that kind of question.")
    
    return AssistantResponse(kind="text", text=payload)


@router.post("/assistant/confirm", response_model=MessageResponse)
def assistant_confirm(body: ConfirmRequest, user=Depends(current_user)):
    try:
        bank.transfer(user, body.recipient_account, body.amount)
        return MessageResponse(message="Transfer complete")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assistant/confirm_deposit", response_model=MessageResponse)
def assistant_confirm_deposit(body: DepositConfirmRequest, user=Depends(current_user)):
    try:
        bank.deposit(user, body.amount)
        return MessageResponse(message="Deposit complete")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assistant/confirm_withdraw", response_model=MessageResponse)
def assistant_confirm_withdraw(body: WithdrawConfirmRequest, user=Depends(current_user)):
    try:
        bank.withdraw(user, body.amount)
        return MessageResponse(message="Withdrawal complete")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))