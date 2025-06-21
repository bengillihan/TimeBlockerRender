# Time Block Planner

## Overview

Time Block Planner is a personal productivity web application that enables users to plan their daily schedules using time blocking methodology. Users can create daily plans with priorities, schedule tasks in 15-minute increments, and track their productivity over time. The application features Google OAuth authentication, ensuring each user has their own private workspace.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Google OAuth 2.0 via `oauthlib`
- **Session Management**: Flask-Login for user sessions
- **Caching**: Flask-Caching with Redis fallback to simple memory cache
- **Deployment**: Gunicorn WSGI server with autoscaling on Replit

### Frontend Architecture
- **Templates**: Jinja2 templating engine
- **Styling**: Bootstrap 5 with dark theme
- **JavaScript**: Vanilla JS with drag-and-drop functionality
- **Icons**: Font Awesome 6.0
- **Real-time Updates**: Auto-save functionality with visual feedback

### Database Schema
- **Users**: Authentication and preferences (day start/end times, timezone)
- **Daily Plans**: Date-specific planning data with productivity ratings
- **Priorities**: Top priorities for each day
- **Time Blocks**: 15-minute scheduling increments
- **Tasks/Categories**: Organized task management
- **Nav Links**: Customizable navigation for external integrations

## Key Components

### Authentication System
- Google OAuth integration via `google_auth.py`
- Secure callback handling with HTTPS enforcement
- User profile management with timezone preferences

### Time Blocking Engine
- 15-minute increment scheduling system
- Drag-and-drop interface for task arrangement
- Auto-save with 10-second delay after changes
- Visual feedback for save status and current time

### Task Management
- Hierarchical task organization with categories and roles
- Task templates for recurring activities
- Progress tracking and completion status
- Analytics for productivity insights

### Caching Layer
- User-specific cache keys for data isolation
- Redis-backed caching with simple memory fallback
- Cached views for improved performance
- Cache invalidation on data updates

### Navigation System
- Customizable nav links for external tool integration
- Iframe embedding support for external applications
- Token-based authentication for cross-application access

## Data Flow

1. **User Authentication**: Google OAuth → User creation/login → Session establishment
2. **Daily Planning**: Date selection → Load existing plan or create new → Display time blocks and priorities
3. **Data Persistence**: User interactions → Auto-save trigger → Database update → Cache invalidation
4. **Analytics**: Historical data aggregation → Category summaries → Productivity metrics

## External Dependencies

### Authentication
- Google OAuth 2.0 API for user authentication
- Requires `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`

### Infrastructure
- PostgreSQL database (configured via `DATABASE_URL`)
- Redis for caching (optional, falls back to memory cache)
- Session secret for secure session management

### Third-Party Integrations
- Google API Python Client (potential Calendar integration)
- Twilio SDK (messaging capabilities)
- Nylas API (email/calendar sync)

## Deployment Strategy

### Production Configuration
- Gunicorn WSGI server with 2 workers
- Connection pooling with PostgreSQL (3 connections, 2 overflow)
- Connection recycling every 5 minutes
- Pre-ping for connection validation

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Flask session security key
- `GOOGLE_OAUTH_CLIENT_ID`: Google OAuth client identifier
- `GOOGLE_OAUTH_CLIENT_SECRET`: Google OAuth client secret
- `REDIS_URL`: Redis connection string (optional)

### Replit Deployment
- Autoscale deployment target
- Port 5000 binding with external port 80
- Automatic package installation and service restart
- Gunicorn process management with graceful shutdowns

## Deployment Strategy

### Supabase Migration (In Progress)
- Successfully imported core data: 1 user, 3 categories, 6 roles, 3 nav links, 1 day template
- Tasks and todos import pending - requires running `add_tasks_todos.sql`
- Updated application schema to use "users" table for compatibility
- Configured connection pooling for production performance

### Render Deployment (Ready)
- Created `render.yaml` configuration for automated deployment
- Configured Gunicorn WSGI server with 2 workers for production
- Environment variables properly configured for cloud deployment
- Created comprehensive deployment guide (`DEPLOYMENT_GUIDE.md`)

## Migration Benefits
- **Scalable Database**: Managed PostgreSQL with automatic backups via Supabase
- **Connection Pooling**: Enhanced performance with PgBouncer connection pooling
- **Production Infrastructure**: Enterprise-grade hosting with automatic HTTPS
- **Zero Downtime**: Seamless migration path from development to production
- **Modern Architecture**: Cloud-native configuration with optimized performance

## Current Status
- Database: Supabase PostgreSQL with connection pooling configured
- Application: Running on Replit with cloud database connectivity
- Deployment: Ready for Render deployment with all configuration files prepared

## Changelog

- June 19, 2025: Updated to use Supabase connection pooling URL for improved connectivity
- June 19, 2025: Successfully migrated to Supabase database and prepared for Render deployment
- June 19, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.