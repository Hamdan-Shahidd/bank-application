import os
import secrets
from urllib.parse import urlencode

import requests
from logging_config import logger

CLIENT_ID = os.environ["GOOGLE_CALENDAR_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CALENDAR_CLIENT_SECRET"]
REDIRECT_URI = os.environ["GOOGLE_CALENDAR_REDIRECT_URI"]

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

_pending_states = {}


def build_auth_url(user_id):
    state = secrets.token_urlsafe(24)
    _pending_states[state] = user_id
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def resolve_state(state):
    return _pending_states.pop(state, None)


def exchange_code_for_tokens(code):
    resp = requests.post(TOKEN_URL, data={
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()