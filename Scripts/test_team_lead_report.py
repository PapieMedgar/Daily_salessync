#!/usr/bin/env python3
"""
Test script for team_lead_visits_report.py

This script tests the team lead visits report with automatic daily visits generation.
"""

import os
import sys
import subprocess
from datetime import date, timedelta

def test_team_lead_report():
    """Test the team lead visits report."""
    print("Testing team lead visits report...")
    
    # Change to the project directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)
    
    # Run the team lead visits report
    script_path = os.path.join("Scripts", "team_lead_visits_report.py")
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, cwd=project_dir)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Team lead visits report completed successfully!")
            
            # Check if output files were created
            reports_dir = "reports"
            if os.path.exists(reports_dir):
                files = os.listdir(reports_dir)
                csv_files = [f for f in files if f.startswith("team_lead_daily_visits") and f.endswith(".csv")]
                xlsx_files = [f for f in files if f.startswith("team_lead_daily_visits") and f.endswith(".xlsx")]
                
                print(f"Generated files:")
                for f in csv_files + xlsx_files:
                    print(f"  - {f}")
            else:
                print("⚠️  Reports directory not found")
                
        else:
            print(f"❌ Team lead visits report failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running team lead visits report: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_team_lead_report()
    sys.exit(0 if success else 1)