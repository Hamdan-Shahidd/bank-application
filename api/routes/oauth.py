from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from core.google_oauth import build_auth_url, resolve_state, exchange_code_for_tokens, verify_identity, has_extended_scopes, FRONTEND_URL
from core.token_crypto import encrypt_token
from core.models import User, hash_password
from api.auth import create_token, current_user
from api.main import bank
from logging_config import logger
import secrets

router = APIRouter()


@router.get("/auth/google/login")
def google_login():
    """Entry A: anonymous, from the Login/Signup page."""
    return RedirectResponse(build_auth_url())


@router.get("/auth/google/connect-url")
def google_connect_url(user=Depends(current_user)):
    """
    Entry B, step 1: returns the auth URL as JSON to an AUTHENTICATED
    request. The frontend then navigates to the returned URL itself.
    """
    return JSONResponse({"url": build_auth_url(user.user_id)})


@router.get("/auth/google/callback")
def google_callback(code: str, state: str):
    resolved = resolve_state(state)
    if resolved is None:
        return RedirectResponse(f"{FRONTEND_URL}/login?error=invalid_state")

    try:
        tokens = exchange_code_for_tokens(code)
        identity = verify_identity(tokens["id_token"])
    except Exception as e:
        logger.warning(f"GOOGLE OAUTH FAILED | {e}")
        return RedirectResponse(f"{FRONTEND_URL}/login?error=oauth_failed")

    refresh_token = tokens.get("refresh_token")

    if resolved == "__anonymous__":
        user = bank.storage.find_by_gmail(identity["email"])
        if user is None:
            random_password = secrets.token_urlsafe(32)
            new_user = User(identity["name"], identity["email"], None,
                            hash_password(random_password))
            user = bank.storage.create(new_user)
            logger.info(f"SIGNUP VIA GOOGLE | user_id={user.user_id}")

        # verify_identity() already rejected unverified addresses, so Google
        # has vouched for this email. Needed for the SMTP fallback in
        # /email/send, which link_google_account used to set for us.
        bank.storage.mark_gmail_verified(user.user_id)

        # Deliberately NOT calling link_google_account here -- a basic-scope
        # login has no Gmail/Calendar access to store.
        jwt_token = create_token(user.user_id)
        return RedirectResponse(f"{FRONTEND_URL}/oauth-callback?token={jwt_token}")

    else:
        if not refresh_token:
            logger.warning(f"GOOGLE CONNECT NO REFRESH TOKEN | user_id={resolved}")
            return RedirectResponse(f"{FRONTEND_URL}/assistant?google=no_refresh_token")

        if not has_extended_scopes(tokens.get("scope")):
            logger.warning(
                f"GOOGLE CONNECT PARTIAL SCOPES | user_id={resolved} | "
                f"granted={tokens.get('scope')!r}")
            return RedirectResponse(f"{FRONTEND_URL}/assistant?google=partial_scopes")

        bank.storage.link_google_account(
            resolved, identity["google_id"], encrypt_token(refresh_token))
        logger.info(f"GOOGLE CONNECTED | user_id={resolved}")
        return RedirectResponse(f"{FRONTEND_URL}/assistant?google=connected")