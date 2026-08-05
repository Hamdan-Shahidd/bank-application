from fastapi import APIRouter, Depends, HTTPException
from api.schemas import AssistantRequest, ConfirmRequest, AssistantResponse, MessageResponse
from api.auth import current_user
from api.main import bank
from agent import interpret

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

    return AssistantResponse(kind="text", text=payload)


@router.post("/assistant/confirm", response_model=MessageResponse)
def assistant_confirm(body: ConfirmRequest, user=Depends(current_user)):
    try:
        bank.transfer(user, body.recipient_account, body.amount)
        return MessageResponse(message="Transfer complete")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
