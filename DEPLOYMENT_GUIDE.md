# TimeBlocker Migration to Render + Supabase

This guide will help you migrate your TimeBlocker application from Replit to Render with Supabase as the database.

## Prerequisites

1. A GitHub account with your TimeBlocker code
2. A Render account (free tier available)
3. A Supabase account (free tier available)
4. Google OAuth credentials (for authentication)

## Step 1: Set up Supabase Database

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - Name: `timeblocker-db`
   - Database Password: Generate a strong password
   - Region: Choose closest to your users
5. Click "Create new project"

### 1.2 Set up Database Schema

1. In your Supabase dashboard, go to the SQL Editor
2. Copy the contents of `supabase_migration.sql`
3. Paste and run the SQL script
4. This will create all necessary tables and indexes

### 1.3 Get Database Connection String

1. Go to Settings → Database
2. Copy the connection string (URI format)
3. Save this for later use in Render

## Step 2: Update Google OAuth Configuration

### 2.1 Update OAuth Redirect URIs

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to your project → APIs & Services → Credentials
3. Edit your OAuth 2.0 Client ID
4. Add your Render domain to authorized redirect URIs:
   - `https://your-app-name.onrender.com/google_login/callback`
   - Replace `your-app-name` with your actual Render app name

## Step 3: Deploy to Render

### 3.1 Connect GitHub Repository

1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select your TimeBlocker repository

### 3.2 Configure Web Service

1. **Name**: `timeblocker` (or your preferred name)
2. **Environment**: `Python 3`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --preload main:app`

### 3.3 Set Environment Variables

Add these environment variables in Render:

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql://postgres:[password]@[host]:5432/postgres` | Your Supabase connection string |
| `SESSION_SECRET` | `[generate-a-secure-random-string]` | Secret key for sessions |
| `GOOGLE_OAUTH_CLIENT_ID` | `[your-google-client-id]` | Google OAuth client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | `[your-google-client-secret]` | Google OAuth client secret |
| `FLASK_ENV` | `production` | Environment setting |
| `FLASK_DEBUG` | `false` | Debug mode setting |

### 3.4 Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Wait for the build to complete (usually 2-5 minutes)

## Step 4: Test Your Deployment

### 4.1 Verify Application

1. Visit your Render URL (e.g., `https://timeblocker.onrender.com`)
2. Test Google OAuth login
3. Verify all features work correctly

### 4.2 Check Database Connection

1. Create a test user account
2. Add some test data
3. Verify data is saved in Supabase dashboard

## Key Migration Benefits

✓ **Supabase Database**: Managed PostgreSQL with automatic backups
✓ **Render Hosting**: Automatic HTTPS and custom domains
✓ **Production Ready**: Optimized for performance and scaling
✓ **Modern Architecture**: Clean separation of concerns
✓ **Easy Maintenance**: Simple deployment and monitoring

## Production Configuration

Your application is now configured with:
- Gunicorn WSGI server with 2 workers
- PostgreSQL connection pooling
- Environment-based configuration
- Automatic HTTPS via Render
- Session management with 8-hour lifetime

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Verify all dependencies are listed in pyproject.toml
   - Check that DATABASE_URL is correctly formatted

2. **Database Connection Issues**
   - Verify Supabase connection string is correct
   - Check that all required tables exist

3. **OAuth Issues**
   - Verify redirect URIs include your Render domain
   - Check Google OAuth credentials are valid

## Support Resources

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Supabase Documentation**: [supabase.com/docs](https://supabase.com/docs)
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com)

Your application is now ready for production deployment with enterprise-grade infrastructure!