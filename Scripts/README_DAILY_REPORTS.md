# Daily Email Reports Automation

This system automatically generates and sends daily reports via email at 4:00 PM every day. It runs three report scripts and emails the generated files to configured recipients.

## Features

- **Automated Daily Execution**: Runs at 4:00 PM every day
- **Multiple Report Types**: 
  - Daily Visits Report (CSV & Excel)
  - Team Lead Visits Report (CSV & Excel)
  - Visit Details Export by Team Lead (CSV & Excel files)
- **Email Delivery**: Sends all reports as email attachments
- **Logging**: Comprehensive logging of all operations
- **Flexible Scheduling**: Supports both cron and systemd scheduling

## Quick Setup

### 1. Configure Email Settings

Copy the example environment file and configure your email settings:

```bash
cp .env.example .env
```

Edit `.env` with your email configuration:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
```

**For Gmail users:**
- Use an App Password instead of your regular password
- Enable 2-factor authentication first
- Generate an App Password in your Google Account settings

### 2. Install Dependencies

```bash
pip install -r Scripts/requirements.txt
```

### 3. Install the Automation

Choose one of the following methods:

#### Option A: Cron Job (Recommended)
```bash
python Scripts/install_daily_reports.py --method cron
```

#### Option B: Systemd Timer (Linux systems with systemd)
```bash
python Scripts/install_daily_reports.py --method systemd
```

#### Option C: Test Only
```bash
python Scripts/install_daily_reports.py --method test
```

## Manual Setup

If you prefer to set up manually:

### Using Cron

1. Make the setup script executable:
```bash
chmod +x Scripts/setup_daily_reports.sh
```

2. Run the setup script:
```bash
./Scripts/setup_daily_reports.sh
```

### Using Systemd

1. Copy service and timer files:
```bash
sudo cp Scripts/daily-reports.service /etc/systemd/system/
sudo cp Scripts/daily-reports.timer /etc/systemd/system/
```

2. Enable and start the timer:
```bash
sudo systemctl daemon-reload
sudo systemctl enable daily-reports.timer
sudo systemctl start daily-reports.timer
```

## Testing

### Test the Reports Generation
```bash
python Scripts/email_reports_scheduler.py
```

### Check Cron Jobs
```bash
crontab -l
```

### Check Systemd Timer Status
```bash
sudo systemctl status daily-reports.timer
sudo systemctl list-timers daily-reports.timer
```

## Monitoring

### View Logs
```bash
tail -f reports/email_reports.log
```

### Check Recent Logs
```bash
tail -n 50 reports/email_reports.log
```

## Troubleshooting

### Common Issues

1. **Email not sending**
   - Check your email credentials in `.env`
   - Verify SMTP server settings
   - For Gmail, ensure you're using an App Password

2. **Reports not generating**
   - Check database connection in `db_config.py`
   - Verify the report scripts work manually
   - Check the logs for specific error messages

3. **Cron job not running**
   - Check if cron service is running: `sudo systemctl status cron`
   - Verify the cron job exists: `crontab -l`
   - Check system logs: `journalctl -u cron`

4. **Systemd timer not running**
   - Check timer status: `sudo systemctl status daily-reports.timer`
   - Check service status: `sudo systemctl status daily-reports.service`
   - View logs: `journalctl -u daily-reports.service`

### Manual Report Generation

To generate reports manually for a specific date:

```bash
# Generate daily visits report
python Scripts/daily_visits_report.py 2024-01-15 2024-01-15 reports/daily_visits_2024-01-15.csv

# Generate team lead visits report
python Scripts/team_lead_visits_report.py reports/daily_visits_2024-01-15.csv reports/team_lead_daily_visits_2024-01-15.csv

# Generate visit details export
python Scripts/team_lead_visit_details_export.py 2024-01-15 2024-01-15 reports/visit_details_2024-01-15
```

## File Structure

```
Scripts/
├── email_reports_scheduler.py    # Main scheduler script
├── install_daily_reports.py      # Installation script
├── setup_daily_reports.sh        # Cron setup script
├── daily-reports.service         # Systemd service file
├── daily-reports.timer           # Systemd timer file
└── README_DAILY_REPORTS.md       # This file

reports/
├── email_reports.log             # Scheduler logs
├── daily_visits_YYYY-MM-DD.csv   # Generated reports
├── daily_visits_YYYY-MM-DD.xlsx
├── team_lead_daily_visits_YYYY-MM-DD.csv
├── team_lead_daily_visits_YYYY-MM-DD.xlsx
└── visit_details_YYYY-MM-DD/     # Visit details by team lead
    ├── visit_details_*.csv
    └── visit_details_*.xlsx
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SMTP_SERVER` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SENDER_EMAIL` | Email address to send from | Required |
| `SENDER_PASSWORD` | Email password/app password | Required |
| `EMAIL_RECIPIENTS` | Comma-separated recipient emails | Required |

### Database Configuration

The system uses the existing database configuration from `db_config.py`. Ensure your database connection is working before setting up the automation.

## Security Notes

- Store your `.env` file securely and never commit it to version control
- Use App Passwords for Gmail instead of your main password
- Consider using a dedicated email account for automated reports
- Regularly rotate your email credentials

## Support

If you encounter issues:

1. Check the logs in `reports/email_reports.log`
2. Test the individual report scripts manually
3. Verify your email configuration
4. Check the scheduling system (cron or systemd) status

For additional help, review the individual script documentation or contact your system administrator.