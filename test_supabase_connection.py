#!/usr/bin/env python3
"""
Test Supabase connection with your actual database URL
Run this with: python test_supabase_connection.py
"""

import os
import sys
from sqlalchemy import create_engine, text

def test_connection():
    """Test connection to Supabase database"""
    
    # You'll need to provide your actual password
    database_url = input("Enter your Supabase connection pooling URL: ")
    
    if not database_url:
        print("No DATABASE_URL provided")
        return False
        
    try:
        # Create engine with connection pooling settings
        engine = create_engine(
            database_url,
            pool_size=2,
            max_overflow=1,
            pool_timeout=20,
            pool_recycle=300,
            pool_pre_ping=True
        )
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            print(f"✅ Database connection successful: {result}")
            
            # Check if user exists
            user_result = conn.execute(text("SELECT username, email FROM users WHERE email = 'bdgillihan@gmail.com'")).fetchone()
            if user_result:
                print(f"✅ User found: {user_result[0]} ({user_result[1]})")
            else:
                print("❌ User not found in database")
                
            # Count tables
            tables_result = conn.execute(text("""
                SELECT 'users' as table_name, COUNT(*) as count FROM users
                UNION ALL
                SELECT 'category', COUNT(*) FROM category
                UNION ALL
                SELECT 'task', COUNT(*) FROM task
                UNION ALL
                SELECT 'to_do', COUNT(*) FROM to_do
            """)).fetchall()
            
            print("📊 Database contents:")
            for table, count in tables_result:
                print(f"   {table}: {count} records")
                
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Supabase Connection")
    print("=" * 40)
    test_connection()