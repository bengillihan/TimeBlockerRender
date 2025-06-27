#!/usr/bin/env python3
"""
Simple Railway startup script - fallback approach
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Railway expects port 5000 based on networking configuration
        port = 5000
        logger.info(f"Starting on Railway assigned port {port}")
        
        # Import and run Flask app directly
        from app import app
        
        # Use Gunicorn for production deployment on Railway
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
        
        logger.info(f"Starting Gunicorn with command: {' '.join(cmd)}")
        subprocess.run(cmd)
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()