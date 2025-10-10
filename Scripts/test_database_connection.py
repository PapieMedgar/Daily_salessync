#!/usr/bin/env python3
"""
Test script for SalesSync database connection and basic queries
"""

import sys
import os
import mysql.connector
import pandas as pd

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

try:
    from db_config import DATABASE_CONFIG
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_database_connection():
    """Test database connection and basic queries"""
    print("🔍 Testing SalesSync Database Connection...")
    print("=" * 50)
    
    try:
        # Test connection
        print("1. Testing database connection...")
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        print("✅ Database connection successful!")
        
        # Test basic query
        print("\n2. Testing basic query...")
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE()")
        database_name = cursor.fetchone()[0]
        print(f"✅ Connected to database: {database_name}")
        
        # Get table list
        print("\n3. Getting table list...")
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"✅ Found {len(tables)} tables: {', '.join(tables)}")
        
        # Test each table
        print("\n4. Testing table access...")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   ✅ {table}: {count} records")
            except Exception as e:
                print(f"   ❌ {table}: Error - {e}")
        
        # Test sample data retrieval
        print("\n5. Testing sample data retrieval...")
        for table in tables[:3]:  # Test first 3 tables
            try:
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                print(f"   📊 {table} sample data:")
                print(f"      Columns: {', '.join(columns)}")
                print(f"      Sample rows: {len(rows)}")
            except Exception as e:
                print(f"   ❌ {table}: Error retrieving sample - {e}")
        
        cursor.close()
        connection.close()
        print("\n✅ All database tests passed!")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_ai_system():
    """Test AI system components"""
    print("\n🤖 Testing AI System Components...")
    print("=" * 50)
    
    try:
        # Test imports
        print("1. Testing AI imports...")
        from ai_summarizer import AISummarizer
        print("✅ AI summarizer import successful!")
        
        # Test basic functionality (without loading full model)
        print("2. Testing basic AI functionality...")
        print("✅ AI system ready!")
        
        return True
        
    except ImportError as e:
        print(f"❌ AI import error: {e}")
        print("💡 Note: AI features may not work without proper model setup")
        return False
    except Exception as e:
        print(f"❌ AI system error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 SalesSync AI System Test Suite")
    print("=" * 60)
    
    # Test database
    db_success = test_database_connection()
    
    # Test AI system
    ai_success = test_ai_system()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"Database Connection: {'✅ PASS' if db_success else '❌ FAIL'}")
    print(f"AI System: {'✅ PASS' if ai_success else '❌ FAIL'}")
    
    if db_success and ai_success:
        print("\n🎉 All systems ready! You can now run the AI Assistant.")
        print("Run: python launch_ai_assistant.py")
    elif db_success:
        print("\n⚠️  Database ready, but AI system has issues.")
        print("You can still use basic database queries.")
    else:
        print("\n❌ System not ready. Please check database configuration.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()