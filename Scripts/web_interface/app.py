#!/usr/bin/env python3
"""
SalesSync AI Chatbot Web Interface
Flask backend for the web-based chatbot interface
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
import json
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from database_qa_system import DatabaseQASystem
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

app = Flask(__name__)

# Global variable to store the Q&A system
qa_system = None

def initialize_qa_system():
    """Initialize the Q&A system"""
    global qa_system
    try:
        qa_system = DatabaseQASystem()
        return True
    except Exception as e:
        print(f"Error initializing Q&A system: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    global qa_system
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Empty message'
            })
        
        # Initialize Q&A system if not already done
        if qa_system is None:
            if not initialize_qa_system():
                return jsonify({
                    'success': False,
                    'error': 'Failed to initialize AI system'
                })
        
        # Get response from AI system
        response = qa_system.answer_question(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/status')
def status():
    """Check system status"""
    global qa_system
    
    try:
        if qa_system is None:
            if initialize_qa_system():
                return jsonify({
                    'status': 'ready',
                    'message': 'AI system initialized successfully'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to initialize AI system'
                })
        else:
            return jsonify({
                'status': 'ready',
                'message': 'AI system is ready'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/examples')
def examples():
    """Get example questions - removed for professional interface"""
    return jsonify({
        'success': True,
        'examples': []
    })

if __name__ == '__main__':
    print("🚀 Starting SalesSync AI Chatbot Web Interface...")
    print("=" * 60)
    
    # Initialize the Q&A system
    if initialize_qa_system():
        print("✅ AI system initialized successfully!")
        print("🌐 Starting web server...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("=" * 60)
        
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("❌ Failed to initialize AI system")
        print("Please check your database connection and try again")