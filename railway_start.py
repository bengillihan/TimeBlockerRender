#!/usr/bin/env python3
"""
Railway startup script with comprehensive error handling and diagnostics
"""
import os
import sys
import logging
import traceback
from datetime import datetime

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check required environment variables"""
    logger.info("=== Railway Startup Diagnostics ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    required_vars = [
        'DATABASE_URL',
        'GOOGLE_OAUTH_CLIENT_ID', 
        'GOOGLE_OAUTH_CLIENT_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Show first 20 chars for security
            logger.info(f"✓ {var}: {value[:20]}...")
        else:
            logger.error(f"✗ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("✓ All required environment variables are set")
    return True

def test_database_connection():
    """Test database connectivity"""
    try:
        logger.info("Testing database connection...")
        import psycopg2
        
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL not found")
            return False
            
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        
        # Extract connection components for psycopg2
        import re
        match = re.match(r'postgresql\+psycopg2://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', database_url)
        if not match:
            logger.error("Invalid DATABASE_URL format")
            return False
        
        user, password, host, port, dbname = match.groups()
        
        conn = psycopg2.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=dbname,
            connect_timeout=10
        )
        
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        
        conn.close()
        logger.info("✓ Database connection successful")
        return True
        
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        return False

def start_application():
    """Start the Flask application with error handling"""
    try:
        logger.info("Starting Flask application...")
        
        # Import and start the app
        from app import app
        
        # Get port from Railway
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        logger.info(f"Starting server on {host}:{port}")
        
        # Start with basic Gunicorn settings for Railway
        import subprocess
        cmd = [
            'gunicorn',
            '--bind', f'{host}:{port}',
            '--workers', '1',  # Single worker for Railway free tier
            '--timeout', '60',
            '--preload',
            '--log-level', 'info',
            '--access-logfile', '-',
            '--error-logfile', '-',
            'app:app'
        ]
        
        logger.info(f"Executing: {' '.join(cmd)}")
        os.execvp('gunicorn', cmd)
        
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def main():
    """Main startup function"""
    try:
        logger.info(f"=== TimeBlocker Railway Startup - {datetime.now()} ===")
        
        # Check environment
        if not check_environment():
            logger.error("Environment check failed")
            sys.exit(1)
        
        # Test database connection
        if not test_database_connection():
            logger.error("Database connection test failed")
            sys.exit(1)
        
        logger.info("All checks passed, starting application...")
        start_application()
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    main()