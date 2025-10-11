"""
Enhanced AI-Powered Database Q&A System for SalesSync
Uses Llama 3 for intelligent responses with improved context understanding
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
    from enhanced_ai_summarizer import EnhancedAISummarizer
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class EnhancedDatabaseQASystem:
    def __init__(self):
        """Initialize the enhanced database Q&A system with Llama 3"""
        self.db_config = DATABASE_CONFIG
        self.ai_summarizer = None
        self.connection = None
        
        print("Initializing Enhanced Database Q&A System with Llama 3...")
        self._initialize_ai()
        self._connect_database()
    
    def _initialize_ai(self):
        """Initialize the enhanced AI summarizer with Llama 3"""
        try:
            self.ai_summarizer = EnhancedAISummarizer()
            print("✅ Enhanced AI system with Llama 3 initialized successfully!")
        except Exception as e:
            print(f"Warning: Enhanced AI system could not be initialized: {e}")
            print("System will work with basic responses only.")
    
    def _connect_database(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("✅ Database connected successfully!")
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
        Answer user questions using enhanced Llama 3 AI
        
        Args:
            question: User's question about the data
            
        Returns:
            AI-generated answer using Llama 3
        """
        try:
            # First, get relevant data based on the question
            relevant_data = self._extract_relevant_data(question)
            
            # Use enhanced AI to generate answer
            if self.ai_summarizer:
                return self.ai_summarizer.answer_question(question, relevant_data)
            else:
                return self._generate_basic_answer(question, relevant_data)
                
        except Exception as e:
            return f"Error processing question: {str(e)}"
    
    def _extract_relevant_data(self, question: str) -> Dict[str, Any]:
        """Extract relevant data based on the question with enhanced context"""
        question_lower = question.lower()
        relevant_data = {}
        
        # Get database schema first
        schema = self.get_database_schema()
        
        # Enhanced keyword detection for better context
        if any(word in question_lower for word in ['visit', 'visits', 'daily', 'team', 'checkin', 'checkins']):
            relevant_data.update(self._get_visit_data())
        
        if any(word in question_lower for word in ['customer', 'client', 'name', 'shop', 'shops']):
            relevant_data.update(self._get_customer_data())
        
        if any(word in question_lower for word in ['performance', 'top', 'best', 'worst', 'ranking', 'leaderboard']):
            relevant_data.update(self._get_performance_data())
        
        if any(word in question_lower for word in ['trend', 'trends', 'over time', 'pattern', 'weekly', 'monthly']):
            relevant_data.update(self._get_trend_data())
        
        if any(word in question_lower for word in ['today', 'current', 'now', 'recent']):
            relevant_data.update(self._get_today_data())
        
        if any(word in question_lower for word in ['month', 'this month', 'current month']):
            relevant_data.update(self._get_monthly_data())
        
        # Agent-specific queries
        if any(word in question_lower for word in ['agent', 'agents', 'how many agents', 'agent count', 'total agents']):
            relevant_data.update(self._get_agent_data())
        
        # User-specific queries (since agents are users with role='agent')
        if any(word in question_lower for word in ['user', 'users', 'how many users', 'user count', 'total users']):
            relevant_data.update(self._get_user_data())
        
        # If no specific keywords, get general summary
        if not relevant_data:
            relevant_data = self.get_sales_data_summary()
        
        return relevant_data
    
    def _get_visit_data(self) -> Dict[str, Any]:
        """Get visit-related data with enhanced metrics"""
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
                COUNT(DISTINCT DATE(c.timestamp)) as active_days,
                ROUND(COUNT(c.id) / COUNT(DISTINCT DATE(c.timestamp)), 2) as avg_checkins_per_day
            FROM checkins c
            JOIN users u ON c.agent_id = u.id
            GROUP BY c.agent_id, u.name
            ORDER BY total_checkins DESC
            """
            
            agent_data = self.execute_query(agent_query)
            
            return {
                "visit_data": {
                    "daily_summary": daily_data.to_dict('records'),
                    "agent_performance": agent_data.to_dict('records'),
                    "total_checkins": int(daily_data['total_checkins'].sum()) if not daily_data.empty else 0
                }
            }
        except Exception as e:
            return {"visit_data": {"error": str(e)}}
    
    def _get_customer_data(self) -> Dict[str, Any]:
        """Get customer/shop-related data"""
        try:
            # Get shop summary
            shop_query = """
            SELECT 
                s.name as shop_name,
                COUNT(c.id) as checkin_count,
                MAX(c.timestamp) as last_checkin,
                MIN(c.timestamp) as first_checkin,
                DATEDIFF(CURDATE(), MAX(c.timestamp)) as days_since_last_visit
            FROM checkins c
            JOIN shops s ON c.shop_id = s.id
            GROUP BY c.shop_id, s.name
            ORDER BY checkin_count DESC
            LIMIT 20
            """
            
            shop_data = self.execute_query(shop_query)
            
            return {
                "customer_data": {
                    "top_shops": shop_data.to_dict('records'),
                    "total_shops": len(shop_data) if not shop_data.empty else 0
                }
            }
        except Exception as e:
            return {"customer_data": {"error": str(e)}}
    
    def _get_performance_data(self) -> Dict[str, Any]:
        """Get performance-related data with enhanced metrics"""
        try:
            # Get agent performance
            performance_query = """
            SELECT 
                u.name as agent_name,
                COUNT(c.id) as total_checkins,
                COUNT(DISTINCT c.shop_id) as unique_shops,
                COUNT(DISTINCT DATE(c.timestamp)) as active_days,
                ROUND(COUNT(c.id) / COUNT(DISTINCT DATE(c.timestamp)), 2) as avg_checkins_per_day,
                MAX(c.timestamp) as last_activity,
                MIN(c.timestamp) as first_activity
            FROM checkins c
            JOIN users u ON c.agent_id = u.id
            GROUP BY c.agent_id, u.name
            ORDER BY total_checkins DESC
            """
            
            performance_data = self.execute_query(performance_query)
            
            return {
                "performance_data": {
                    "agent_performance": performance_data.to_dict('records'),
                    "top_performer": performance_data.iloc[0].to_dict() if not performance_data.empty else None,
                    "total_agents": len(performance_data) if not performance_data.empty else 0
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
                    "weekly_trends": weekly_data.to_dict('records'),
                    "trend_direction": "increasing" if len(weekly_data) > 1 and weekly_data.iloc[0]['total_checkins'] > weekly_data.iloc[1]['total_checkins'] else "decreasing"
                }
            }
        except Exception as e:
            return {"trend_data": {"error": str(e)}}
    
    def _get_today_data(self) -> Dict[str, Any]:
        """Get today's specific data"""
        try:
            today_query = """
            SELECT 
                COUNT(*) as total_checkins_today,
                COUNT(DISTINCT agent_id) as agents_working_today,
                COUNT(DISTINCT shop_id) as shops_visited_today
            FROM checkins 
            WHERE DATE(timestamp) = CURDATE()
            """
            
            today_data = self.execute_query(today_query)
            
            # Get today's top agents
            today_agents_query = """
            SELECT 
                u.name as agent_name,
                COUNT(c.id) as checkins_today
            FROM checkins c
            JOIN users u ON c.agent_id = u.id
            WHERE DATE(c.timestamp) = CURDATE()
            GROUP BY c.agent_id, u.name
            ORDER BY checkins_today DESC
            LIMIT 5
            """
            
            today_agents = self.execute_query(today_agents_query)
            
            return {
                "today_data": {
                    "summary": today_data.iloc[0].to_dict() if not today_data.empty else {},
                    "top_agents_today": today_agents.to_dict('records') if not today_agents.empty else []
                }
            }
        except Exception as e:
            return {"today_data": {"error": str(e)}}
    
    def _get_monthly_data(self) -> Dict[str, Any]:
        """Get monthly data"""
        try:
            monthly_query = """
            SELECT 
                COUNT(*) as total_checkins_month,
                COUNT(DISTINCT agent_id) as active_agents_month,
                COUNT(DISTINCT shop_id) as unique_shops_month,
                COUNT(DISTINCT DATE(timestamp)) as active_days_month
            FROM checkins 
            WHERE MONTH(timestamp) = MONTH(CURDATE()) 
            AND YEAR(timestamp) = YEAR(CURDATE())
            """
            
            monthly_data = self.execute_query(monthly_query)
            
            return {
                "monthly_data": {
                    "summary": monthly_data.iloc[0].to_dict() if not monthly_data.empty else {},
                    "avg_daily_checkins": monthly_data.iloc[0]['total_checkins_month'] / monthly_data.iloc[0]['active_days_month'] if not monthly_data.empty and monthly_data.iloc[0]['active_days_month'] > 0 else 0
                }
            }
        except Exception as e:
            return {"monthly_data": {"error": str(e)}}
    
    def _get_agent_data(self) -> Dict[str, Any]:
        """Get agent-specific data"""
        try:
            # Count total agents (users with role='agent')
            agent_count_query = """
            SELECT COUNT(*) as total_agents
            FROM users 
            WHERE role = 'agent' AND is_active = 1
            """
            
            agent_count_data = self.execute_query(agent_count_query)
            total_agents = int(agent_count_data['total_agents'].iloc[0]) if not agent_count_data.empty else 0
            
            # Get agent details
            agent_details_query = """
            SELECT 
                u.id,
                u.name,
                u.phone,
                u.created_at,
                COUNT(c.id) as total_checkins,
                MAX(c.timestamp) as last_checkin,
                MIN(c.timestamp) as first_checkin
            FROM users u
            LEFT JOIN checkins c ON u.id = c.agent_id
            WHERE u.role = 'agent' AND u.is_active = 1
            GROUP BY u.id, u.name, u.phone, u.created_at
            ORDER BY total_checkins DESC
            """
            
            agent_details = self.execute_query(agent_details_query)
            
            return {
                "agent_data": {
                    "total_agents": total_agents,
                    "agent_details": agent_details.to_dict('records') if not agent_details.empty else [],
                    "active_agents": len([agent for agent in agent_details.to_dict('records') if agent['total_checkins'] > 0]) if not agent_details.empty else 0
                }
            }
        except Exception as e:
            return {"agent_data": {"error": str(e)}}
    
    def _get_user_data(self) -> Dict[str, Any]:
        """Get user-specific data"""
        try:
            # Count total users by role
            user_count_query = """
            SELECT 
                role,
                COUNT(*) as count
            FROM users 
            WHERE is_active = 1
            GROUP BY role
            """
            
            user_count_data = self.execute_query(user_count_query)
            
            # Get total users
            total_users_query = """
            SELECT COUNT(*) as total_users
            FROM users 
            WHERE is_active = 1
            """
            
            total_users_data = self.execute_query(total_users_query)
            total_users = int(total_users_data['total_users'].iloc[0]) if not total_users_data.empty else 0
            
            # Get user details
            user_details_query = """
            SELECT 
                u.id,
                u.name,
                u.role,
                u.phone,
                u.created_at,
                COUNT(c.id) as total_checkins
            FROM users u
            LEFT JOIN checkins c ON u.id = c.agent_id
            WHERE u.is_active = 1
            GROUP BY u.id, u.name, u.role, u.phone, u.created_at
            ORDER BY u.role, total_checkins DESC
            """
            
            user_details = self.execute_query(user_details_query)
            
            return {
                "user_data": {
                    "total_users": total_users,
                    "users_by_role": user_count_data.to_dict('records') if not user_count_data.empty else [],
                    "user_details": user_details.to_dict('records') if not user_details.empty else []
                }
            }
        except Exception as e:
            return {"user_data": {"error": str(e)}}
    
    def _generate_basic_answer(self, question: str, data: Dict[str, Any]) -> str:
        """Generate basic answer without AI"""
        question_lower = question.lower()
        
        # Enhanced keyword-based responses
        if 'total' in question_lower and ('checkin' in question_lower or 'visit' in question_lower):
            visit_data = data.get('visit_data', {})
            if 'total_checkins' in visit_data:
                return f"Total checkins: {visit_data['total_checkins']}"
        
        if 'agent' in question_lower and 'performance' in question_lower:
            perf_data = data.get('performance_data', {})
            if 'top_performer' in perf_data and perf_data['top_performer']:
                top = perf_data['top_performer']
                return f"Top performing agent: {top['agent_name']} with {top['total_checkins']} checkins"
        
        if 'shop' in question_lower or 'customer' in question_lower:
            customer_data = data.get('customer_data', {})
            if 'top_shops' in customer_data and customer_data['top_shops']:
                top_shop = customer_data['top_shops'][0]
                return f"Top shop: {top_shop['shop_name']} with {top_shop['checkin_count']} checkins"
        
        if 'today' in question_lower:
            today_data = data.get('today_data', {})
            if 'summary' in today_data:
                summary = today_data['summary']
                return f"Today's activity: {summary.get('total_checkins_today', 0)} checkins by {summary.get('agents_working_today', 0)} agents"
        
        # Agent count questions
        if 'agent' in question_lower and ('how many' in question_lower or 'count' in question_lower):
            agent_data = data.get('agent_data', {})
            if 'total_agents' in agent_data:
                total_agents = agent_data['total_agents']
                active_agents = agent_data.get('active_agents', 0)
                return f"You have {total_agents} total agents, with {active_agents} active agents who have made checkins."
        
        # User count questions
        if 'user' in question_lower and ('how many' in question_lower or 'count' in question_lower):
            user_data = data.get('user_data', {})
            if 'total_users' in user_data:
                total_users = user_data['total_users']
                users_by_role = user_data.get('users_by_role', [])
                role_breakdown = ", ".join([f"{role['role']}: {role['count']}" for role in users_by_role])
                return f"You have {total_users} total users ({role_breakdown})."
        
        # Default response
        return f"Based on the available data: {json.dumps(data, indent=2, default=str)}"
    
    def interactive_session(self):
        """Start an interactive Q&A session"""
        print("\n" + "="*60)
        print("🤖 ENHANCED SALESSYNC AI ASSISTANT (Llama 3)")
        print("="*60)
        print("Ask me anything about your sales data!")
        print("Type 'quit', 'exit', or 'bye' to end the session")
        print("Type 'help' for example questions")
        print("="*60)
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! Thanks for using Enhanced SalesSync AI Assistant!")
                    break
                
                if question.lower() == 'help':
                    self._show_help()
                    continue
                
                if not question:
                    print("Please enter a question.")
                    continue
                
                print("\n🔍 Analyzing your data with Llama 3...")
                answer = self.answer_question(question)
                
                print("\n" + "="*50)
                print("📊 AI RESPONSE:")
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
        print("• How many agents have worked today?")
        print("• What's the current month's performance?")
        print("• Show me agent activity by day")
        print("• Which agents are underperforming?")
        print("• What's our daily checkin average?")
        print("• Show me the latest checkin data")
        print("="*50)
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    try:
        qa_system = EnhancedDatabaseQASystem()
        qa_system.interactive_session()
    except Exception as e:
        print(f"Failed to start Enhanced Q&A system: {e}")
    finally:
        if 'qa_system' in locals():
            qa_system.close()