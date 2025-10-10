#!/usr/bin/env python3
"""
Simple demo to show specific database queries and AI responses
"""

import mysql.connector
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

try:
    from db_config import DATABASE_CONFIG
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def get_monthly_checkins():
    """Get checkins for the current month"""
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        
        # Get current month checkins
        query = """
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as daily_checkins,
            COUNT(DISTINCT agent_id) as active_agents,
            COUNT(DISTINCT shop_id) as unique_shops
        FROM checkins 
        WHERE MONTH(timestamp) = MONTH(CURDATE()) 
        AND YEAR(timestamp) = YEAR(CURDATE())
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
        """
        
        df = pd.read_sql(query, connection)
        
        # Get total for the month
        total_query = """
        SELECT COUNT(*) as total_checkins
        FROM checkins 
        WHERE MONTH(timestamp) = MONTH(CURDATE()) 
        AND YEAR(timestamp) = YEAR(CURDATE())
        """
        
        total_df = pd.read_sql(total_query, connection)
        total_checkins = total_df['total_checkins'].iloc[0]
        
        # Get top agents
        agent_query = """
        SELECT 
            u.name as agent_name,
            COUNT(c.id) as checkin_count
        FROM checkins c
        JOIN users u ON c.agent_id = u.id
        WHERE MONTH(c.timestamp) = MONTH(CURDATE()) 
        AND YEAR(c.timestamp) = YEAR(CURDATE())
        GROUP BY c.agent_id, u.name
        ORDER BY checkin_count DESC
        LIMIT 5
        """
        
        agent_df = pd.read_sql(agent_query, connection)
        
        connection.close()
        
        return {
            "total_monthly_checkins": int(total_checkins),
            "daily_breakdown": df.to_dict('records'),
            "top_agents": agent_df.to_dict('records')
        }
        
    except Exception as e:
        return {"error": str(e)}

def get_agent_performance():
    """Get overall agent performance"""
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        
        query = """
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
        
        df = pd.read_sql(query, connection)
        connection.close()
        
        return df.to_dict('records')
        
    except Exception as e:
        return {"error": str(e)}

def demo_questions():
    """Demo specific questions with direct database queries"""
    
    print("🚀 SalesSync AI Assistant - Direct Database Demo")
    print("=" * 60)
    
    # Question 1: Monthly checkins
    print("\n📊 QUESTION 1: What are the total checkins this month?")
    print("-" * 50)
    
    monthly_data = get_monthly_checkins()
    if "error" not in monthly_data:
        print(f"✅ Total checkins this month: {monthly_data['total_monthly_checkins']}")
        print(f"📅 Daily breakdown available for {len(monthly_data['daily_breakdown'])} days")
        print(f"👥 Top agents this month:")
        for agent in monthly_data['top_agents'][:3]:
            print(f"   • {agent['agent_name']}: {agent['checkin_count']} checkins")
    else:
        print(f"❌ Error: {monthly_data['error']}")
    
    # Question 2: Agent performance
    print("\n📊 QUESTION 2: Which agent has the best performance?")
    print("-" * 50)
    
    agent_data = get_agent_performance()
    if "error" not in agent_data and agent_data:
        top_agent = agent_data[0]
        print(f"🏆 Top performing agent: {top_agent['agent_name']}")
        print(f"   • Total checkins: {top_agent['total_checkins']}")
        print(f"   • Unique shops visited: {top_agent['unique_shops']}")
        print(f"   • Active days: {top_agent['active_days']}")
        print(f"   • Average checkins per day: {top_agent['avg_checkins_per_day']}")
        
        print(f"\n📈 Top 5 agents overall:")
        for i, agent in enumerate(agent_data[:5], 1):
            print(f"   {i}. {agent['agent_name']}: {agent['total_checkins']} checkins")
    else:
        print(f"❌ Error: {agent_data.get('error', 'No data available')}")
    
    # Question 3: Shop data
    print("\n📊 QUESTION 3: Show me the top shops by checkin count")
    print("-" * 50)
    
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        
        shop_query = """
        SELECT 
            s.name as shop_name,
            COUNT(c.id) as checkin_count,
            MAX(c.timestamp) as last_checkin
        FROM checkins c
        JOIN shops s ON c.shop_id = s.id
        GROUP BY c.shop_id, s.name
        ORDER BY checkin_count DESC
        LIMIT 5
        """
        
        shop_df = pd.read_sql(shop_query, connection)
        connection.close()
        
        if not shop_df.empty:
            print("🏪 Top shops by checkin count:")
            for i, shop in shop_df.iterrows():
                print(f"   {i+1}. {shop['shop_name']}: {shop['checkin_count']} checkins")
                print(f"      Last checkin: {shop['last_checkin']}")
        else:
            print("No shop data available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed! The AI system can answer these and many more questions.")
    print("💡 Try running: python3 launch_ai_assistant.py for interactive mode")

if __name__ == "__main__":
    demo_questions()