from fastapi import APIRouter, Depends, HTTPException
from api.schemas import AssistantRequest, ConfirmRequest, AssistantResponse, MessageResponse , DepositConfirmRequest , WithdrawConfirmRequest
from api.auth import current_user
from api.main import bank
from ai.agent import interpret , summarize_results

router = APIRouter()


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

    elif kind == "propose_deposit":
        return AssistantResponse(kind="proposal_deposit", proposal=payload)

    elif kind == "propose_withdrawal":
        return AssistantResponse(kind="proposal_withdrawal", proposal=payload)
    
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