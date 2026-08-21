import os
import base64
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from logging_config import logger
from core.token_crypto import decrypt_token

CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
TOKEN_URL = "https://oauth2.googleapis.com/token"


def _get_service(encrypted_refresh_token):
    refresh_token = decrypt_token(encrypted_refresh_token)
    creds = Credentials(
        token=None, refresh_token=refresh_token, token_uri=TOKEN_URL,
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _extract_body(payload):
    if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode(errors="replace")
    for part in payload.get("parts", []):
        text = _extract_body(part)
        if text:
            return text
    return ""


def search_inbox(encrypted_refresh_token, query="", max_results=5):
    try:
        service = _get_service(encrypted_refresh_token)
        result = service.users().messages().list(
            userId="me", q=query, maxResults=max_results
        ).execute()

        messages = []
        for m in result.get("messages", []):
            full = service.users().messages().get(
                userId="me", id=m["id"], format="full"
            ).execute()
            headers = {h["name"]: h["value"] for h in full["payload"].get("headers", [])}
            messages.append({
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
                "snippet": full.get("snippet", ""),
                "body": _extract_body(full["payload"])[:2000],
            })

        logger.info(f"GMAIL INBOX SEARCH | query={query!r} | found={len(messages)}")
        return {"messages": messages, "error": None}

    except HttpError as e:
        if e.resp.status == 401:
            return {"messages": [], "error": "Your Google connection has expired. Please reconnect."}
        logger.warning(f"GMAIL API ERROR | {e}")
        return {"messages": [], "error": "Could not reach Gmail."}
    except Exception as e:
        logger.warning(f"GMAIL SEARCH FAILED | {e}")
        return {"messages": [], "error": "Could not search the inbox right now."}