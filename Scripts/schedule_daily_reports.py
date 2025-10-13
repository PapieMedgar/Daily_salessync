import os
import time
from datetime import date

import schedule
from dotenv import load_dotenv

from Scripts.send_daily_reports import generate_all_reports_for_range
from Scripts.email_utils import send_email_with_attachments


def job():
    load_dotenv()
    today = date.today().isoformat()
    start = os.getenv("REPORT_START_DATE", today)
    end = os.getenv("REPORT_END_DATE", today)

    attachments = generate_all_reports_for_range(start, end)

    subject = f"SalesSync Reports for {start} to {end}"
    body = (
        f"Please find attached the SalesSync reports for {start} to {end}.\n\n"
        f"Total attachments: {len(attachments)}\n\n"
        "This is an automated email."
    )

    recipients_env = os.getenv("EMAIL_TO")
    to_list = [addr.strip() for addr in (recipients_env or "").split(",") if addr.strip()]

    send_email_with_attachments(subject=subject, body_text=body, to_emails=to_list or None, attachments=attachments)


if __name__ == "__main__":
    # Schedule the job every day at 16:00 (4 PM) server local time
    schedule.every().day.at("16:00").do(job)

    print("Scheduler started. Will send daily reports at 16:00.")
    while True:
        schedule.run_pending()
        time.sleep(30)
