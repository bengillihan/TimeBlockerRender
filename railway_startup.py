#!/usr/bin/env python3
"""
Railway startup script - uses dynamic port assignment
"""
import os
import sys
import logging

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Railway assigns port dynamically via PORT environment variable
        port = os.environ.get('PORT')
        if not port:
            logger.error("PORT environment variable not set by Railway")
            sys.exit(1)
            
        logger.info(f"Starting TimeBlocker on Railway port {port}")
        
        # Import Flask app
        from app import app
        
        # Start with Gunicorn for production
        import subprocess
        cmd = [
            'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '2',
            '--timeout', '120',
            '--keep-alive', '2',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--worker-class', 'sync',
            '--log-level', 'info',
            '--access-logfile', '-',
            '--error-logfile', '-',
            'main:app'
        ]
        
        logger.info(f"Executing: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except Exception as e:
        logger.error(f"Railway startup failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == '__main__':
    main()