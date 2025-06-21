#!/usr/bin/env python3
"""
Update DATABASE_URL for Supabase testing
"""

import os
import subprocess

# Get your Supabase password
password = input("Enter your Supabase database password: ")

if password:
    # Create the full connection URL
    database_url = f"postgresql://postgres.ltrawiqehgfxmtcjoumf:{password}@aws-0-us-west-1.pooler.supabase.com:6543/postgres?pgbouncer=true"
    
    # Export the environment variable
    os.environ['DATABASE_URL'] = database_url
    
    print("Database URL updated. Restarting application...")
    
    # Test the connection
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT username, email FROM users WHERE email = 'bdgillihan@gmail.com'")).fetchone()
            if result:
                print(f"Success! User found: {result[0]} ({result[1]})")
                print("Your Supabase database is ready for testing.")
            else:
                print("Connection successful but user not found.")
    except Exception as e:
        print(f"Connection test failed: {e}")
else:
    print("No password provided.")