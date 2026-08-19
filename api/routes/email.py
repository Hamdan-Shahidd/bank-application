from fastapi import APIRouter, Depends
from api.schemas import (
    EmailRefineRequest, EmailRefineResponse,
    EmailSendRequest, EmailSendResponse,
)
from api.auth import current_user
from ai.agent import refine_email_draft
from core.email_service import send_email

router = APIRouter()


@router.post("/email/refine", response_model=EmailRefineResponse)
def email_refine(body: EmailRefineRequest, user=Depends(current_user)):
    draft = refine_email_draft(body.subject, body.body, body.instruction)
    return EmailRefineResponse(**draft)


@router.post("/email/send", response_model=EmailSendResponse)
def email_send(body: EmailSendRequest, user=Depends(current_user)):
    result = send_email(user.user_id, body.recipient, body.subject, body.body)
    return EmailSendResponse(**result)