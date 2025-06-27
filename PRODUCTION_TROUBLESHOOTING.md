# Production 502 Error Troubleshooting Guide

## Current Issue
Your TimeBlocker application is experiencing 502 Bad Gateway errors on both:
- Railway deployment: `timeblockerrw-production.up.railway.app`
- Custom domain: `tb.bengillihan.com`

## What 502 Errors Mean
502 errors occur when the reverse proxy (Railway/Cloudflare) cannot reach your application server, usually due to:
1. Application crashes
2. Database connection timeouts
3. Memory/resource constraints on free tier
4. Application startup failures

## Recent Optimizations Applied
- Added Railway-specific database connection pooling (1 connection, no overflow)
- Reduced connection timeouts to 5 seconds for Railway
- Added health check endpoints at `/health` and `/health-check`
- Implemented better error handling for 500/502 errors
- Created Railway startup script with comprehensive diagnostics (`railway_start.py`)
- Added Railway configuration file (`railway.json`) with proper health checks
- Fixed startup logging and error handling for production deployment
- Application now starting successfully in Replit environment (verified)

## Immediate Steps to Resolve

### 1. Check Railway Logs
```bash
railway logs --tail
```
Look for:
- Application startup errors
- Database connection failures
- Memory limit exceeded warnings
- Worker timeout messages

### 2. Verify Environment Variables
Ensure these are set in Railway:
- `DATABASE_URL` (PostgreSQL connection string)
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `SESSION_SECRET`
- `RAILWAY_ENVIRONMENT_NAME` (should be auto-set)

### 3. Database Connection Test
Try connecting to your database directly:
```bash
railway connect
```

### 4. Restart Railway Service
Force restart your Railway deployment:
```bash
railway up --detach
```

## Common Railway Free Tier Issues

### Memory Limits
- Free tier: 512MB RAM limit
- Flask + PostgreSQL can be memory-intensive
- Solution: Optimize database connections (already implemented)

### Connection Limits
- Free PostgreSQL: Limited concurrent connections
- Solution: Use connection pooling (already implemented)

### Startup Time
- Railway has ~30 second startup timeout
- Large applications may timeout during cold starts
- Solution: Optimize startup process

## Health Check Testing
Once deployed, test health endpoints:
```bash
curl https://timeblockerrw-production.up.railway.app/health
curl https://tb.bengillihan.com/health-check
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "nylas_configured": false,
  "timestamp": "2025-06-27T11:40:00-07:00"
}
```

## If Issues Persist

### Option 1: Redeploy from Scratch
1. Delete current Railway service
2. Create new service from GitHub
3. Reconfigure environment variables
4. Test deployment

### Option 2: Switch to Render
Your application is already configured for Render deployment:
- `render.yaml` is ready
- Gunicorn configuration optimized
- Database migrations prepared

### Option 3: Debug Mode Deployment
Temporarily enable debug logging:
1. Set `FLASK_ENV=development` in Railway
2. Check detailed logs for specific errors
3. Revert to production after debugging

## Contact Points
If persistent issues occur:
- Railway Support: For platform-specific issues
- Database Provider: For connection problems
- GitHub Issues: For application bugs

## Files Modified for Production Stability
- `app.py`: Added Railway-specific database optimizations
- `gunicorn_config.py`: Optimized for free tier constraints
- `render.yaml`: Backup deployment configuration
- Health check endpoints: Better monitoring

## Prevention
- Monitor health endpoints regularly
- Keep an eye on Railway usage metrics
- Consider upgrading to paid tier for production workloads