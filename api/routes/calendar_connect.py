from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from core.user_calendar_oauth import build_auth_url, resolve_state, exchange_code_for_tokens
from core.token_crypto import encrypt_token
from api.auth import current_user
from api.main import bank
from logging_config import logger
import os

router = APIRouter()
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")


@router.get("/calendar/connect")
def calendar_connect(user=Depends(current_user)):
    return RedirectResponse(build_auth_url(user.user_id))


@router.get("/calendar/callback")
def calendar_callback(code: str, state: str):
    user_id = resolve_state(state)
    if user_id is None:
        return RedirectResponse(f"{FRONTEND_URL}/assistant?calendar=error")

    try:
        tokens = exchange_code_for_tokens(code)
        refresh_token = tokens["refresh_token"]
    except Exception as e:
        logger.warning(f"CALENDAR OAUTH FAILED | {e}")
        return RedirectResponse(f"{FRONTEND_URL}/assistant?calendar=error")

    bank.storage.link_calendar(user_id, encrypt_token(refresh_token))
    logger.info(f"CALENDAR CONNECTED | user_id={user_id}")
    return RedirectResponse(f"{FRONTEND_URL}/assistant?calendar=connected")