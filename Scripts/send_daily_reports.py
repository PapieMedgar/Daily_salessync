import os
import sys
from datetime import date
from typing import List

from dotenv import load_dotenv

# Local imports
from Scripts.daily_visits_report import main as daily_visits_main  # type: ignore
from Scripts.team_lead_visits_report import main as team_lead_visits_main  # type: ignore
from Scripts.team_lead_visit_details_export import export_visit_details  # type: ignore
from Scripts.email_utils import send_email_with_attachments  # type: ignore


def generate_all_reports_for_range(start_date: str, end_date: str) -> List[str]:
    """Generate all report files for the given date range. Returns paths of files.

    - Daily visits pivot CSV/XLSX under reports/
    - Team lead daily visits CSV/XLSX under reports/
    - Visit details per team lead CSV/XLSX under reports/visit_details/
    """
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)

    # 1) Generate daily visits pivot and xlsx
    # daily_visits_report.main expects argv: start, end, output_csv
    sys_argv_backup = sys.argv
    try:
        sys.argv = [sys.argv[0], start_date, end_date, os.path.join("reports", "daily_visits.csv")]
        daily_visits_main()
    finally:
        sys.argv = sys_argv_backup

    # 2) Generate team lead summarized report (reads from the daily_visits.csv by default)
    sys_argv_backup = sys.argv
    try:
        sys.argv = [sys.argv[0], os.path.join("reports", "daily_visits.csv"), os.path.join("reports", "team_lead_daily_visits.csv")]
        team_lead_visits_main()
    finally:
        sys.argv = sys_argv_backup

    # 3) Generate detailed per-team-lead visit details (also produces XLSX)
    export_paths = export_visit_details(
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        output_dir=os.path.join("reports", "visit_details"),
    )

    # Collect attachment paths
    attachments: List[str] = []
    attachments.append(os.path.join("reports", "daily_visits.csv"))
    daily_visits_xlsx = os.path.join("reports", "daily_visits.xlsx")
    if os.path.exists(daily_visits_xlsx):
        attachments.append(daily_visits_xlsx)

    attachments.append(os.path.join("reports", "team_lead_daily_visits.csv"))
    team_lead_xlsx = os.path.join("reports", "team_lead_daily_visits.xlsx")
    if os.path.exists(team_lead_xlsx):
        attachments.append(team_lead_xlsx)

    attachments.extend([p for p in export_paths if os.path.exists(p)])
    return attachments


def main() -> None:
    load_dotenv()

    # Default to the last full day; or allow overrides via env
    start = os.getenv("REPORT_START_DATE")
    end = os.getenv("REPORT_END_DATE")

    if not start or not end:
        # Default: generate for the current date (inclusive bounds)
        today = date.today().isoformat()
        start = start or today
        end = end or today

    attachments = generate_all_reports_for_range(start, end)

    subject = f"SalesSync Reports for {start} to {end}"
    body_lines = [
        f"Please find attached the SalesSync reports for {start} to {end}.",
        "",
        f"Total attachments: {len(attachments)}",
        "",
        "This is an automated email.",
    ]
    body = "\n".join(body_lines)

    recipients_env = os.getenv("EMAIL_TO")
    to_list = [addr.strip() for addr in recipients_env.split(",") if addr.strip()] if recipients_env else []

    send_email_with_attachments(
        subject=subject,
        body_text=body,
        to_emails=to_list or None,
        attachments=attachments,
    )


if __name__ == "__main__":
    main()
