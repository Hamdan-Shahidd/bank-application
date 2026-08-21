import os
import secrets
from urllib.parse import urlencode

import requests
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from logging_config import logger

CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = os.environ["GOOGLE_REDIRECT_URI"]
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

_pending_states = {}   # state -> "__anonymous__" (Entry A) or user_id (Entry B)


def build_auth_url(user_id=None):
    """user_id=None -> anonymous login flow. Real id -> connect flow."""
    state = secrets.token_urlsafe(24)
    _pending_states[state] = user_id if user_id is not None else "__anonymous__"
    params = {
        "client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI,
        "response_type": "code", "scope": " ".join(SCOPES),
        "access_type": "offline", "prompt": "consent", "state": state,
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def resolve_state(state):
    return _pending_states.pop(state, None)


def exchange_code_for_tokens(code):
    resp = requests.post(TOKEN_URL, data={
        "code": code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code",
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()


def verify_identity(id_token_str):
    info = google_id_token.verify_oauth2_token(
        id_token_str, google_requests.Request(), CLIENT_ID
    )
    if not info.get("email_verified", False):
        raise ValueError("Google reports this email is not verified.")
    return {
        "google_id": info["sub"], "email": info["email"],
        "name": info.get("name", info["email"].split("@")[0]),
    }