# api/services/emailer.py
import smtplib
from email.message import EmailMessage
import os

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")  # your gmail
SMTP_PASS = os.environ.get("SMTP_PASS")  # app password

FROM = os.environ.get("EMAIL_FROM", SMTP_USER)

def send_email(to: str, subject: str, body: str):
    if not SMTP_USER or not SMTP_PASS:
        raise RuntimeError("SMTP credentials not set (SMTP_USER/SMTP_PASS)")
    msg = EmailMessage()
    msg["From"] = FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
