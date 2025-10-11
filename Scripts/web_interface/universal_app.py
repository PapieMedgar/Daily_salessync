#!/usr/bin/env python3
"""
Universal SalesSync AI Chatbot Web Interface
Can answer ANY question without limitations
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
import json
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from universal_qa_system import UniversalQASystem
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

app = Flask(__name__)

# Global variable to store the universal Q&A system
qa_system = None

def initialize_qa_system():
    """Initialize the universal Q&A system"""
    global qa_system
    try:
        qa_system = UniversalQASystem()
        return True
    except Exception as e:
        print(f"Error initializing Universal Q&A system: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('universal_index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with universal question answering"""
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
                    'error': 'Failed to initialize Universal AI system'
                })
        
        # Get response from universal AI system
        response = qa_system.answer_question(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'model': 'Universal AI Assistant'
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
                    'message': 'Universal AI system initialized successfully',
                    'model': 'Universal AI Assistant',
                    'capabilities': [
                        'Answer ANY question about your data',
                        'No demo question limitations',
                        'Natural language responses',
                        'Comprehensive data analysis',
                        'Intelligent context understanding'
                    ]
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to initialize Universal AI system'
                })
        else:
            return jsonify({
                'status': 'ready',
                'message': 'Universal AI system is ready',
                'model': 'Universal AI Assistant',
                'capabilities': [
                    'Answer ANY question about your data',
                    'No demo question limitations',
                    'Natural language responses',
                    'Comprehensive data analysis',
                    'Intelligent context understanding'
                ]
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/api/examples')
def examples():
    """Get example questions - now showing the unlimited nature"""
    examples = [
        "How many people worked today?",
        "What's our best performing agent?",
        "Show me the busiest day this week",
        "Which shops haven't been visited recently?",
        "What's the average checkins per day?",
        "How many agents do we have?",
        "What's our monthly performance?",
        "Who worked on October 1st, 2025?",
        "Which agent has the most unique shop visits?",
        "What's our team's productivity trend?",
        "How many checkins did we have yesterday?",
        "What's the distribution of work across days?",
        "Which shops are most popular?",
        "How has our performance changed over time?",
        "What insights can you provide about our data?",
        "Compare this month to last month",
        "What patterns do you see in our data?",
        "How can we improve our performance?",
        "What's the breakdown by agent role?",
        "Show me the data for any specific date",
        "What's our current status?",
        "How many total users are in the system?",
        "What's the most active time of day?",
        "Which agents are underperforming?",
        "What recommendations do you have?"
    ]
    
    return jsonify({
        'success': True,
        'examples': examples,
        'note': 'These are just examples - you can ask ANY question!'
    })

@app.route('/api/model-info')
def model_info():
    """Get information about the AI model"""
    return jsonify({
        'model_name': 'Universal AI Assistant',
        'model_type': 'Universal Question Answering System',
        'capabilities': [
            'Answer ANY question about your data',
            'No demo question limitations',
            'Natural language responses',
            'Comprehensive data analysis',
            'Intelligent context understanding',
            'Date-specific queries',
            'Performance analysis',
            'Trend identification',
            'Strategic recommendations',
            'Real-time data processing'
        ],
        'features': [
            'Universal question handling',
            'No JSON responses',
            'Natural conversation',
            'Context-aware responses',
            'Intelligent data extraction',
            'Multi-source data analysis',
            'Date pattern recognition',
            'Performance insights',
            'Trend analysis',
            'Actionable recommendations'
        ],
        'limitations': 'None - ask anything!'
    })

if __name__ == '__main__':
    print("🚀 Starting Universal SalesSync AI Chatbot Web Interface...")
    print("=" * 70)
    print("🤖 Powered by Universal AI Assistant")
    print("💡 Can answer ANY question - no limitations!")
    print("=" * 70)
    
    # Initialize the universal Q&A system
    if initialize_qa_system():
        print("✅ Universal AI system initialized successfully!")
        print("🌐 Starting web server...")
        print("📱 Open your browser and go to: http://localhost:5003")
        print("=" * 70)
        
        app.run(host='0.0.0.0', port=5003, debug=True)
    else:
        print("❌ Failed to initialize Universal AI system")
        print("Please check your database connection and try again")