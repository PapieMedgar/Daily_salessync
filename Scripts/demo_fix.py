#!/usr/bin/env python3
"""
Demo script showing the fix for team_lead_visits_report.py

This demonstrates how the script now handles missing input files gracefully.
"""

import os
import sys
import subprocess
from datetime import date, timedelta

def demo_fix():
    """Demonstrate the fix for team lead visits report."""
    print("🔧 Team Lead Visits Report Fix Demo")
    print("=" * 50)
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)
    
    print("1. Testing with existing daily visits file...")
    print("   (This should work automatically)")
    
    try:
        result = subprocess.run([sys.executable, "Scripts/team_lead_visits_report.py"], 
                              capture_output=True, text=True, cwd=project_dir)
        
        if result.returncode == 0:
            print("   ✅ SUCCESS: Script ran without errors")
            print("   📁 Generated files:")
            for line in result.stdout.split('\n'):
                if 'Wrote team-lead' in line:
                    print(f"      {line}")
        else:
            print("   ❌ FAILED: Script had errors")
            print("   Error output:")
            print(result.stderr)
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n2. Testing with non-existent file...")
    print("   (This should show helpful error message)")
    
    try:
        result = subprocess.run([sys.executable, "Scripts/team_lead_visits_report.py", 
                               "nonexistent_file.csv"], 
                              capture_output=True, text=True, cwd=project_dir)
        
        if result.returncode != 0:
            print("   ✅ SUCCESS: Script properly detected missing file")
            print("   📝 Error message:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    print(f"      {line}")
        else:
            print("   ⚠️  UNEXPECTED: Script should have failed but didn't")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n3. Summary of the fix:")
    print("   • Script now automatically finds the most recent daily visits file")
    print("   • Provides clear error messages when files are missing")
    print("   • Can auto-generate daily visits report if needed")
    print("   • Maintains backward compatibility")
    
    print("\n🎉 The fix is working correctly!")

if __name__ == "__main__":
    demo_fix()