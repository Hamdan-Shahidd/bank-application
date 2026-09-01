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
    conversation_id: Optional[int] = None


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
    conversation_id: Optional[int] = None

class UserResponse(BaseModel):
    user_id: int
    username: str
    gmail: str
    account_number: str
    balance: int
    balance_display: str

    @classmethod
    def from_user(cls, user):
        return cls(
            user_id=user.user_id,
            username=user.username,
            gmail=user.gmail,
            account_number=user.account_number,
            balance=user.balance,
            balance_display=f"PKR {user.balance / 100:.2f}"
        )
class WithdrawRequest(BaseModel):
    amount: int

class DepositConfirmRequest(BaseModel):
    amount: int

class WithdrawConfirmRequest(BaseModel):
    amount: int


class CryptoPrice(BaseModel):
    symbol: str
    ticker: str
    price_usd: float
    change_pct_today: float


class CryptoPricesResponse(BaseModel):
    prices: list[CryptoPrice]
    stale: bool
    error: Optional[str] = None

class CityWeather(BaseModel):
    city: str
    temperature_c: float
    windspeed_kmh: float
    condition: str
    observed_at: str


class WeatherResponse(BaseModel):
    cities: list[CityWeather]
    stale: bool
    error: Optional[str] = None


class EmailDraft(BaseModel):
    recipient: str
    subject: str
    body: str
    tone: str = "professional"


class EmailRefineRequest(BaseModel):
    subject: str
    body: str
    instruction: str


class EmailRefineResponse(BaseModel):
    subject: str
    body: str


class EmailSendRequest(BaseModel):
    recipient: str
    subject: str
    body: str


class EmailSendResponse(BaseModel):
    sent: bool
    error: Optional[str] = None


# Schema of web searches
class SearchResultItem(BaseModel):
    title: str
    url: str
    snippet: str
    score: float


class WebSearchResponse(BaseModel):
    answer: Optional[str] = None
    results: list[SearchResultItem] = []
    query: str
    cached: bool = False
    error: Optional[str] = None

# Image Generation
class ImageGenRequest(BaseModel):
    prompt: str

class ImageGenResponse(BaseModel):
    image_b64: Optional[str] = None
    prompt: str
    cached: bool = False
    error: Optional[str] = None

# For OTP generation
class OTPRequestRequest(BaseModel):
    gmail: str

class OTPVerifyRequest(BaseModel):
    username: str
    gmail: str
    password: str
    code: str

class OTPResponse(BaseModel):
    success: bool
    error: Optional[str] = None


class ConversationSummary(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str
    message_count: int


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummary]


class RenameConversationRequest(BaseModel):
    title: str