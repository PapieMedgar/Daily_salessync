# Daily Reports Setup Guide

## Quick Setup for Your Configuration

The daily reports are configured to send to:
- **papie@gonxt.tech**
- **luke@gonxt.tech** 
- **antoinette@bridgethegap.site**

### Step 1: Configure Your Email Settings

1. Edit the `.env` file and replace the placeholder values:

```bash
nano .env
```

Update these lines with your actual email credentials:
```env
SENDER_EMAIL=your-actual-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**For Gmail users:**
- Go to your Google Account settings
- Enable 2-factor authentication
- Generate an App Password for this application
- Use the App Password (not your regular password)

### Step 2: Test Email Configuration

Before setting up automation, test that emails work:

```bash
python Scripts/test_email_config.py
```

This will send a test email to all three recipients to verify the configuration.

### Step 3: Install the Automation

Choose one method:

#### Option A: Cron Job (Recommended)
```bash
python Scripts/install_daily_reports.py --method cron
```

#### Option B: Test First
```bash
python Scripts/install_daily_reports.py --method test
```

### Step 4: Verify Setup

Check that everything is working:

```bash
# View current cron jobs
crontab -l

# Check logs
tail -f reports/email_reports.log

# Test manual run
python Scripts/email_reports_scheduler.py
```

## What Happens Daily

Every day at 4:00 PM, the system will:

1. **Generate Reports:**
   - Daily Visits Report (CSV & Excel)
   - Team Lead Visits Report (CSV & Excel)
   - Visit Details Export by Team Lead (CSV & Excel files)

2. **Send Email:**
   - To: papie@gonxt.tech, luke@gonxt.tech, antoinette@bridgethegap.site
   - Subject: "Daily Reports - YYYY-MM-DD"
   - Attachments: All generated report files

3. **Log Activity:**
   - All operations logged to `reports/email_reports.log`

## Troubleshooting

### Email Not Sending
```bash
# Test email configuration
python Scripts/test_email_config.py

# Check logs
tail -n 20 reports/email_reports.log
```

### Reports Not Generating
```bash
# Test individual scripts
python Scripts/daily_visits_report.py
python Scripts/team_lead_visits_report.py
python Scripts/team_lead_visit_details_export.py
```

### Cron Job Issues
```bash
# Check if cron is running
sudo systemctl status cron

# View cron logs
journalctl -u cron

# Check your cron jobs
crontab -l
```

## Manual Report Generation

To generate reports for a specific date:

```bash
# Generate for yesterday
python Scripts/email_reports_scheduler.py

# Or generate for specific date
python Scripts/daily_visits_report.py 2024-01-15 2024-01-15 reports/daily_visits_2024-01-15.csv
```

## File Locations

- **Configuration:** `.env`
- **Logs:** `reports/email_reports.log`
- **Generated Reports:** `reports/` directory
- **Scripts:** `Scripts/` directory

## Need Help?

1. Check the logs: `tail -f reports/email_reports.log`
2. Test email: `python Scripts/test_email_config.py`
3. Test reports: `python Scripts/email_reports_scheduler.py`
4. Check cron: `crontab -l`

The system is now configured to automatically send daily reports to the three specified email addresses every day at 4:00 PM.