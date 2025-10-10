#!/usr/bin/env python3
"""
SalesSync AI Chatbot Web Interface Launcher
Simple launcher for the web-based chatbot interface
"""

import sys
import os
import subprocess
import webbrowser
import time
import threading

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask',
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
                "flask", "mysql-connector-python", "pandas", "transformers", "torch", "accelerate"
            ])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def open_browser():
    """Open browser after a short delay"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 Opening web browser...")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("Please open your browser and go to: http://localhost:5000")

def main():
    """Main launcher function"""
    print("🚀 Starting SalesSync AI Chatbot Web Interface...")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Cannot start without required dependencies.")
        return
    
    # Change to web interface directory
    web_dir = os.path.join(os.path.dirname(__file__), 'web_interface')
    if not os.path.exists(web_dir):
        print(f"❌ Web interface directory not found: {web_dir}")
        return
    
    os.chdir(web_dir)
    
    print("✅ All systems ready!")
    print("🔗 Starting web server...")
    print("📱 The chatbot will be available at: http://localhost:5000")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Start the Flask app
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Web server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting web server: {e}")

if __name__ == "__main__":
    main()