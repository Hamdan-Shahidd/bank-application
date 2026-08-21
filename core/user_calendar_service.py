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

def find_events_matching(encrypted_refresh_token, date=None, title_query=""):
    """
    Finds events on a given date (YYYY-MM-DD) and/or matching a title
    keyword. date=None searches the next 14 days.
    """
    try:
        service = _get_service(encrypted_refresh_token)
        if date:
            day_start = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=ZoneInfo(TIMEZONE))
            time_min, time_max = day_start.isoformat(), (day_start + timedelta(days=1)).isoformat()
        else:
            now = datetime.now(ZoneInfo(TIMEZONE))
            time_min, time_max = now.isoformat(), (now + timedelta(days=14)).isoformat()

        result = service.events().list(
            calendarId="primary", timeMin=time_min, timeMax=time_max,
            singleEvents=True, orderBy="startTime"
        ).execute()

        events = [
            {"event_id": e["id"], "title": e.get("summary", "(no title)"),
             "start": e["start"].get("dateTime", e["start"].get("date"))}
            for e in result.get("items", []) if e.get("status") != "cancelled"
        ]
        if title_query:
            q = title_query.lower()
            events = [e for e in events if q in e["title"].lower()]
        return {"events": events, "error": None}
    except HttpError as e:
        if e.resp.status == 401:
            return {"events": [], "error": "Your calendar connection expired. Please reconnect."}
        return {"events": [], "error": "Could not reach your calendar."}
    except Exception:
        return {"events": [], "error": "Could not search your calendar right now."}


def delete_event(encrypted_refresh_token, event_id):
    try:
        service = _get_service(encrypted_refresh_token)
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        logger.info(f"USER CALENDAR EVENT DELETED | event_id={event_id}")
        return {"deleted": True, "error": None}
    except HttpError as e:
        if e.resp.status == 404:
            return {"deleted": False, "error": "That event no longer exists."}
        if e.resp.status == 401:
            return {"deleted": False, "error": "Your calendar connection expired. Please reconnect."}
        return {"deleted": False, "error": "Could not reach your calendar."}
    except Exception:
        return {"deleted": False, "error": "Could not delete the event right now."}


def update_event(encrypted_refresh_token, event_id, date=None, time=None,
                 duration_minutes=None, title=None):
    """Partial update — only the fields you pass in actually change."""
    try:
        service = _get_service(encrypted_refresh_token)
        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        if title:
            event["summary"] = title

        if date or time or duration_minutes:
            current_start = datetime.fromisoformat(event["start"]["dateTime"])
            current_end = datetime.fromisoformat(event["end"]["dateTime"])
            new_date = date or current_start.strftime("%Y-%m-%d")
            new_time = time or current_start.strftime("%H:%M")
            new_start = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M").replace(
                tzinfo=ZoneInfo(TIMEZONE))
            dur = duration_minutes or (current_end - current_start).total_seconds() / 60
            new_end = new_start + timedelta(minutes=dur)
            event["start"] = {"dateTime": new_start.isoformat(), "timeZone": TIMEZONE}
            event["end"] = {"dateTime": new_end.isoformat(), "timeZone": TIMEZONE}

        updated = service.events().update(
            calendarId="primary", eventId=event_id, body=event).execute()
        logger.info(f"USER CALENDAR EVENT UPDATED | event_id={event_id}")
        return {"updated": True, "start": updated["start"]["dateTime"], "error": None}
    except HttpError as e:
        if e.resp.status == 404:
            return {"updated": False, "error": "That event no longer exists."}
        if e.resp.status == 401:
            return {"updated": False, "error": "Your calendar connection expired. Please reconnect."}
        return {"updated": False, "error": "Could not reach your calendar."}
    except Exception:
        return {"updated": False, "error": "Could not update the event right now."}