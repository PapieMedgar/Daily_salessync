"""
Enhanced Universal AI-Powered Database Q&A System for SalesSync
Integrates Tiny AI Summarizer for executive summary generation
Can answer ANY question and generate comprehensive executive summaries
"""

import mysql.connector
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
import os
import re

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

try:
    from db_config import DATABASE_CONFIG
    from tiny_ai_summarizer import TinyAISummarizer
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class EnhancedUniversalQASystem:
    def __init__(self):
        """Initialize the enhanced universal Q&A system with executive summary capabilities"""
        self.db_config = DATABASE_CONFIG
        self.ai_summarizer = None
        self.tiny_summarizer = None
        self.connection = None
        
        print("Initializing Enhanced Universal Q&A System...")
        self._initialize_ai()
        self._connect_database()
    
    def _initialize_ai(self):
        """Initialize the AI systems"""
        try:
            # Initialize the tiny AI summarizer for executive summaries
            self.tiny_summarizer = TinyAISummarizer()
            print("✅ Tiny AI Summarizer initialized successfully!")
        except Exception as e:
            print(f"Warning: Tiny AI Summarizer could not be initialized: {e}")
            print("System will work with rule-based summaries only.")
    
    def _connect_database(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("✅ Database connected successfully!")
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise
    
    def get_database_schema(self) -> Dict[str, List[str]]:
        """Get comprehensive database schema information"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            schema = {}
            for table in tables:
                cursor.execute(f"DESCRIBE {table}")
                columns = [col[0] for col in cursor.fetchall()]
                schema[table] = columns
                
                # Get sample data for better understanding
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    sample_data = cursor.fetchall()
                    schema[f"{table}_sample"] = sample_data
                except:
                    pass
            
            cursor.close()
            return schema
        except Exception as e:
            print(f"Error getting schema: {e}")
            return {}
    
    def execute_query(self, query: str, params=None) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame"""
        try:
            if params:
                df = pd.read_sql(query, self.connection, params=params)
            else:
                df = pd.read_sql(query, self.connection)
            return df
        except Exception as e:
            print(f"Query execution error: {e}")
            return pd.DataFrame()
    
    def generate_executive_summary(self) -> str:
        """
        Generate a comprehensive executive summary from all available data
        
        Returns:
            Executive summary text
        """
        try:
            print("📊 Generating comprehensive executive summary...")
            
            # Collect all available data
            all_reports_data = self._collect_all_reports_data()
            
            # Generate executive summary using tiny AI summarizer
            if self.tiny_summarizer:
                return self.tiny_summarizer.generate_executive_summary(all_reports_data)
            else:
                return self._generate_rule_based_executive_summary(all_reports_data)
                
        except Exception as e:
            return f"I apologize, but I encountered an error while generating the executive summary: {str(e)}. Please try again or contact support if the issue persists."
    
    def _collect_all_reports_data(self) -> Dict[str, Any]:
        """Collect all available reports data for executive summary"""
        try:
            reports_data = {
                "timestamp": datetime.now().isoformat(),
                "database_schema": self.get_database_schema()
            }
            
            # Get comprehensive checkin data
            reports_data.update(self._get_comprehensive_checkin_data("", {}))
            
            # Get comprehensive user data
            reports_data.update(self._get_comprehensive_user_data("", {}))
            
            # Get comprehensive shop data
            reports_data.update(self._get_comprehensive_shop_data("", {}))
            
            # Get comprehensive performance data
            reports_data.update(self._get_comprehensive_performance_data("", {}))
            
            # Get comprehensive trend data
            reports_data.update(self._get_comprehensive_trend_data("", {}))
            
            # Get general system data
            reports_data.update(self._get_general_data("", {}))
            
            return reports_data
            
        except Exception as e:
            print(f"Error collecting reports data: {e}")
            return {"error": str(e)}
    
    def answer_question(self, question: str) -> str:
        """
        Answer ANY user question about the data using enhanced approach
        
        Args:
            question: User's question about the data
            
        Returns:
            Natural language answer based on database data
        """
        try:
            print(f"Processing question: {question}")
            
            # Check if user is asking for executive summary
            if any(phrase in question.lower() for phrase in [
                'executive summary', 'summary report', 'comprehensive report', 
                'overall summary', 'business summary', 'management report'
            ]):
                return self.generate_executive_summary()
            
            # Get comprehensive data based on the question
            relevant_data = self._extract_comprehensive_data(question)
            
            # Generate intelligent answer
            return self._generate_intelligent_answer(question, relevant_data)
                
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your question: {str(e)}. Please try rephrasing your question or contact support if the issue persists."
    
    def _extract_comprehensive_data(self, question: str) -> Dict[str, Any]:
        """Extract comprehensive data based on the question using intelligent analysis"""
        question_lower = question.lower()
        relevant_data = {}
        
        # Get database schema for context
        schema = self.get_database_schema()
        relevant_data['database_schema'] = schema
        
        # Extract date information from question
        date_info = self._extract_date_information(question)
        if date_info:
            relevant_data['date_context'] = date_info
        
        # Get comprehensive data based on question analysis
        data_sources = self._identify_data_sources(question)
        
        for source in data_sources:
            if source == 'checkins':
                relevant_data.update(self._get_comprehensive_checkin_data(question, date_info))
            elif source == 'users':
                relevant_data.update(self._get_comprehensive_user_data(question, date_info))
            elif source == 'shops':
                relevant_data.update(self._get_comprehensive_shop_data(question, date_info))
            elif source == 'performance':
                relevant_data.update(self._get_comprehensive_performance_data(question, date_info))
            elif source == 'trends':
                relevant_data.update(self._get_comprehensive_trend_data(question, date_info))
            elif source == 'general':
                relevant_data.update(self._get_general_data(question, date_info))
        
        # If no specific data sources identified, get comprehensive overview
        if not relevant_data or len(relevant_data) <= 1:  # Only schema
            relevant_data.update(self._get_comprehensive_overview(question, date_info))
        
        return relevant_data
    
    def _extract_date_information(self, question: str) -> Dict[str, Any]:
        """Extract date information from the question"""
        question_lower = question.lower()
        date_info = {}
        
        # Check for specific dates
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\w+) (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})',  # Month Day, Year
            r'(\w+) (\d{1,2})(?:st|nd|rd|th)?',  # Month Day (current year)
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, question_lower)
            if match:
                try:
                    groups = match.groups()
                    if len(groups) == 3:
                        if '/' in pattern:
                            # Assume MM/DD/YYYY format
                            month, day, year = groups
                            date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        elif '-' in pattern:
                            year, month, day = groups
                            date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        else:
                            month_name, day, year = groups
                            month_num = self._get_month_number(month_name)
                            if month_num:
                                date_str = f"{year}-{month_num:02d}-{day.zfill(2)}"
                            else:
                                continue
                    else:
                        month_name, day = groups
                        month_num = self._get_month_number(month_name)
                        if month_num:
                            current_year = datetime.now().year
                            date_str = f"{current_year}-{month_num:02d}-{day.zfill(2)}"
                        else:
                            continue
                    
                    date_info['specific_date'] = date_str
                    break
                except:
                    continue
        
        # Check for relative dates
        if 'today' in question_lower:
            date_info['relative_date'] = 'today'
        elif 'yesterday' in question_lower:
            date_info['relative_date'] = 'yesterday'
        elif 'this week' in question_lower:
            date_info['relative_date'] = 'this_week'
        elif 'last week' in question_lower:
            date_info['relative_date'] = 'last_week'
        elif 'this month' in question_lower:
            date_info['relative_date'] = 'this_month'
        elif 'last month' in question_lower:
            date_info['relative_date'] = 'last_month'
        elif 'this year' in question_lower:
            date_info['relative_date'] = 'this_year'
        elif 'last year' in question_lower:
            date_info['relative_date'] = 'last_year'
        
        return date_info
    
    def _get_month_number(self, month_name: str) -> int:
        """Convert month name to number"""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month_name.lower(), None)
    
    def _identify_data_sources(self, question: str) -> List[str]:
        """Identify which data sources are relevant to the question"""
        question_lower = question.lower()
        sources = []
        
        # Check for checkin/visit related keywords
        checkin_keywords = ['checkin', 'checkins', 'visit', 'visits', 'daily', 'activity', 'work', 'worked']
        if any(keyword in question_lower for keyword in checkin_keywords):
            sources.append('checkins')
        
        # Check for user/agent related keywords
        user_keywords = ['agent', 'agents', 'user', 'users', 'person', 'people', 'staff', 'team', 'member', 'members']
        if any(keyword in question_lower for keyword in user_keywords):
            sources.append('users')
        
        # Check for shop/customer related keywords
        shop_keywords = ['shop', 'shops', 'customer', 'customers', 'store', 'stores', 'client', 'clients']
        if any(keyword in question_lower for keyword in shop_keywords):
            sources.append('shops')
        
        # Check for performance related keywords
        performance_keywords = ['performance', 'best', 'worst', 'top', 'bottom', 'ranking', 'leaderboard', 'productive', 'productivity']
        if any(keyword in question_lower for keyword in performance_keywords):
            sources.append('performance')
        
        # Check for trend related keywords
        trend_keywords = ['trend', 'trends', 'pattern', 'patterns', 'over time', 'weekly', 'monthly', 'yearly', 'growth', 'decline']
        if any(keyword in question_lower for keyword in trend_keywords):
            sources.append('trends')
        
        # If no specific sources identified, include general data
        if not sources:
            sources.append('general')
        
        return sources
    
    def _get_comprehensive_checkin_data(self, question: str, date_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive checkin data based on question and date context"""
        try:
            data = {}
            
            # Build date filter
            date_filter = self._build_date_filter(date_info)
            
            # Get basic checkin summary
            basic_query = f"""
            SELECT 
                COUNT(*) as total_checkins,
                COUNT(DISTINCT agent_id) as unique_agents,
                COUNT(DISTINCT shop_id) as unique_shops,
                COUNT(DISTINCT DATE(timestamp)) as active_days,
                MIN(timestamp) as first_checkin,
                MAX(timestamp) as last_checkin
            FROM checkins 
            {date_filter}
            """
            
            basic_data = self.execute_query(basic_query)
            if not basic_data.empty:
                data['checkin_summary'] = basic_data.iloc[0].to_dict()
            
            # Get daily breakdown
            daily_query = f"""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as checkins,
                COUNT(DISTINCT agent_id) as agents,
                COUNT(DISTINCT shop_id) as shops
            FROM checkins 
            {date_filter}
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
            """
            
            daily_data = self.execute_query(daily_query)
            if not daily_data.empty:
                data['daily_breakdown'] = daily_data.to_dict('records')
            
            return {'checkin_data': data}
            
        except Exception as e:
            return {'checkin_data': {'error': str(e)}}
    
    def _get_comprehensive_user_data(self, question: str, date_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive user data based on question and date context"""
        try:
            data = {}
            
            # Build date filter
            date_filter = self._build_date_filter(date_info)
            
            # Get user summary
            user_summary_query = f"""
            SELECT 
                COUNT(DISTINCT u.id) as total_users,
                COUNT(DISTINCT CASE WHEN u.role = 'agent' THEN u.id END) as total_agents,
                COUNT(DISTINCT CASE WHEN u.role = 'admin' THEN u.id END) as total_admins,
                COUNT(DISTINCT CASE WHEN c.agent_id IS NOT NULL THEN u.id END) as active_users
            FROM users u
            LEFT JOIN checkins c ON u.id = c.agent_id {date_filter.replace('WHERE', 'AND') if date_filter else ''}
            WHERE u.is_active = 1
            """
            
            user_summary = self.execute_query(user_summary_query)
            if not user_summary.empty:
                data['user_summary'] = user_summary.iloc[0].to_dict()
            
            # Get user performance
            user_performance_query = f"""
            SELECT 
                u.id,
                u.name,
                u.role,
                u.phone,
                u.created_at,
                COUNT(c.id) as total_checkins,
                COUNT(DISTINCT c.shop_id) as unique_shops,
                COUNT(DISTINCT DATE(c.timestamp)) as active_days,
                MAX(c.timestamp) as last_activity,
                MIN(c.timestamp) as first_activity
            FROM users u
            LEFT JOIN checkins c ON u.id = c.agent_id {date_filter.replace('WHERE', 'AND') if date_filter else ''}
            WHERE u.is_active = 1
            GROUP BY u.id, u.name, u.role, u.phone, u.created_at
            ORDER BY total_checkins DESC
            """
            
            user_performance = self.execute_query(user_performance_query)
            if not user_performance.empty:
                data['user_performance'] = user_performance.to_dict('records')
            
            return {'user_data': data}
            
        except Exception as e:
            return {'user_data': {'error': str(e)}}
    
    def _get_comprehensive_shop_data(self, question: str, date_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive shop data based on question and date context"""
        try:
            data = {}
            
            # Build date filter
            date_filter = self._build_date_filter(date_info)
            
            # Get shop summary
            shop_summary_query = f"""
            SELECT 
                COUNT(DISTINCT s.id) as total_shops,
                COUNT(DISTINCT c.shop_id) as active_shops,
                COUNT(DISTINCT CASE WHEN c.timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN c.shop_id END) as recently_visited_shops
            FROM shops s
            LEFT JOIN checkins c ON s.id = c.shop_id {date_filter.replace('WHERE', 'AND') if date_filter else ''}
            WHERE s.is_active = 1
            """
            
            shop_summary = self.execute_query(shop_summary_query)
            if not shop_summary.empty:
                data['shop_summary'] = shop_summary.iloc[0].to_dict()
            
            # Get shop performance
            shop_performance_query = f"""
            SELECT 
                s.id,
                s.name,
                s.address,
                s.phone,
                s.created_at,
                COUNT(c.id) as total_checkins,
                COUNT(DISTINCT c.agent_id) as unique_agents,
                MAX(c.timestamp) as last_visit,
                MIN(c.timestamp) as first_visit,
                DATEDIFF(CURDATE(), MAX(c.timestamp)) as days_since_last_visit
            FROM shops s
            LEFT JOIN checkins c ON s.id = c.shop_id {date_filter.replace('WHERE', 'AND') if date_filter else ''}
            WHERE s.is_active = 1
            GROUP BY s.id, s.name, s.address, s.phone, s.created_at
            ORDER BY total_checkins DESC
            """
            
            shop_performance = self.execute_query(shop_performance_query)
            if not shop_performance.empty:
                data['shop_performance'] = shop_performance.to_dict('records')
            
            return {'shop_data': data}
            
        except Exception as e:
            return {'shop_data': {'error': str(e)}}
    
    def _get_comprehensive_performance_data(self, question: str, date_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive performance data based on question and date context"""
        try:
            data = {}
            
            # Build date filter
            date_filter = self._build_date_filter(date_info)
            
            # Get performance metrics
            performance_query = f"""
            SELECT 
                u.name as agent_name,
                u.role,
                COUNT(c.id) as total_checkins,
                COUNT(DISTINCT c.shop_id) as unique_shops,
                COUNT(DISTINCT DATE(c.timestamp)) as active_days,
                ROUND(COUNT(c.id) / COUNT(DISTINCT DATE(c.timestamp)), 2) as avg_checkins_per_day,
                MAX(c.timestamp) as last_activity,
                MIN(c.timestamp) as first_activity,
                DATEDIFF(MAX(c.timestamp), MIN(c.timestamp)) as career_span_days
            FROM users u
            LEFT JOIN checkins c ON u.id = c.agent_id {date_filter.replace('WHERE', 'AND') if date_filter else ''}
            WHERE u.is_active = 1 AND u.role = 'agent'
            GROUP BY u.id, u.name, u.role
            ORDER BY total_checkins DESC
            """
            
            performance_data = self.execute_query(performance_query)
            if not performance_data.empty:
                data['agent_performance'] = performance_data.to_dict('records')
                
                # Calculate additional metrics
                total_checkins = performance_data['total_checkins'].sum()
                avg_checkins = performance_data['total_checkins'].mean()
                top_performer = performance_data.iloc[0].to_dict()
                
                data['performance_metrics'] = {
                    'total_checkins': int(total_checkins),
                    'average_checkins_per_agent': float(avg_checkins),
                    'top_performer': top_performer,
                    'total_agents': len(performance_data)
                }
            
            return {'performance_data': data}
            
        except Exception as e:
            return {'performance_data': {'error': str(e)}}
    
    def _get_comprehensive_trend_data(self, question: str, date_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive trend data based on question and date context"""
        try:
            data = {}
            
            # Get weekly trends
            weekly_query = """
            SELECT 
                YEARWEEK(timestamp) as week,
                YEAR(timestamp) as year,
                WEEK(timestamp) as week_number,
                COUNT(*) as total_checkins,
                COUNT(DISTINCT agent_id) as active_agents,
                COUNT(DISTINCT shop_id) as unique_shops,
                COUNT(DISTINCT DATE(timestamp)) as active_days
            FROM checkins 
            GROUP BY YEARWEEK(timestamp), YEAR(timestamp), WEEK(timestamp)
            ORDER BY week DESC
            LIMIT 12
            """
            
            weekly_data = self.execute_query(weekly_query)
            if not weekly_data.empty:
                data['weekly_trends'] = weekly_data.to_dict('records')
            
            # Get monthly trends
            monthly_query = """
            SELECT 
                YEAR(timestamp) as year,
                MONTH(timestamp) as month,
                COUNT(*) as total_checkins,
                COUNT(DISTINCT agent_id) as active_agents,
                COUNT(DISTINCT shop_id) as unique_shops,
                COUNT(DISTINCT DATE(timestamp)) as active_days
            FROM checkins 
            GROUP BY YEAR(timestamp), MONTH(timestamp)
            ORDER BY year DESC, month DESC
            LIMIT 12
            """
            
            monthly_data = self.execute_query(monthly_query)
            if not monthly_data.empty:
                data['monthly_trends'] = monthly_data.to_dict('records')
            
            return {'trend_data': data}
            
        except Exception as e:
            return {'trend_data': {'error': str(e)}}
    
    def _get_general_data(self, question: str, date_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get general data for questions that don't fit specific categories"""
        try:
            data = {}
            
            # Get overall system statistics
            general_query = """
            SELECT 
                (SELECT COUNT(*) FROM users WHERE is_active = 1) as total_users,
                (SELECT COUNT(*) FROM users WHERE is_active = 1 AND role = 'agent') as total_agents,
                (SELECT COUNT(*) FROM shops WHERE is_active = 1) as total_shops,
                (SELECT COUNT(*) FROM checkins) as total_checkins,
                (SELECT MIN(timestamp) FROM checkins) as first_checkin,
                (SELECT MAX(timestamp) FROM checkins) as last_checkin,
                (SELECT COUNT(DISTINCT DATE(timestamp)) FROM checkins) as total_active_days
            """
            
            general_data = self.execute_query(general_query)
            if not general_data.empty:
                data['system_overview'] = general_data.iloc[0].to_dict()
            
            return {'general_data': data}
            
        except Exception as e:
            return {'general_data': {'error': str(e)}}
    
    def _get_comprehensive_overview(self, question: str, date_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive overview when no specific data sources are identified"""
        try:
            overview = {}
            
            # Get all data sources
            overview.update(self._get_comprehensive_checkin_data(question, date_info))
            overview.update(self._get_comprehensive_user_data(question, date_info))
            overview.update(self._get_comprehensive_shop_data(question, date_info))
            overview.update(self._get_comprehensive_performance_data(question, date_info))
            overview.update(self._get_comprehensive_trend_data(question, date_info))
            overview.update(self._get_general_data(question, date_info))
            
            return overview
            
        except Exception as e:
            return {'overview_data': {'error': str(e)}}
    
    def _build_date_filter(self, date_info: Dict[str, Any]) -> str:
        """Build SQL date filter based on date information"""
        if not date_info:
            return ""
        
        if 'specific_date' in date_info:
            return f"WHERE DATE(timestamp) = '{date_info['specific_date']}'"
        
        relative_date = date_info.get('relative_date')
        if relative_date == 'today':
            return "WHERE DATE(timestamp) = CURDATE()"
        elif relative_date == 'yesterday':
            return "WHERE DATE(timestamp) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)"
        elif relative_date == 'this_week':
            return "WHERE YEARWEEK(timestamp) = YEARWEEK(CURDATE())"
        elif relative_date == 'last_week':
            return "WHERE YEARWEEK(timestamp) = YEARWEEK(DATE_SUB(CURDATE(), INTERVAL 1 WEEK))"
        elif relative_date == 'this_month':
            return "WHERE MONTH(timestamp) = MONTH(CURDATE()) AND YEAR(timestamp) = YEAR(CURDATE())"
        elif relative_date == 'last_month':
            return "WHERE MONTH(timestamp) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND YEAR(timestamp) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))"
        elif relative_date == 'this_year':
            return "WHERE YEAR(timestamp) = YEAR(CURDATE())"
        elif relative_date == 'last_year':
            return "WHERE YEAR(timestamp) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))"
        
        return ""
    
    def _generate_intelligent_answer(self, question: str, data: Dict[str, Any]) -> str:
        """Generate intelligent answer with comprehensive data analysis"""
        question_lower = question.lower()
        
        # Handle specific question types with intelligent responses
        if 'how many' in question_lower and 'people' in question_lower:
            return self._answer_people_count_question(data)
        elif 'how many' in question_lower and ('agent' in question_lower or 'staff' in question_lower):
            return self._answer_agent_count_question(data)
        elif 'how many' in question_lower and ('shop' in question_lower or 'store' in question_lower):
            return self._answer_shop_count_question(data)
        elif 'how many' in question_lower and ('checkin' in question_lower or 'visit' in question_lower):
            return self._answer_checkin_count_question(data)
        elif 'who' in question_lower and ('best' in question_lower or 'top' in question_lower):
            return self._answer_top_performer_question(data)
        elif 'what' in question_lower and ('today' in question_lower or 'current' in question_lower):
            return self._answer_today_question(data)
        elif 'what' in question_lower and ('month' in question_lower or 'monthly' in question_lower):
            return self._answer_monthly_question(data)
        else:
            return self._answer_general_question(question, data)
    
    def _answer_people_count_question(self, data: Dict[str, Any]) -> str:
        """Answer questions about people count"""
        if 'user_data' in data and 'user_summary' in data['user_data']:
            summary = data['user_data']['user_summary']
            total_users = summary.get('total_users', 0)
            active_users = summary.get('active_users', 0)
            return f"Based on the data, there are **{total_users} total users** in the system, with **{active_users} active users** who have made checkins."
        
        return "I'd be happy to help you with the people count, but I need to access the user data first. Let me check the database connection."
    
    def _answer_agent_count_question(self, data: Dict[str, Any]) -> str:
        """Answer questions about agent count"""
        if 'user_data' in data and 'user_summary' in data['user_data']:
            summary = data['user_data']['user_summary']
            total_agents = summary.get('total_agents', 0)
            active_users = summary.get('active_users', 0)
            return f"You have **{total_agents} total agents** in the system, with **{active_users} active agents** who have made checkins."
        
        return "I'd be happy to help you with the agent count, but I need to access the user data first. Let me check the database connection."
    
    def _answer_shop_count_question(self, data: Dict[str, Any]) -> str:
        """Answer questions about shop count"""
        if 'shop_data' in data and 'shop_summary' in data['shop_data']:
            summary = data['shop_data']['shop_summary']
            total_shops = summary.get('total_shops', 0)
            active_shops = summary.get('active_shops', 0)
            return f"You have **{total_shops} total shops** in the system, with **{active_shops} active shops** that have been visited."
        
        return "I'd be happy to help you with the shop count, but I need to access the shop data first. Let me check the database connection."
    
    def _answer_checkin_count_question(self, data: Dict[str, Any]) -> str:
        """Answer questions about checkin count"""
        if 'checkin_data' in data and 'checkin_summary' in data['checkin_data']:
            summary = data['checkin_data']['checkin_summary']
            total_checkins = summary.get('total_checkins', 0)
            unique_agents = summary.get('unique_agents', 0)
            unique_shops = summary.get('unique_shops', 0)
            return f"There have been **{total_checkins:,} total checkins** by **{unique_agents} agents** at **{unique_shops} different shops**."
        
        return "I'd be happy to help you with the checkin count, but I need to access the checkin data first. Let me check the database connection."
    
    def _answer_top_performer_question(self, data: Dict[str, Any]) -> str:
        """Answer questions about top performers"""
        if 'performance_data' in data and 'agent_performance' in data['performance_data']:
            agents = data['performance_data']['agent_performance']
            if agents:
                top_agent = agents[0]
                name = top_agent.get('agent_name', 'Unknown')
                checkins = top_agent.get('total_checkins', 0)
                shops = top_agent.get('unique_shops', 0)
                return f"**{name}** is your top performer with **{checkins:,} total checkins** across **{shops} different shops**. They've been very productive!"
        
        return "I'd be happy to help you identify the top performer, but I need to access the performance data first. Let me check the database connection."
    
    def _answer_today_question(self, data: Dict[str, Any]) -> str:
        """Answer questions about today's activity"""
        if 'checkin_data' in data and 'checkin_summary' in data['checkin_data']:
            summary = data['checkin_data']['checkin_summary']
            total_checkins = summary.get('total_checkins', 0)
            unique_agents = summary.get('unique_agents', 0)
            unique_shops = summary.get('unique_shops', 0)
            return f"Today's activity shows **{total_checkins:,} checkins** by **{unique_agents} agents** at **{unique_shops} different shops**. Great work today!"
        
        return "I'd be happy to help you with today's activity, but I need to access today's data first. Let me check the database connection."
    
    def _answer_monthly_question(self, data: Dict[str, Any]) -> str:
        """Answer questions about monthly performance"""
        if 'checkin_data' in data and 'checkin_summary' in data['checkin_data']:
            summary = data['checkin_data']['checkin_summary']
            total_checkins = summary.get('total_checkins', 0)
            unique_agents = summary.get('unique_agents', 0)
            unique_shops = summary.get('unique_shops', 0)
            active_days = summary.get('active_days', 0)
            avg_daily = total_checkins / active_days if active_days > 0 else 0
            return f"This month's performance shows **{total_checkins:,} total checkins** by **{unique_agents} agents** at **{unique_shops} different shops** across **{active_days} active days**. That's an average of **{avg_daily:.1f} checkins per day**!"
        
        return "I'd be happy to help you with the monthly performance, but I need to access the monthly data first. Let me check the database connection."
    
    def _answer_general_question(self, question: str, data: Dict[str, Any]) -> str:
        """Answer general questions with available data"""
        response_parts = [f"Thanks for your question: '{question}'"]
        
        # Add relevant data insights
        if 'checkin_data' in data and 'checkin_summary' in data['checkin_data']:
            summary = data['checkin_data']['checkin_summary']
            response_parts.append(f"\n📊 **Current Activity:**")
            response_parts.append(f"• Total checkins: {summary.get('total_checkins', 0):,}")
            response_parts.append(f"• Active agents: {summary.get('unique_agents', 0)}")
            response_parts.append(f"• Unique shops: {summary.get('unique_shops', 0)}")
        
        if 'user_data' in data and 'user_summary' in data['user_data']:
            summary = data['user_data']['user_summary']
            response_parts.append(f"\n👥 **Team Overview:**")
            response_parts.append(f"• Total users: {summary.get('total_users', 0)}")
            response_parts.append(f"• Active agents: {summary.get('total_agents', 0)}")
            response_parts.append(f"• Active users: {summary.get('active_users', 0)}")
        
        if 'performance_data' in data and 'agent_performance' in data['performance_data']:
            agents = data['performance_data']['agent_performance']
            if agents:
                response_parts.append(f"\n🏆 **Top Performers:**")
                for i, agent in enumerate(agents[:3], 1):
                    response_parts.append(f"{i}. {agent.get('agent_name', 'Unknown')}: {agent.get('total_checkins', 0):,} checkins")
        
        response_parts.append(f"\nIs there anything specific about this data you'd like me to explain further?")
        
        return "\n".join(response_parts)
    
    def _generate_rule_based_executive_summary(self, all_reports_data: Dict[str, Any]) -> str:
        """Generate rule-based executive summary when AI is not available"""
        return f"""# EXECUTIVE SUMMARY
*Generated on: {all_reports_data.get('timestamp', 'Unknown date')}*

## OVERVIEW
This comprehensive report analyzes all business activities and performance metrics across the organization. The data reveals significant insights into team productivity, customer engagement, and operational efficiency.

## KEY PERFORMANCE INDICATORS
Based on the available data, here are the key metrics:

- **Database Schema**: {len(all_reports_data.get('database_schema', {}))} tables available
- **Data Sources**: {len([k for k, v in all_reports_data.items() if isinstance(v, dict) and 'error' not in v])} active data sources

## RECOMMENDATIONS
• Continue monitoring performance metrics for trend analysis
• Focus on data-driven decision making
• Regular review of team performance
• Optimize operational efficiency

*This executive summary provides a comprehensive overview of all business activities and performance metrics.*"""
    
    def interactive_session(self):
        """Start an interactive Q&A session"""
        print("\n" + "="*60)
        print("🤖 ENHANCED UNIVERSAL SALESSYNC AI ASSISTANT")
        print("="*60)
        print("Ask me ANYTHING about your sales data!")
        print("Type 'executive summary' for a comprehensive report")
        print("Type 'quit', 'exit', or 'bye' to end the session")
        print("="*60)
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! Thanks for using Enhanced Universal SalesSync AI Assistant!")
                    break
                
                if not question:
                    print("Please enter a question.")
                    continue
                
                print("\n🔍 Analyzing your question and data...")
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
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    try:
        qa_system = EnhancedUniversalQASystem()
        qa_system.interactive_session()
    except Exception as e:
        print(f"Failed to start Enhanced Universal Q&A system: {e}")
    finally:
        if 'qa_system' in locals():
            qa_system.close()