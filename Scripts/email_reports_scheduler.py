#!/usr/bin/env python3
"""
Daily Email Reports Scheduler

This script runs the three report scripts daily at 4pm and sends the generated reports via email.
It uses cron job scheduling to run automatically.

Usage:
    python Scripts/email_reports_scheduler.py

The script will:
1. Run daily_visits_report.py to generate daily visits report
2. Run team_lead_visits_report.py to generate team lead visits report  
3. Run team_lead_visit_details_export.py to generate visit details export
4. Send all generated reports via email to configured recipients
"""

import os
import sys
import subprocess
import smtplib
import logging
from datetime import datetime, date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reports/email_reports.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailReportsScheduler:
    def __init__(self):
        load_dotenv()
        self.reports_dir = "reports"
        self.scripts_dir = "Scripts"
        
        # Email configuration from environment variables
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipients = os.getenv('EMAIL_RECIPIENTS', '').split(',')
        
        # Validate email configuration
        if not self.sender_email or not self.sender_password:
            raise ValueError("SENDER_EMAIL and SENDER_PASSWORD must be set in environment variables")
        
        if not self.recipients or self.recipients == ['']:
            raise ValueError("EMAIL_RECIPIENTS must be set in environment variables (comma-separated)")
        
        # Clean up recipients list
        self.recipients = [email.strip() for email in self.recipients if email.strip()]
        
        logger.info(f"Email scheduler initialized for {len(self.recipients)} recipients")

    def run_report_script(self, script_name: str, args: List[str] = None) -> bool:
        """Run a report script and return success status."""
        try:
            script_path = os.path.join(self.scripts_dir, script_name)
            cmd = [sys.executable, script_path]
            if args:
                cmd.extend(args)
            
            logger.info(f"Running script: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
            
            if result.returncode == 0:
                logger.info(f"Successfully ran {script_name}")
                if result.stdout:
                    logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"Failed to run {script_name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running {script_name}: {str(e)}")
            return False

    def generate_reports(self) -> Dict[str, Any]:
        """Generate all reports and return status and file paths."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Format dates for scripts
        start_date = yesterday.strftime('%Y-%m-%d')
        end_date = yesterday.strftime('%Y-%m-%d')
        
        logger.info(f"Generating reports for {start_date}")
        
        results = {
            'success': True,
            'files': [],
            'errors': []
        }
        
        # 1. Generate daily visits report
        daily_visits_csv = os.path.join(self.reports_dir, f"daily_visits_{start_date}.csv")
        if self.run_report_script('daily_visits_report.py', [start_date, end_date, daily_visits_csv]):
            results['files'].extend([
                daily_visits_csv,
                daily_visits_csv.replace('.csv', '.xlsx')
            ])
        else:
            results['success'] = False
            results['errors'].append("Failed to generate daily visits report")
        
        # 2. Generate team lead visits report (depends on daily visits report)
        team_lead_csv = os.path.join(self.reports_dir, f"team_lead_daily_visits_{start_date}.csv")
        if self.run_report_script('team_lead_visits_report.py', [daily_visits_csv, team_lead_csv]):
            results['files'].extend([
                team_lead_csv,
                team_lead_csv.replace('.csv', '.xlsx')
            ])
        else:
            results['success'] = False
            results['errors'].append("Failed to generate team lead visits report")
        
        # 3. Generate visit details export
        visit_details_dir = os.path.join(self.reports_dir, f"visit_details_{start_date}")
        if self.run_report_script('team_lead_visit_details_export.py', [start_date, end_date, visit_details_dir]):
            # Add all files from visit details directory
            if os.path.exists(visit_details_dir):
                for file in os.listdir(visit_details_dir):
                    if file.endswith(('.csv', '.xlsx')):
                        results['files'].append(os.path.join(visit_details_dir, file))
        else:
            results['success'] = False
            results['errors'].append("Failed to generate visit details export")
        
        return results

    def send_email(self, report_files: List[str], errors: List[str] = None) -> bool:
        """Send email with report attachments."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = f"Daily Reports - {date.today().strftime('%Y-%m-%d')}"
            
            # Email body
            body = f"""
Dear Team,

Please find attached the daily reports for {date.today().strftime('%B %d, %Y')}.

Reports included:
- Daily Visits Report (CSV & Excel)
- Team Lead Visits Report (CSV & Excel)  
- Visit Details Export by Team Lead (CSV & Excel files)

"""
            
            if errors:
                body += f"\nNote: Some reports failed to generate:\n"
                for error in errors:
                    body += f"- {error}\n"
            
            body += f"\nGenerated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            body += "\nBest regards,\nAutomated Report System"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach files
            attached_files = []
            for file_path in report_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            
                            filename = os.path.basename(file_path)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {filename}'
                            )
                            msg.attach(part)
                            attached_files.append(filename)
                    except Exception as e:
                        logger.warning(f"Could not attach {file_path}: {str(e)}")
                else:
                    logger.warning(f"File not found: {file_path}")
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            
            text = msg.as_string()
            server.sendmail(self.sender_email, self.recipients, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {len(self.recipients)} recipients")
            logger.info(f"Attached files: {', '.join(attached_files)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def run_daily_reports(self):
        """Main method to run daily reports and send email."""
        logger.info("Starting daily reports generation and email sending")
        
        try:
            # Generate reports
            results = self.generate_reports()
            
            # Send email
            if results['files']:
                email_success = self.send_email(results['files'], results['errors'])
                if email_success:
                    logger.info("Daily reports process completed successfully")
                else:
                    logger.error("Failed to send email with reports")
            else:
                logger.error("No report files generated")
                
        except Exception as e:
            logger.error(f"Error in daily reports process: {str(e)}")

def main():
    """Main entry point for the scheduler."""
    try:
        scheduler = EmailReportsScheduler()
        scheduler.run_daily_reports()
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()