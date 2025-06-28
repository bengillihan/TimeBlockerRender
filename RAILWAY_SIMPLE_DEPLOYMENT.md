# Simplified Railway Deployment Guide

## Configuration Summary

Your Railway deployment has been simplified to use Railway's standard approach. Here's what you have:

### Key Files
- **Procfile**: Single line with optimized Gunicorn configuration
- **railway.json**: Health check and restart policy configuration
- **main.py**: Simple Flask app startup with dynamic port handling
- **requirements.txt**: All Python dependencies

### Procfile Configuration
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 60 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100 --preload --log-level info --access-logfile - --error-logfile - app:app
```

### Railway.json Configuration
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "deploy": {
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

## Required Environment Variables
Set these in your Railway dashboard:
- `DATABASE_URL` - Your Supabase PostgreSQL connection string
- `GOOGLE_OAUTH_CLIENT_ID` - Your Google OAuth client ID
- `GOOGLE_OAUTH_CLIENT_SECRET` - Your Google OAuth client secret
- `SESSION_SECRET` - Flask session security key

## Deployment Steps
1. Commit and push these changes to your repository
2. Railway will automatically detect the Python app and use the Procfile
3. Railway will assign a dynamic port via the `$PORT` environment variable
4. Your app will start with a single Gunicorn worker optimized for free tier

## Health Check
Your app has a health endpoint at `/health` that Railway will monitor automatically.

## What Was Removed
- Complex startup scripts (railway_startup.py, railway_start.py, start_simple.py)
- Render-specific configuration files
- Nixpacks.toml overrides that were causing conflicts

The simplified setup should eliminate the 502 Bad Gateway errors you were experiencing.