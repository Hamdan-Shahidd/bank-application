# test_smtp.py
import os, smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()

msg = EmailMessage()
msg["Subject"] = "SMTP test from Bank Application"
msg["From"] = os.environ["SMTP_USER"]
msg["To"] = os.environ["SMTP_USER"]      # send to yourself
msg.set_content("If you can read this, SMTP works.")

with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"])) as s:
    s.starttls()
    s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
    s.send_message(msg)

print("sent")