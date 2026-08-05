from pydantic import BaseModel
from typing import Optional


# Request bodies
class SignupRequest(BaseModel):
    username: str
    gmail: str
    password: str


class LoginRequest(BaseModel):
    gmail: str
    password: str


class DepositRequest(BaseModel):
    amount: int


class TransferRequest(BaseModel):
    recipient_account: str
    amount: int


class AssistantRequest(BaseModel):
    message: str


class ConfirmRequest(BaseModel):
    recipient_account: str
    amount: int


# Response bodies
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: int
    username: str
    gmail: str
    account_number: str
    balance: int


class MessageResponse(BaseModel):
    message: str


class AssistantResponse(BaseModel):
    kind: str                          # "proposal", "account_details", "text"
    text: Optional[str] = None
    proposal: Optional[dict] = None
    details: Optional[dict] = None