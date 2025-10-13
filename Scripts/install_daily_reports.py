#!/usr/bin/env python3
"""
Installation script for daily email reports

This script provides multiple options for setting up automated daily reports:
1. Cron job (recommended for most systems)
2. Systemd timer (for systemd-based Linux systems)
3. Manual testing

Usage:
    python Scripts/install_daily_reports.py [--method cron|systemd|test]
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path

def check_requirements():
    """Check if all required dependencies are installed."""
    try:
        import mysql.connector
        import openpyxl
        from dotenv import load_dotenv
        print("✓ All required Python packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please install requirements: pip install -r Scripts/requirements.txt")
        return False

def check_env_config():
    """Check if .env file is properly configured."""
    env_file = Path(".env")
    if not env_file.exists():
        print("✗ .env file not found")
        print("Please copy .env.example to .env and configure your email settings:")
        print("  cp .env.example .env")
        return False
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['SENDER_EMAIL', 'SENDER_PASSWORD', 'EMAIL_RECIPIENTS']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        print("Please configure these in your .env file")
        return False
    
    print("✓ .env file is properly configured")
    return True

def setup_cron():
    """Set up cron job for daily reports."""
    print("Setting up cron job...")
    
    project_dir = Path(__file__).parent.parent.absolute()
    python_path = shutil.which('python3')
    script_path = project_dir / "Scripts" / "email_reports_scheduler.py"
    wrapper_script = project_dir / "Scripts" / "run_daily_reports.sh"
    
    # Create wrapper script
    wrapper_content = f"""#!/bin/bash
# Wrapper script for daily reports
cd "{project_dir}"
export PYTHONPATH="{project_dir}:$PYTHONPATH"
"{python_path}" "{script_path}" >> "{project_dir}/reports/email_reports.log" 2>&1
"""
    
    with open(wrapper_script, 'w') as f:
        f.write(wrapper_content)
    
    os.chmod(wrapper_script, 0o755)
    
    # Add cron job
    cron_job = f"0 16 * * * {wrapper_script}"
    
    try:
        # Get current crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_crontab = result.stdout if result.returncode == 0 else ""
        
        # Check if job already exists
        if "run_daily_reports.sh" in current_crontab:
            print("Cron job already exists. Updating...")
            # Remove existing job and add new one
            lines = [line for line in current_crontab.split('\n') if "run_daily_reports.sh" not in line]
            new_crontab = '\n'.join(lines) + f'\n{cron_job}\n'
        else:
            new_crontab = current_crontab + f'\n{cron_job}\n'
        
        # Install new crontab
        subprocess.run(['crontab', '-'], input=new_crontab, text=True, check=True)
        print("✓ Cron job installed successfully")
        print(f"  Daily reports will run at 4:00 PM")
        print(f"  Logs: {project_dir}/reports/email_reports.log")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install cron job: {e}")
        return False
    
    return True

def setup_systemd():
    """Set up systemd timer for daily reports."""
    print("Setting up systemd timer...")
    
    project_dir = Path(__file__).parent.parent.absolute()
    service_file = project_dir / "Scripts" / "daily-reports.service"
    timer_file = project_dir / "Scripts" / "daily-reports.timer"
    
    # Update service file with correct paths
    service_content = f"""[Unit]
Description=Daily Email Reports Service
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory={project_dir}
Environment=PYTHONPATH={project_dir}:/usr/bin/python3
ExecStart=/usr/bin/python3 {project_dir}/Scripts/email_reports_scheduler.py
StandardOutput=append:{project_dir}/reports/email_reports.log
StandardError=append:{project_dir}/reports/email_reports.log

[Install]
WantedBy=multi-user.target
"""
    
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    try:
        # Copy files to systemd directory
        subprocess.run(['sudo', 'cp', str(service_file), '/etc/systemd/system/'], check=True)
        subprocess.run(['sudo', 'cp', str(timer_file), '/etc/systemd/system/'], check=True)
        
        # Reload systemd and enable timer
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        subprocess.run(['sudo', 'systemctl', 'enable', 'daily-reports.timer'], check=True)
        subprocess.run(['sudo', 'systemctl', 'start', 'daily-reports.timer'], check=True)
        
        print("✓ Systemd timer installed successfully")
        print("  Daily reports will run at 4:00 PM")
        print(f"  Logs: {project_dir}/reports/email_reports.log")
        print("  To check status: sudo systemctl status daily-reports.timer")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install systemd timer: {e}")
        return False
    
    return True

def test_reports():
    """Test the reports generation and email sending."""
    print("Testing reports generation...")
    
    try:
        project_dir = Path(__file__).parent.parent.absolute()
        script_path = project_dir / "Scripts" / "email_reports_scheduler.py"
        
        # Change to project directory and run script
        os.chdir(project_dir)
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Reports generated and email sent successfully")
            print("Check your email inbox for the reports")
        else:
            print(f"✗ Reports generation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing reports: {e}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Install daily email reports automation')
    parser.add_argument('--method', choices=['cron', 'systemd', 'test'], 
                       default='cron', help='Installation method')
    
    args = parser.parse_args()
    
    print("Daily Email Reports Installation")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment configuration
    if not check_env_config():
        sys.exit(1)
    
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    success = False
    
    if args.method == 'cron':
        success = setup_cron()
    elif args.method == 'systemd':
        success = setup_systemd()
    elif args.method == 'test':
        success = test_reports()
    
    if success:
        print("\n✓ Installation completed successfully!")
        print("\nNext steps:")
        print("1. Verify your email settings in .env file")
        print("2. Test the setup by running: python Scripts/email_reports_scheduler.py")
        print("3. Check the logs at reports/email_reports.log")
    else:
        print("\n✗ Installation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()