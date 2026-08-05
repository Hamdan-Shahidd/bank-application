from fastapi import APIRouter, Depends, HTTPException
from api.schemas import (
    SignupRequest, LoginRequest, DepositRequest,
    TransferRequest, TokenResponse, UserResponse, MessageResponse
)
from api.auth import create_token, current_user
from api.main import bank

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
def signup(body: SignupRequest):
    try:
        user = bank.sign_up(body.username, body.gmail, body.password)
        return UserResponse(
            user_id=user.user_id,
            username=user.username,
            gmail=user.gmail,
            account_number=user.account_number,
            balance=user.balance,
        )
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    try:
        user = bank.log_in(body.gmail, body.password)
        token = create_token(user.user_id)
        return TokenResponse(access_token=token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
def me(user=Depends(current_user)):
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        gmail=user.gmail,
        account_number=user.account_number,
        balance=user.balance,
    )


@router.post("/deposit", response_model=UserResponse)
def deposit(body: DepositRequest, user=Depends(current_user)):
    try:
        bank.deposit(user, body.amount)
        return UserResponse(
            user_id=user.user_id,
            username=user.username,
            gmail=user.gmail,
            account_number=user.account_number,
            balance=user.balance,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transfer", response_model=MessageResponse)
def transfer(body: TransferRequest, user=Depends(current_user)):
    try:
        bank.transfer(user, body.recipient_account, body.amount)
        return MessageResponse(message="Transfer complete")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))