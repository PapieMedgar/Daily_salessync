#!/bin/bash
# Wrapper script for daily reports
cd "/workspace"
export PYTHONPATH="/workspace:"
"/usr/bin/python3" "/workspace/Scripts/email_reports_scheduler.py" >> "/workspace/reports/email_reports.log" 2>&1
