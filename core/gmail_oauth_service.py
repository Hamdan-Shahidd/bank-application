import base64
import os
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from logging_config import logger
from core.token_crypto import decrypt_token

CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
TOKEN_URL = "https://oauth2.googleapis.com/token"


def send_via_gmail(user_id, encrypted_refresh_token, recipient, subject, body):
    try:
        refresh_token = decrypt_token(encrypted_refresh_token)
    except Exception as e:
        logger.warning(f"GMAIL TOKEN DECRYPT FAILED | user_id={user_id} | {e}")
        return {"sent": False, "error": "Your Google connection is invalid. Please reconnect."}

    try:
        creds = Credentials(
            token=None, refresh_token=refresh_token, token_uri=TOKEN_URL,
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
        )
        creds.refresh(Request())
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["To"] = recipient
        msg.set_content(body)

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()

        logger.info(f"GMAIL API SEND | user_id={user_id} | recipient={recipient} | subject={subject[:60]!r}")
        return {"sent": True, "error": None}

    except HttpError as e:
        logger.warning(f"GMAIL API ERROR | user_id={user_id} | {e}")
        if e.resp.status == 401:
            return {"sent": False, "error": "Your Google connection has expired. Please reconnect."}
        return {"sent": False, "error": "Gmail rejected the request."}
    except Exception as e:
        logger.warning(f"GMAIL SEND FAILED | user_id={user_id} | {e}")
        return {"sent": False, "error": "Could not send the email right now."}