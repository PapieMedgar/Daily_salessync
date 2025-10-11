#!/usr/bin/env python3
"""
Launch Universal SalesSync AI Assistant
Can answer ANY question without limitations
"""

import sys
import os
import subprocess
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

def launch_universal_ai():
    """Launch the Universal AI Assistant"""
    print("🚀 Launching Universal SalesSync AI Assistant...")
    print("=" * 60)
    print("🤖 Universal AI Assistant - No Limitations!")
    print("💡 Can answer ANY question about your data")
    print("🌐 Natural language responses - no JSON!")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('universal_qa_system.py'):
        print("❌ Error: universal_qa_system.py not found!")
        print("Please run this script from the Scripts directory")
        return False
    
    try:
        # Launch the web interface
        print("🌐 Starting Universal Web Interface...")
        print("📱 Open your browser and go to: http://localhost:5003")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Change to web_interface directory and run the universal app
        web_interface_dir = os.path.join(os.path.dirname(__file__), 'web_interface')
        os.chdir(web_interface_dir)
        
        # Run the universal app
        subprocess.run([sys.executable, 'universal_app.py'])
        
    except KeyboardInterrupt:
        print("\n\n👋 Universal AI Assistant stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error launching Universal AI Assistant: {e}")
        return False
    
    return True

if __name__ == "__main__":
    launch_universal_ai()