"""
The protocol used is SMTP, which is a text-based command response protocol. The oython library used to talk with 
it is smtplib. Google's SMTP server rejects our regular passwords, the solution is creating a app paaswrod.
App passwords are used beacuse they bypass 2FA because they are only generated after completing 2FA.

"""

import os
import re
import time
import smtplib # Python in-build SMTP client for sending the email. 
from email.message import EmailMessage # Construct the email
from email.utils import formataddr # Format the head correctly
from logging_config import logger

# SMTP Configurations: These values come from the envr=ironment variables. Keep credentials outside the source code
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Apex Finance")

# Email validation. Checks wether the adress looks like the email adress (hamdan2@gmail.com)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Maximum length: This prevents someone from sending extremaly large subject and body
MAX_SUBJECT_LENGTH = 200
MAX_BODY_LENGTH = 5000

# Recipient allowlist: Empty right now but we can send to bank's email. This way the email could be sent to bank omly.
RECIPIENT_ALLOWLIST = set()

# Rate Limiting: The users are limited to sending 5 gmails every 1 hour (3600 seconds). Timestamps stores in _send_log()
RATE_LIMIT_MAX = 5
RATE_LIMIT_WINDOW_SECONDS = 3600
_send_log = {}   # user_id -> [timestamps]


def _rate_limited(user_id):
    now = time.time() # Gets the current timestamp
    # This removes the old time stamps. Suppose the mail was sent an hour ago, those timestamps are removed.
    stamps = [
        t for t in _send_log.get(user_id, [])
        if now - t < RATE_LIMIT_WINDOW_SECONDS
    ]
    # If already 5 emails are sent don't allow another one
    _send_log[user_id] = stamps
    return len(stamps) >= RATE_LIMIT_MAX

# After successful email this records the correct timestamp.
def _record_send(user_id):
    _send_log.setdefault(user_id, []).append(time.time())

# This is the main function. 
def send_email(user_id, recipient, subject, body):
    """
    Returns dictioanry in the format {"sent": bool, "error": None}.
    Validates before touching SMTP so bad input fails fast and cheaply.
    """
    # If the SMTP is not configured. 
    if not SMTP_USER or not SMTP_PASSWORD:
        return {
            "sent": False, 
            "error": "Email sending is not configured on the server."
        }

    # Clean the input
    recipient = (recipient or "").strip()
    subject = (subject or "").strip()
    body = (body or "").strip()

    # Check if the recipient match the basic email adress format defined above
    if not EMAIL_RE.match(recipient):
        return {
            "sent": False, 
            "error": f"'{recipient}' is not a valid email address."
        }

    # Check if the recipient is in the allowlist. In present case all gmails are in the allowed list.
    if RECIPIENT_ALLOWLIST and recipient.lower() not in RECIPIENT_ALLOWLIST:
        logger.warning(f"EMAIL BLOCKED | user_id={user_id} | recipient={recipient} | reason=not in allowlist")
        return {
            "sent": False, 
            "error": "Sending to that address is not permitted."
        }

    # Prevents an empty subject
    if not subject:
        return {
            "sent": False, 
            "error": "Subject cannot be empty."
        }

    # Prevents an empty body
    if not body:
        return {
            "sent": False, 
            "error": "Body cannot be empty."
        }

    # Check if the subject is greater then the maximum subject length
    if len(subject) > MAX_SUBJECT_LENGTH:
        return {
            "sent": False, 
            "error": "Subject is too long."
        }

    # Check if the body is greater then the maximum body length.
    if len(body) > MAX_BODY_LENGTH:
        return {
            "sent": False, 
            "error": "Body is too long."
        }

    # Check rate limit: If the user has already sent the 5 mails.
    if _rate_limited(user_id):
        logger.warning(f"EMAIL RATE LIMITED | user_id={user_id}")
        return {
            "sent": False,
            "error": f"Send limit reached ({RATE_LIMIT_MAX} per hour). Try again later."
        }

    try:
        # Creating the email
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = formataddr((SMTP_FROM_NAME, SMTP_USER))
        msg["To"] = recipient
        msg["Reply-To"] = SMTP_USER
        msg.set_content(body)

        # Connect to gmail
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            # starttlsl means that the connection begins in plain text then move towards encrypted
            # implicit TLS is encrypted from the first byte.
            server.starttls() 
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        _record_send(user_id)
        # Log the fact and the recipient, never the body.
        logger.info(f"EMAIL SENT | user_id={user_id} | recipient={recipient} "
                    f"| subject={subject[:60]!r}")
        return {
            "sent": True, 
            "error": None
        }

    except smtplib.SMTPAuthenticationError:
        logger.warning("EMAIL SEND FAILED | reason=SMTP auth rejected")
        return {
            "sent": False, 
            "error": "Email server rejected the credentials."
        }
    except Exception as e:
        logger.warning(f"EMAIL SEND FAILED | user_id={user_id} | {e}")
        return {
            "sent": False, 
            "error": "Could not send the email right now."
        }