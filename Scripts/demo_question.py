#!/usr/bin/env python3
"""
Demo script to test the AI Q&A system with a specific question
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

try:
    from database_qa_system import DatabaseQASystem
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def demo_question(question: str):
    """Demo a specific question"""
    print("🚀 SalesSync AI Assistant Demo")
    print("=" * 50)
    print(f"Question: {question}")
    print("=" * 50)
    
    try:
        # Initialize the Q&A system
        print("🔗 Connecting to database and initializing AI...")
        qa_system = DatabaseQASystem()
        
        # Ask the question
        print("🤖 Processing your question...")
        answer = qa_system.answer_question(question)
        
        # Display the answer
        print("\n" + "=" * 50)
        print("📊 AI RESPONSE:")
        print("=" * 50)
        print(answer)
        print("=" * 50)
        
        # Close the connection
        qa_system.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Demo questions
    demo_questions = [
        "What are the total checkins this month?",
        "Which agent has the best performance?",
        "Show me the top 5 shops by checkin count",
        "How many unique shops did we visit?",
        "What are the weekly checkin trends?"
    ]
    
    if len(sys.argv) > 1:
        # Use command line argument as question
        question = " ".join(sys.argv[1:])
        demo_question(question)
    else:
        # Run all demo questions
        for i, question in enumerate(demo_questions, 1):
            print(f"\n{'='*60}")
            print(f"DEMO {i}/{len(demo_questions)}")
            print(f"{'='*60}")
            demo_question(question)
            print("\nPress Enter to continue to next question...")
            input()