"""
Configuration file for SalesSync AI Assistant
"""

# AI Model Configuration
AI_CONFIG = {
    # Primary model (larger, better quality)
    "primary_model": "meta-llama/Llama-3.1-8B-Instruct",
    
    # Fallback model (smaller, faster)
    "fallback_model": "microsoft/DialoGPT-medium",
    
    # Model settings
    "max_tokens": 512,
    "temperature": 0.7,
    "use_quantization": True,
    
    # Memory settings
    "max_memory_usage": "8GB",
    "device": "auto"  # auto, cuda, cpu
}

# Database Query Configuration
QUERY_CONFIG = {
    # Default limits for queries
    "max_records": 1000,
    "default_limit": 100,
    
    # Time ranges
    "default_days_back": 30,
    "max_days_back": 365,
    
    # Performance settings
    "query_timeout": 30,  # seconds
    "enable_caching": True
}

# Response Configuration
RESPONSE_CONFIG = {
    # Response formatting
    "include_timestamps": True,
    "include_data_sources": True,
    "max_response_length": 2000,
    
    # Output format
    "format": "markdown",  # markdown, plain, json
    
    # Interactive settings
    "show_processing_time": True,
    "show_data_summary": True
}

# Example Questions Database
EXAMPLE_QUESTIONS = [
    "What are the total visits this month?",
    "Which team lead has the best performance?",
    "Show me the top 10 customers by visit count",
    "What are the weekly visit trends?",
    "How many unique customers did we visit?",
    "Which team members are most active?",
    "What's the average visits per day?",
    "Show me customer visit patterns",
    "What's our team performance summary?",
    "How many visits did we have last week?",
    "Which customers haven't been visited recently?",
    "What's the conversion rate for our visits?",
    "Show me the busiest days of the week",
    "Which team lead has the most repeat customers?",
    "What's our customer retention rate?"
]

# Database Table Mappings
TABLE_MAPPINGS = {
    "visits": {
        "primary_key": "visit_id",
        "date_column": "visit_date",
        "team_column": "team_lead",
        "customer_column": "customer_id"
    },
    "customers": {
        "primary_key": "customer_id",
        "name_column": "customer_name",
        "contact_column": "contact_info"
    },
    "team_leads": {
        "primary_key": "team_lead_id",
        "name_column": "team_lead_name",
        "region_column": "region"
    }
}

# Common SQL Patterns
SQL_PATTERNS = {
    "daily_visits": """
        SELECT 
            DATE(visit_date) as date,
            COUNT(*) as total_visits,
            COUNT(DISTINCT team_lead) as active_team_leads,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM visits 
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        GROUP BY DATE(visit_date)
        ORDER BY date DESC
    """,
    
    "team_performance": """
        SELECT 
            team_lead,
            COUNT(*) as total_visits,
            COUNT(DISTINCT customer_id) as unique_customers,
            COUNT(DISTINCT DATE(visit_date)) as active_days,
            ROUND(COUNT(*) / COUNT(DISTINCT DATE(visit_date)), 2) as avg_visits_per_day
        FROM visits 
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        GROUP BY team_lead
        ORDER BY total_visits DESC
    """,
    
    "customer_summary": """
        SELECT 
            customer_name,
            COUNT(*) as visit_count,
            MAX(visit_date) as last_visit,
            MIN(visit_date) as first_visit,
            DATEDIFF(CURDATE(), MAX(visit_date)) as days_since_last_visit
        FROM visits 
        WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        GROUP BY customer_id, customer_name
        ORDER BY visit_count DESC
    """
}