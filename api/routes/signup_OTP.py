from fastapi import APIRouter, HTTPException
# Pydantic schema that defines what your API takes and returns.
from api.schemas import OTPRequestRequest, OTPVerifyRequest, OTPResponse, TokenResponse
from core.otp_service import request_code, verify_code
from api.auth import create_token
from api.main import bank

# This creates a FastAPI router. Attach our sign up endpoint to this.
router = APIRouter()


@router.post("/signup/request-code", response_model=OTPResponse)
def signup_request_code(body: OTPRequestRequest):
    if bank.find(body.gmail):
        return OTPResponse(success=False, error="An account with this email already exists.")
    result = request_code(body.gmail)
    return OTPResponse(success=result["sent"], error=result["error"])


@router.post("/signup/verify-code", response_model=TokenResponse)
def signup_verify_code(body: OTPVerifyRequest):
    result = verify_code(body.gmail, body.code)
    if not result["verified"]:
        raise HTTPException(status_code=400, detail=result["error"])

    try:
        user = bank.sign_up(body.username, body.gmail, body.password)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    bank.storage.mark_gmail_verified(user.user_id)
    token = create_token(user.user_id)
    return TokenResponse(access_token=token)