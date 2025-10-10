#!/usr/bin/env python3
"""
SalesSync AI Assistant Launcher
Simple launcher script for the AI-powered database Q&A system
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'mysql-connector-python',
        'pandas',
        'transformers',
        'torch'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "mysql-connector-python", "pandas", "transformers", "torch", "accelerate"
            ])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def main():
    """Main launcher function"""
    print("🚀 Starting SalesSync AI Assistant...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Cannot start without required dependencies.")
        return
    
    # Import and start the Q&A system
    try:
        from database_qa_system import DatabaseQASystem
        
        print("✅ All systems ready!")
        print("🔗 Connecting to SalesSync database...")
        
        qa_system = DatabaseQASystem()
        qa_system.interactive_session()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all files are in the correct location.")
    except Exception as e:
        print(f"❌ Error starting AI Assistant: {e}")
    finally:
        print("\n👋 SalesSync AI Assistant closed.")

if __name__ == "__main__":
    main()