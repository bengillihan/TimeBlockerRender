#!/bin/bash
# Start the application with optimized PostgreSQL database settings

echo "Starting TimeBlocker with optimized database settings..."
gunicorn --config gunicorn_config.py main:app
