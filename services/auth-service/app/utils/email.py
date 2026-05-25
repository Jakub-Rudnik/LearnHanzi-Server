import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings


def _resolve_sender() -> str | None:
    return settings.smtp_from_email or settings.smtp_user


def send_password_reset_email(recipient: str, reset_token: str) -> bool:
    sender = _resolve_sender()
    if not settings.smtp_host or not sender:
        return False

    reset_link = (
        f"{settings.frontend_url.rstrip('/')}"
        f"{settings.frontend_reset_password_path}?token={reset_token}"
    )

    message = EmailMessage()
    message["Subject"] = "LearnHanzi - Password reset"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        "Use this link to reset your password:\n"
        f"{reset_link}\n\n"
        f"If you did not request a password reset, ignore this message."
    )

    tls_context = ssl.create_default_context()

    if settings.smtp_port == 465 and not settings.smtp_starttls:
        with smtplib.SMTP_SSL(
            settings.smtp_host,
            settings.smtp_port,
            timeout=10,
            context=tls_context,
        ) as smtp:
            if settings.smtp_user and settings.smtp_password:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.ehlo()
            if settings.smtp_starttls:
                smtp.starttls(context=tls_context)
                smtp.ehlo()
            if settings.smtp_user and settings.smtp_password:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)

    return True

