"""
AI-Powered Database Q&A System for SalesSync
Integrates with salessync database to answer questions using AI
"""

import mysql.connector
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

try:
    from db_config import DATABASE_CONFIG
    from ai_summarizer import AISummarizer
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class DatabaseQASystem:
    def __init__(self):
        """Initialize the database Q&A system"""
        self.db_config = DATABASE_CONFIG
        self.ai_summarizer = None
        self.connection = None
        
        print("Initializing Database Q&A System...")
        self._initialize_ai()
        self._connect_database()
    
    def _initialize_ai(self):
        """Initialize the AI summarizer"""
        try:
            self.ai_summarizer = AISummarizer()
            print("AI system initialized successfully!")
        except Exception as e:
            print(f"Warning: AI system could not be initialized: {e}")
            print("System will work with basic responses only.")
    
    def _connect_database(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("Database connected successfully!")
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise
    
    def get_database_schema(self) -> Dict[str, List[str]]:
        """Get database schema information"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            schema = {}
            for table in tables:
                cursor.execute(f"DESCRIBE {table}")
                columns = [col[0] for col in cursor.fetchall()]
                schema[table] = columns
            
            cursor.close()
            return schema
        except Exception as e:
            print(f"Error getting schema: {e}")
            return {}
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        try:
            df = pd.read_sql(query, self.connection)
            return df
        except Exception as e:
            print(f"Query execution error: {e}")
            return pd.DataFrame()
    
    def get_sales_data_summary(self) -> Dict[str, Any]:
        """Get comprehensive sales data summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "tables": self.get_database_schema(),
            "data_summary": {}
        }
        
        # Get basic counts for each table
        for table in summary["tables"].keys():
            try:
                count_query = f"SELECT COUNT(*) as count FROM {table}"
                result = self.execute_query(count_query)
                summary["data_summary"][table] = {
                    "total_records": int(result['count'].iloc[0]) if not result.empty else 0
                }
            except Exception as e:
                summary["data_summary"][table] = {"error": str(e)}
        
        return summary
    
    def answer_question(self, question: str) -> str:
        """
        Answer user questions based on database data
        
        Args:
            question: User's question about the data
            
        Returns:
            AI-generated answer based on database data
        """
        try:
            # First, get relevant data based on the question
            relevant_data = self._extract_relevant_data(question)
            
            # If AI is available, use it to generate answer
            if self.ai_summarizer:
                return self._generate_ai_answer(question, relevant_data)
            else:
                return self._generate_basic_answer(question, relevant_data)
                
        except Exception as e:
            return f"Error processing question: {str(e)}"
    
    def _extract_relevant_data(self, question: str) -> Dict[str, Any]:
        """Extract relevant data based on the question"""
        question_lower = question.lower()
        relevant_data = {}
        
        # Get database schema first
        schema = self.get_database_schema()
        
        # Determine what data to fetch based on question keywords
        if any(word in question_lower for word in ['visit', 'visits', 'daily', 'team']):
            relevant_data.update(self._get_visit_data())
        
        if any(word in question_lower for word in ['customer', 'client', 'name']):
            relevant_data.update(self._get_customer_data())
        
        if any(word in question_lower for word in ['performance', 'top', 'best', 'worst']):
            relevant_data.update(self._get_performance_data())
        
        if any(word in question_lower for word in ['trend', 'trends', 'over time', 'pattern']):
            relevant_data.update(self._get_trend_data())
        
        # If no specific keywords, get general summary
        if not relevant_data:
            relevant_data = self.get_sales_data_summary()
        
        return relevant_data
    
    def _get_visit_data(self) -> Dict[str, Any]:
        """Get visit-related data"""
        try:
            # Get daily checkin summary
            daily_query = """
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_checkins,
                COUNT(DISTINCT agent_id) as active_agents,
                COUNT(DISTINCT shop_id) as unique_shops
            FROM checkins 
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
            """
            
            daily_data = self.execute_query(daily_query)
            
            # Get agent performance
            agent_query = """
            SELECT 
                u.name as agent_name,
                COUNT(c.id) as total_checkins,
                COUNT(DISTINCT c.shop_id) as unique_shops,
                AVG(TIMESTAMPDIFF(MINUTE, c.timestamp, c.timestamp)) as avg_duration
            FROM checkins c
            JOIN users u ON c.agent_id = u.id
            GROUP BY c.agent_id, u.name
            ORDER BY total_checkins DESC
            """
            
            agent_data = self.execute_query(agent_query)
            
            return {
                "visit_data": {
                    "daily_summary": daily_data.to_dict('records'),
                    "agent_performance": agent_data.to_dict('records')
                }
            }
        except Exception as e:
            return {"visit_data": {"error": str(e)}}
    
    def _get_customer_data(self) -> Dict[str, Any]:
        """Get customer-related data"""
        try:
            # Get shop summary
            shop_query = """
            SELECT 
                s.name as shop_name,
                COUNT(c.id) as checkin_count,
                MAX(c.timestamp) as last_checkin,
                MIN(c.timestamp) as first_checkin
            FROM checkins c
            JOIN shops s ON c.shop_id = s.id
            GROUP BY c.shop_id, s.name
            ORDER BY checkin_count DESC
            LIMIT 20
            """
            
            shop_data = self.execute_query(shop_query)
            
            return {
                "customer_data": {
                    "top_shops": shop_data.to_dict('records')
                }
            }
        except Exception as e:
            return {"customer_data": {"error": str(e)}}
    
    def _get_performance_data(self) -> Dict[str, Any]:
        """Get performance-related data"""
        try:
            # Get agent performance
            performance_query = """
            SELECT 
                u.name as agent_name,
                COUNT(c.id) as total_checkins,
                COUNT(DISTINCT c.shop_id) as unique_shops,
                COUNT(DISTINCT DATE(c.timestamp)) as active_days,
                ROUND(COUNT(c.id) / COUNT(DISTINCT DATE(c.timestamp)), 2) as avg_checkins_per_day
            FROM checkins c
            JOIN users u ON c.agent_id = u.id
            GROUP BY c.agent_id, u.name
            ORDER BY total_checkins DESC
            """
            
            performance_data = self.execute_query(performance_query)
            
            return {
                "performance_data": {
                    "agent_performance": performance_data.to_dict('records')
                }
            }
        except Exception as e:
            return {"performance_data": {"error": str(e)}}
    
    def _get_trend_data(self) -> Dict[str, Any]:
        """Get trend-related data"""
        try:
            # Get weekly trends
            weekly_query = """
            SELECT 
                YEARWEEK(timestamp) as week,
                COUNT(*) as total_checkins,
                COUNT(DISTINCT agent_id) as active_agents,
                COUNT(DISTINCT shop_id) as unique_shops
            FROM checkins 
            GROUP BY YEARWEEK(timestamp)
            ORDER BY week DESC
            LIMIT 12
            """
            
            weekly_data = self.execute_query(weekly_query)
            
            return {
                "trend_data": {
                    "weekly_trends": weekly_data.to_dict('records')
                }
            }
        except Exception as e:
            return {"trend_data": {"error": str(e)}}
    
    def _generate_ai_answer(self, question: str, data: Dict[str, Any]) -> str:
        """Generate AI-powered answer"""
        try:
            # Create a prompt for the AI
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a business intelligence assistant for a sales team. Answer questions about sales data in a clear, professional manner. Use the provided data to give specific, actionable insights.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Question: {question}

Data Context: {json.dumps(data, indent=2, default=str)}

Please provide a comprehensive answer based on the data. Include specific numbers, trends, and actionable insights where possible.

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Answer:

"""
            
            response = self.ai_summarizer.pipeline(
                prompt,
                max_new_tokens=400,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.ai_summarizer.tokenizer.eos_token_id
            )
            
            answer = response[0]['generated_text'].replace(prompt, "").strip()
            return answer
            
        except Exception as e:
            return self._generate_basic_answer(question, data)
    
    def _generate_basic_answer(self, question: str, data: Dict[str, Any]) -> str:
        """Generate basic answer without AI"""
        question_lower = question.lower()
        
        # Simple keyword-based responses
        if 'total' in question_lower and ('checkin' in question_lower or 'visit' in question_lower):
            visit_data = data.get('visit_data', {})
            if 'daily_summary' in visit_data:
                total_checkins = sum(day['total_checkins'] for day in visit_data['daily_summary'])
                return f"Total checkins: {total_checkins}"
        
        if 'agent' in question_lower and 'performance' in question_lower:
            perf_data = data.get('performance_data', {})
            if 'agent_performance' in perf_data:
                agents = perf_data['agent_performance']
                if agents:
                    top_agent = agents[0]
                    return f"Top performing agent: {top_agent['agent_name']} with {top_agent['total_checkins']} checkins"
        
        if 'shop' in question_lower or 'customer' in question_lower:
            customer_data = data.get('customer_data', {})
            if 'top_shops' in customer_data:
                shops = customer_data['top_shops']
                if shops:
                    top_shop = shops[0]
                    return f"Top shop: {top_shop['shop_name']} with {top_shop['checkin_count']} checkins"
        
        # Default response
        return f"Based on the available data, here's what I found:\n{json.dumps(data, indent=2, default=str)}"
    
    def interactive_session(self):
        """Start an interactive Q&A session"""
        print("\n" + "="*60)
        print("🤖 SALESSYNC AI ASSISTANT")
        print("="*60)
        print("Ask me anything about your sales data!")
        print("Type 'quit', 'exit', or 'bye' to end the session")
        print("Type 'help' for example questions")
        print("="*60)
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! Thanks for using SalesSync AI Assistant!")
                    break
                
                if question.lower() == 'help':
                    self._show_help()
                    continue
                
                if not question:
                    print("Please enter a question.")
                    continue
                
                print("\n🔍 Analyzing your data...")
                answer = self.answer_question(question)
                
                print("\n" + "="*50)
                print("📊 ANSWER:")
                print("="*50)
                print(answer)
                print("="*50)
                
            except KeyboardInterrupt:
                print("\n\n👋 Session ended. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def _show_help(self):
        """Show example questions"""
        print("\n" + "="*50)
        print("📚 EXAMPLE QUESTIONS:")
        print("="*50)
        print("• What are the total checkins this month?")
        print("• Which agent has the best performance?")
        print("• Show me the top 10 shops by checkin count")
        print("• What are the weekly checkin trends?")
        print("• How many unique shops did we visit?")
        print("• Which agents are most active?")
        print("• What's the average checkins per day?")
        print("• Show me shop visit patterns")
        print("• What's our agent performance summary?")
        print("• How many checkins did we have last week?")
        print("• Which shops haven't been visited recently?")
        print("• Show me the busiest days of the week")
        print("• Which agent has the most repeat shop visits?")
        print("• What's our shop retention rate?")
        print("="*50)
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    try:
        qa_system = DatabaseQASystem()
        qa_system.interactive_session()
    except Exception as e:
        print(f"Failed to start Q&A system: {e}")
    finally:
        if 'qa_system' in locals():
            qa_system.close()