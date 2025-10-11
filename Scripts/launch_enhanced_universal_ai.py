#!/usr/bin/env python3
"""
Launch Enhanced Universal SalesSync AI Assistant
Can answer ANY question and generate executive summaries using Tiny AI
"""

import sys
import os
import subprocess
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

def launch_enhanced_universal_ai():
    """Launch the Enhanced Universal AI Assistant"""
    print("🚀 Launching Enhanced Universal SalesSync AI Assistant...")
    print("=" * 70)
    print("🤖 Enhanced Universal AI Assistant - No Limitations!")
    print("💡 Can answer ANY question about your data")
    print("📊 Generate comprehensive executive summaries")
    print("🧠 Powered by Tiny AI Summarizer technology")
    print("🌐 Natural language responses - no JSON!")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists('enhanced_universal_qa_system.py'):
        print("❌ Error: enhanced_universal_qa_system.py not found!")
        print("Please run this script from the Scripts directory")
        return False
    
    try:
        # Launch the web interface
        print("🌐 Starting Enhanced Universal Web Interface...")
        print("📱 Open your browser and go to: http://localhost:5004")
        print("=" * 70)
        print("Press Ctrl+C to stop the server")
        print("=" * 70)
        
        # Change to web_interface directory and run the enhanced universal app
        web_interface_dir = os.path.join(os.path.dirname(__file__), 'web_interface')
        os.chdir(web_interface_dir)
        
        # Run the enhanced universal app
        subprocess.run([sys.executable, 'enhanced_universal_app.py'])
        
    except KeyboardInterrupt:
        print("\n\n👋 Enhanced Universal AI Assistant stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error launching Enhanced Universal AI Assistant: {e}")
        return False
    
    return True

if __name__ == "__main__":
    launch_enhanced_universal_ai()