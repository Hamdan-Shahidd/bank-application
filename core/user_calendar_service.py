import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from logging_config import logger
from core.token_crypto import decrypt_token

CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
TOKEN_URL = "https://oauth2.googleapis.com/token"
TIMEZONE = os.getenv("BANK_TIMEZONE", "Asia/Karachi")


def _get_service(encrypted_refresh_token):
    refresh_token = decrypt_token(encrypted_refresh_token)
    creds = Credentials(
        token=None, refresh_token=refresh_token, token_uri=TOKEN_URL,
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
    )
    creds.refresh(Request())
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def add_event(encrypted_refresh_token, date, time, duration_minutes, title):
    try:
        start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M").replace(
            tzinfo=ZoneInfo(TIMEZONE))
    except ValueError:
        return {"added": False, "error": "Could not understand that date or time."}

    end_dt = start_dt + timedelta(minutes=duration_minutes)

    try:
        service = _get_service(encrypted_refresh_token)
        event = service.events().insert(calendarId="primary", body={
            "summary": title,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": TIMEZONE},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": TIMEZONE},
        }).execute()
        logger.info(f"USER CALENDAR EVENT ADDED | event_id={event['id']}")
        return {"added": True, "event_id": event["id"], "error": None}
    except HttpError as e:
        if e.resp.status == 401:
            return {"added": False, "error": "Your calendar connection expired. Please reconnect."}
        logger.warning(f"CALENDAR API ERROR | {e}")
        return {"added": False, "error": "Could not reach your calendar."}
    except Exception as e:
        logger.warning(f"CALENDAR ADD FAILED | {e}")
        return {"added": False, "error": "Could not add the event right now."}