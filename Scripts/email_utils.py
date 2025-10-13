import os
import mimetypes
import smtplib
from email.message import EmailMessage
from typing import Iterable, List, Optional

from dotenv import load_dotenv


def _split_and_strip(addresses: Optional[str]) -> List[str]:
    if not addresses:
        return []
    return [addr.strip() for addr in addresses.split(",") if addr.strip()]


def send_email_with_attachments(
    subject: str,
    body_text: str,
    to_emails: Optional[Iterable[str]] = None,
    *,
    cc_emails: Optional[Iterable[str]] = None,
    bcc_emails: Optional[Iterable[str]] = None,
    attachments: Optional[Iterable[str]] = None,
) -> None:
    """Send an email using SMTP with optional attachments.

    Configuration is taken from environment variables (loaded via python-dotenv):
      - SMTP_HOST (required)
      - SMTP_PORT (default: 587)
      - SMTP_USER (optional)
      - SMTP_PASSWORD (optional)
      - SMTP_USE_TLS (default: true)
      - EMAIL_FROM (default: SMTP_USER)
      - EMAIL_TO (fallback recipients if to_emails not provided; comma-separated)
      - EMAIL_CC (optional, comma-separated)
      - EMAIL_BCC (optional, comma-separated)
    """
    load_dotenv()

    smtp_host = os.getenv("SMTP_HOST")
    if not smtp_host:
        raise RuntimeError("SMTP_HOST is required to send emails")

    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}

    default_from = smtp_user or os.getenv("EMAIL_FROM") or "no-reply@example.com"
    email_from = os.getenv("EMAIL_FROM", default_from)

    # Determine recipients
    env_to = _split_and_strip(os.getenv("EMAIL_TO"))
    env_cc = _split_and_strip(os.getenv("EMAIL_CC"))
    env_bcc = _split_and_strip(os.getenv("EMAIL_BCC"))

    to_list = list(to_emails or env_to)
    cc_list = list(cc_emails or env_cc)
    bcc_list = list(bcc_emails or env_bcc)

    if not to_list and not cc_list and not bcc_list:
        raise RuntimeError("No recipients provided. Set EMAIL_TO or pass to_emails.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_from
    if to_list:
        msg["To"] = ", ".join(to_list)
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    # BCC is not added to headers

    msg.set_content(body_text)

    for path in (attachments or []):
        if not os.path.exists(path):
            continue
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        filename = os.path.basename(path)
        with open(path, "rb") as f:
            file_data = f.read()
        msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=filename)

    all_recipients = to_list + cc_list + bcc_list

    # Choose SSL vs STARTTLS based on port and flag
    if smtp_use_tls and smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg, from_addr=email_from, to_addrs=all_recipients)
    else:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            if smtp_use_tls:
                try:
                    server.starttls()
                except smtplib.SMTPException:
                    pass
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg, from_addr=email_from, to_addrs=all_recipients)
