#!/usr/bin/env python3
"""
Enhanced SalesSync AI Chatbot Web Interface
Uses Llama 3 for improved AI responses
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
import json
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from enhanced_database_qa_system import EnhancedDatabaseQASystem
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

app = Flask(__name__)

# Global variable to store the enhanced Q&A system
qa_system = None

def initialize_qa_system():
    """Initialize the enhanced Q&A system with Llama 3"""
    global qa_system
    try:
        qa_system = EnhancedDatabaseQASystem()
        return True
    except Exception as e:
        print(f"Error initializing Enhanced Q&A system: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with enhanced Llama 3 responses"""
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
                    'error': 'Failed to initialize Enhanced AI system'
                })
        
        # Get response from enhanced AI system
        response = qa_system.answer_question(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'model': 'Llama 3 Enhanced'
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
                    'message': 'Enhanced AI system with Llama 3 initialized successfully',
                    'model': 'Llama 3 Enhanced'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to initialize Enhanced AI system'
                })
        else:
            return jsonify({
                'status': 'ready',
                'message': 'Enhanced AI system with Llama 3 is ready',
                'model': 'Llama 3 Enhanced'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/examples')
def examples():
    """Get example questions"""
    examples = [
        "What are the total checkins this month?",
        "Which agent has the best performance?",
        "Show me the top 10 shops by checkin count",
        "What are the weekly checkin trends?",
        "How many unique shops did we visit?",
        "Which agents are most active?",
        "What's the average checkins per day?",
        "Show me shop visit patterns",
        "What's our agent performance summary?",
        "How many checkins did we have last week?",
        "Which shops haven't been visited recently?",
        "Show me the busiest days of the week",
        "Which agent has the most repeat shop visits?",
        "What's our shop retention rate?",
        "How many agents have worked today?",
        "What's the current month's performance?",
        "Show me agent activity by day",
        "Which agents are underperforming?",
        "What's our daily checkin average?",
        "Show me the latest checkin data",
        "Analyze our team's productivity trends",
        "What insights can you provide about our sales performance?",
        "Compare this month's performance to last month",
        "Identify our top performing strategies",
        "What recommendations do you have for improving sales?"
    ]
    
    return jsonify({
        'success': True,
        'examples': examples
    })

@app.route('/api/model-info')
def model_info():
    """Get information about the AI model"""
    return jsonify({
        'model_name': 'Llama 3.1-1B-Instruct',
        'model_type': 'Enhanced AI Assistant',
        'capabilities': [
            'Natural language processing',
            'Database query analysis',
            'Performance insights',
            'Trend analysis',
            'Strategic recommendations',
            'Real-time data processing'
        ],
        'features': [
            'Quantized for efficiency',
            'Context-aware responses',
            'Professional formatting',
            'Actionable insights',
            'Multi-query understanding'
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Enhanced SalesSync AI Chatbot Web Interface...")
    print("=" * 70)
    print("🤖 Powered by Llama 3.1-1B-Instruct")
    print("=" * 70)
    
    # Initialize the enhanced Q&A system
    if initialize_qa_system():
        print("✅ Enhanced AI system with Llama 3 initialized successfully!")
        print("🌐 Starting web server...")
        print("📱 Open your browser and go to: http://localhost:5002")
        print("=" * 70)
        
        app.run(host='0.0.0.0', port=5002, debug=True)
    else:
        print("❌ Failed to initialize Enhanced AI system")
        print("Please check your database connection and try again")