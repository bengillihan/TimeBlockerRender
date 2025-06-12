#!/bin/bash
# Start the application with simplified gunicorn settings

echo "Starting TimeBlocker..."
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 --preload main:app
