#!/bin/bash

# Setup script for daily email reports
# This script sets up the cron job to run daily reports at 4pm

set -e

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_PATH="$(which python3)"
SCRIPT_PATH="$PROJECT_DIR/Scripts/email_reports_scheduler.py"

echo "Setting up daily email reports..."
echo "Project directory: $PROJECT_DIR"
echo "Python path: $PYTHON_PATH"
echo "Script path: $SCRIPT_PATH"

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Warning: .env file not found. Please copy .env.example to .env and configure your email settings."
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your email configuration."
fi

# Create reports directory if it doesn't exist
mkdir -p "$PROJECT_DIR/reports"

# Make the script executable
chmod +x "$SCRIPT_PATH"

# Create a wrapper script for cron
WRAPPER_SCRIPT="$PROJECT_DIR/Scripts/run_daily_reports.sh"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# Wrapper script for daily reports
cd "$PROJECT_DIR"
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
"$PYTHON_PATH" "$SCRIPT_PATH" >> "$PROJECT_DIR/reports/email_reports.log" 2>&1
EOF

chmod +x "$WRAPPER_SCRIPT"

# Add cron job (runs daily at 4:00 PM)
CRON_JOB="0 16 * * * $WRAPPER_SCRIPT"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "run_daily_reports.sh"; then
    echo "Cron job already exists. Updating..."
    # Remove existing job and add new one
    (crontab -l 2>/dev/null | grep -v "run_daily_reports.sh"; echo "$CRON_JOB") | crontab -
else
    echo "Adding new cron job..."
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
fi

echo "Setup complete!"
echo "Daily reports will run at 4:00 PM every day."
echo "Logs will be written to: $PROJECT_DIR/reports/email_reports.log"
echo ""
echo "To test the setup, run:"
echo "  $PYTHON_PATH $SCRIPT_PATH"
echo ""
echo "To view current cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove the cron job:"
echo "  crontab -l | grep -v 'run_daily_reports.sh' | crontab -"