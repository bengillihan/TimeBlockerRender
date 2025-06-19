#!/usr/bin/env python3
"""
Data Migration Script for TimeBlocker

This script helps migrate data from your current database to Supabase.
Run this script after setting up your Supabase database with the migration SQL.
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test the database connection before migration"""
    try:
        from app import app, db
        with app.app_context():
            # Test basic connection
            result = db.session.execute("SELECT 1").fetchone()
            if result:
                logger.info("✅ Database connection successful")
                return True
            else:
                logger.error("❌ Database connection failed - no result")
                return False
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

def create_tables():
    """Create all database tables"""
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
            logger.info("✅ Database tables created successfully")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {str(e)}")
        return False

def verify_setup():
    """Verify the database setup is complete"""
    try:
        from app import app, db
        from models import User, Category, DailyPlan
        
        with app.app_context():
            # Check if tables exist by querying them
            user_count = User.query.count()
            category_count = Category.query.count()
            plan_count = DailyPlan.query.count()
            
            logger.info(f"📊 Database Status:")
            logger.info(f"   Users: {user_count}")
            logger.info(f"   Categories: {category_count}")
            logger.info(f"   Daily Plans: {plan_count}")
            
            return True
    except Exception as e:
        logger.error(f"❌ Database verification failed: {str(e)}")
        return False

def main():
    """Main migration function"""
    print("🚀 TimeBlocker Database Migration Tool")
    print("=" * 50)
    
    # Check environment variables
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("Please set your Supabase connection string as DATABASE_URL")
        sys.exit(1)
    
    print(f"📍 Database: {database_url.split('@')[1] if '@' in database_url else 'Unknown'}")
    
    # Step 1: Test connection
    print("\n1️⃣ Testing database connection...")
    if not test_database_connection():
        print("\n💡 SOLUTION:")
        print("1. Verify your Supabase database is running")
        print("2. Check your DATABASE_URL includes the correct password")
        print("3. Ensure your Supabase project allows external connections")
        sys.exit(1)
    
    # Step 2: Create tables
    print("\n2️⃣ Creating database tables...")
    if not create_tables():
        print("\n💡 Run the SQL migration script in your Supabase dashboard:")
        print("   - Go to SQL Editor in Supabase")
        print("   - Copy contents from supabase_migration.sql")
        print("   - Execute the script")
        sys.exit(1)
    
    # Step 3: Verify setup
    print("\n3️⃣ Verifying database setup...")
    if not verify_setup():
        sys.exit(1)
    
    print("\n✅ SUCCESS! Your TimeBlocker database is ready!")
    print("\n🎯 Next Steps:")
    print("1. Your application is now connected to Supabase")
    print("2. Deploy to Render using the provided configuration")
    print("3. Update your Google OAuth redirect URIs")
    print("\n📚 See DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()