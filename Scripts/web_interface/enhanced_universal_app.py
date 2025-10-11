#!/usr/bin/env python3
"""
Enhanced Universal SalesSync AI Chatbot Web Interface
Integrates Tiny AI Summarizer for executive summary generation
Can answer ANY question and generate comprehensive executive summaries
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
import json
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from enhanced_universal_qa_system import EnhancedUniversalQASystem
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

app = Flask(__name__)

# Global variable to store the enhanced universal Q&A system
qa_system = None

def initialize_qa_system():
    """Initialize the enhanced universal Q&A system"""
    global qa_system
    try:
        qa_system = EnhancedUniversalQASystem()
        return True
    except Exception as e:
        print(f"Error initializing Enhanced Universal Q&A system: {e}")
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('enhanced_universal_index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with enhanced universal question answering"""
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
                    'error': 'Failed to initialize Enhanced Universal AI system'
                })
        
        # Get response from enhanced universal AI system
        response = qa_system.answer_question(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'model': 'Enhanced Universal AI Assistant with Tiny AI Summarizer'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/executive-summary', methods=['POST'])
def generate_executive_summary():
    """Generate comprehensive executive summary"""
    global qa_system
    
    try:
        # Initialize Q&A system if not already done
        if qa_system is None:
            if not initialize_qa_system():
                return jsonify({
                    'success': False,
                    'error': 'Failed to initialize Enhanced Universal AI system'
                })
        
        # Generate executive summary
        summary = qa_system.generate_executive_summary()
        
        return jsonify({
            'success': True,
            'summary': summary,
            'timestamp': datetime.now().isoformat(),
            'model': 'Enhanced Universal AI Assistant with Tiny AI Summarizer'
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
                    'message': 'Enhanced Universal AI system initialized successfully',
                    'model': 'Enhanced Universal AI Assistant with Tiny AI Summarizer',
                    'capabilities': [
                        'Answer ANY question about your data',
                        'Generate comprehensive executive summaries',
                        'No demo question limitations',
                        'Natural language responses',
                        'Tiny AI-powered analysis',
                        'Comprehensive data analysis',
                        'Intelligent context understanding'
                    ]
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to initialize Enhanced Universal AI system'
                })
        else:
            return jsonify({
                'status': 'ready',
                'message': 'Enhanced Universal AI system is ready',
                'model': 'Enhanced Universal AI Assistant with Tiny AI Summarizer',
                'capabilities': [
                    'Answer ANY question about your data',
                    'Generate comprehensive executive summaries',
                    'No demo question limitations',
                    'Natural language responses',
                    'Tiny AI-powered analysis',
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
    """Get example questions"""
    examples = [
        "Generate an executive summary",
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
        "Show me the data for any specific date",
        "What's our current status?",
        "How many total users are in the system?",
        "What's the most active time of day?",
        "Which agents are underperforming?",
        "What recommendations do you have?",
        "Create a comprehensive business report",
        "Analyze our team's performance",
        "What are our key performance indicators?",
        "Show me the executive dashboard",
        "Generate a management summary"
    ]
    
    return jsonify({
        'success': True,
        'examples': examples,
        'note': 'These are just examples - you can ask ANY question!',
        'special_features': [
            'Type "executive summary" for comprehensive reports',
            'Ask about specific dates and time periods',
            'Get performance insights and recommendations',
            'Analyze trends and patterns'
        ]
    })

@app.route('/api/model-info')
def model_info():
    """Get information about the AI model"""
    return jsonify({
        'model_name': 'Enhanced Universal AI Assistant',
        'model_type': 'Universal Question Answering System with Tiny AI Summarizer',
        'capabilities': [
            'Answer ANY question about your data',
            'Generate comprehensive executive summaries',
            'No demo question limitations',
            'Natural language responses',
            'Tiny AI-powered analysis',
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
            'Executive summary generation',
            'Tiny AI model integration',
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
        'limitations': 'None - ask anything!',
        'special_commands': [
            'Type "executive summary" for comprehensive reports',
            'Ask about specific dates and time periods',
            'Get performance insights and recommendations'
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Enhanced Universal SalesSync AI Chatbot Web Interface...")
    print("=" * 80)
    print("🤖 Powered by Enhanced Universal AI Assistant with Tiny AI Summarizer")
    print("💡 Can answer ANY question and generate executive summaries!")
    print("📊 Comprehensive business intelligence platform")
    print("=" * 80)
    
    # Initialize the enhanced universal Q&A system
    if initialize_qa_system():
        print("✅ Enhanced Universal AI system initialized successfully!")
        print("🌐 Starting web server...")
        print("📱 Open your browser and go to: http://localhost:5004")
        print("=" * 80)
        
        app.run(host='0.0.0.0', port=5004, debug=True)
    else:
        print("❌ Failed to initialize Enhanced Universal AI system")
        print("Please check your database connection and try again")