"""
Email ownership verification via OTP. No OAuth , just proves
the signer controls the inbox they claim, using the app's existing SMTP.
User enters the email -> server generates a 6 digit code -> code emailed to them -> user enters the code
-> server checks if the code is correct (not expired, haven't completed limit) -> user verified
"""
import random
import time
from core.email_service import send_email
from logging_config import logger

OTP_TTL_SECONDS = 600          # Code valid for 10 minutes
MAX_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 30

# In-memory, same pattern as your other rate limiters/caches.
_pending_codes = {}

# This function is responsible for sending and generating and sedning the OTP
def request_code(email):
    email = email.strip().lower()
    now = time.time()

    # Check the resend cool down
    existing = _pending_codes.get(email)
    if existing and (now - existing["sent_at"]) < RESEND_COOLDOWN_SECONDS:
        wait = int(RESEND_COOLDOWN_SECONDS - (now - existing["sent_at"]))
        return {"sent": False, "error": f"Please wait {wait}s before requesting another code."}

    # Generate the OTP
    code = f"{random.randint(0, 999999):06d}"
    # Stores the OTP and its meta-data
    _pending_codes[email] = {
        "code": code, "expires_at": now + OTP_TTL_SECONDS,
        "attempts": 0, "sent_at": now,
    }

    # Send the mail by calling the function from email_service which is the existing email service.
    result = send_email(
        user_id=0,
        recipient=email,
        subject="Your verification code",
        body=f"Your verification code is {code}. It expires in 10 minutes.\n\n"
             f"If you didn't request this, you can ignore this email.",
    )

    # Handle email failure
    if not result["sent"]:
        logger.warning(f"OTP EMAIL FAILED | email={email} | {result['error']}")
        return {"sent": False, "error": "Could not send the verification email."}

    logger.info(f"OTP SENT | email={email}")
    return {"sent": True, "error": None}

# Verifies the code (OTP)
def verify_code(email, submitted_code):
    email = email.strip().lower()
    entry = _pending_codes.get(email)

    # If their is no code entered by the user.
    if not entry:
        return {"verified": False, "error": "No verification code was requested for this email."}

    # Check expiration of the code.
    if time.time() > entry["expires_at"]:
        _pending_codes.pop(email, None)
        return {"verified": False, "error": "That code has expired. Request a new one."}

    entry["attempts"] += 1
    # If the user has gone beyond five attempts the OTP will be deleted.
    if entry["attempts"] > MAX_ATTEMPTS:
        _pending_codes.pop(email, None)
        return {"verified": False, "error": "Too many incorrect attempts. Request a new code."}

    # If incorrect code is entered.
    if submitted_code.strip() != entry["code"]:
        return {"verified": False, "error": "Incorrect code."}

    # If the code (OTP) matches. 
    _pending_codes.pop(email, None)
    logger.info(f"OTP VERIFIED | email={email}")
    return {"verified": True, "error": None}