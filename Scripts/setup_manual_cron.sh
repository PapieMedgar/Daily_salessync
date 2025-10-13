#!/bin/bash

# Manual cron setup for daily email reports
# Run this script to set up the cron job manually

echo "Setting up daily email reports cron job..."

# Get the current directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_PATH="$(which python3)"
SCRIPT_PATH="$PROJECT_DIR/Scripts/email_reports_scheduler.py"

echo "Project directory: $PROJECT_DIR"
echo "Python path: $PYTHON_PATH"
echo "Script path: $SCRIPT_PATH"

# Create reports directory if it doesn't exist
mkdir -p "$PROJECT_DIR/reports"

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

echo "Wrapper script created: $WRAPPER_SCRIPT"

# Display the cron job command
echo ""
echo "To set up the cron job, run the following command:"
echo ""
echo "crontab -e"
echo ""
echo "Then add this line to run daily at 4:00 PM:"
echo ""
echo "0 16 * * * $WRAPPER_SCRIPT"
echo ""
echo "Or run this command to add it automatically:"
echo ""
echo "(crontab -l 2>/dev/null; echo \"0 16 * * * $WRAPPER_SCRIPT\") | crontab -"
echo ""
echo "To test the setup, run:"
echo "  $PYTHON_PATH $SCRIPT_PATH"
echo ""
echo "To view logs:"
echo "  tail -f $PROJECT_DIR/reports/email_reports.log"