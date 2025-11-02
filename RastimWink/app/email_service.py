import os
import smtplib
from email.message import EmailMessage
from typing import Optional
from dotenv import load_dotenv
from fastapi.concurrency import run_in_threadpool

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
DEFAULT_FROM = os.getenv("EMAIL_FROM", SMTP_USER or "noreply@wink.ru")

def send_email(to_email: str, subject: str, body: str, html: Optional[str] = None, from_email: Optional[str] = None):
    from_email = from_email or DEFAULT_FROM
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD]):
        raise RuntimeError("SMTP config missing")
    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype = "html")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

async def send_email_async(to_email: str, subject: str, body: str, html: Optional[str] = None, from_email: Optional[str] = None):
    await run_in_threadpool(send_email, to_email, subject, body, html, from_email)

def send_set_password_email(personal_email: str, corporate_email: str, link: str):
    subject = "Wink - настройка пароля"
    body = f"Вам создана корпоративная почта: {corporate_email}\\nУстановите пароль: {link}"
    try:
        send_email(personal_email, subject, body)
    except Exception:
        pass