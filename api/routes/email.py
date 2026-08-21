from fastapi import APIRouter, Depends
from api.schemas import (
    EmailRefineRequest, EmailRefineResponse,
    EmailSendRequest, EmailSendResponse,
)
from api.auth import current_user
from ai.agent import refine_email_draft
from core.email_service import send_email
from core.gmail_oauth_service import send_via_gmail
from api.main import bank

router = APIRouter()


@router.post("/email/refine", response_model=EmailRefineResponse)
def email_refine(body: EmailRefineRequest, user=Depends(current_user)):
    draft = refine_email_draft(body.subject, body.body, body.instruction)
    return EmailRefineResponse(**draft)

# api/routes/email.py
@router.post("/email/send", response_model=EmailSendResponse)
def email_send(body: EmailSendRequest, user=Depends(current_user)):
    refresh_token = bank.storage.get_google_refresh_token(user.user_id)

    if refresh_token:
        result = send_via_gmail(user.user_id, refresh_token, body.recipient,
                                body.subject, body.body)
        return EmailSendResponse(**result)

    if not user.gmail_verified:
        return EmailSendResponse(sent=False, error="Your email isn't verified.")
    if body.recipient.strip().lower() != user.gmail.strip().lower():
        return EmailSendResponse(sent=False,
            error="Connect your Google account to send to other people, "
                  "or send to your own verified address.")
    result = send_email(user.user_id, body.recipient, body.subject, body.body)
    return EmailSendResponse(**result)