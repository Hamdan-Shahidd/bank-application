from fastapi import APIRouter, Depends, HTTPException
from api.schemas import (
    SignupRequest, LoginRequest, DepositRequest,
    TransferRequest, WithdrawRequest,
    UserResponse, TokenResponse, MessageResponse
)
from api.auth import create_token, current_user
from api.main import bank

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
def signup(body: SignupRequest):
    try:
        user = bank.sign_up(body.username, body.gmail, body.password)
        return UserResponse.from_user(user)
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
    return UserResponse.from_user(user)


@router.post("/deposit", response_model=UserResponse)
def deposit(body: DepositRequest, user=Depends(current_user)):
    try:
        bank.deposit(user, body.amount)
        return UserResponse.from_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/withdraw", response_model=UserResponse)
def withdraw(body: WithdrawRequest, user=Depends(current_user)):
    try:
        bank.withdraw(user, body.amount)
        return UserResponse.from_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transfer", response_model=MessageResponse)
def transfer(body: TransferRequest, user=Depends(current_user)):
    try:
        bank.transfer(user, body.recipient_account, body.amount)
        return MessageResponse(message="Transfer complete")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history")
def history(user=Depends(current_user)):
    return bank.get_history(user)

