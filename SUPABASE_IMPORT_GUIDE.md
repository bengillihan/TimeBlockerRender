# Supabase Database Import Guide

This guide will help you import your TimeBlocker data from Replit to Supabase.

## Prerequisites

1. Supabase project created and accessible
2. Connection pooling URL from Supabase
3. `supabase_import.sql` file (included in this project)

## Import Steps

### Step 1: Access Supabase SQL Editor

1. Go to your Supabase dashboard
2. Navigate to **SQL Editor** in the left sidebar
3. Click **New Query**

### Step 2: Import Database Schema and Data

1. Copy the entire contents of `supabase_import.sql`
2. Paste into the SQL Editor
3. Click **Run** to execute the script

### Step 3: Verify Import

The script includes verification queries at the end. You should see:

```
table_name    | record_count
--------------+-------------
users         | 1
category      | 3
role          | 6
nav_link      | 3
day_template  | 1
task          | 29
to_do         | 18
daily_plan    | 2
```

### Step 4: Test Application Connection

1. Update your `DATABASE_URL` environment variable with the Supabase connection pooling URL:
   ```
   postgresql://postgres.ltrawiqehgfxmtcjoumf:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres?pgbouncer=true
   ```

2. Restart your application

3. Test the health endpoint: `curl http://localhost:5000/health`

## What Gets Imported

### Core Data
- **User Profile**: Your account (Ben, bdgillihan@gmail.com)
- **Categories**: APS, Personal, Church (with colors)
- **Roles**: 6 roles for task organization
- **Tasks**: 29 tasks from your original database
- **To-dos**: 18 important to-do items
- **Navigation Links**: Google Calendar, Notion, Rescue Time
- **Day Template**: Sunday template with time blocks

### Schema Improvements
- **Foreign Key Constraints**: Proper referential integrity
- **Indexes**: Optimized for performance
- **JSONB Support**: Better JSON handling for Supabase
- **Conflict Resolution**: ON CONFLICT clauses for safe re-imports

## Key Schema Changes

1. **Table Name**: `user` → `users` (avoids PostgreSQL reserved word)
2. **Column Names**: `order` → `priority_order`, `link_order` (avoids reserved words)
3. **JSON Fields**: Converted to JSONB for better performance
4. **Cascade Deletes**: Proper cleanup when records are deleted

## Troubleshooting

### Import Errors
- **Permission denied**: Ensure you have admin access to Supabase project
- **Syntax errors**: Copy the entire file without modifications
- **Timeout**: Large imports may take 30-60 seconds

### Connection Issues
- Verify your DATABASE_URL includes the correct password
- Use connection pooling URL (port 6543) for better reliability
- Check Supabase dashboard for connection status

### Data Verification
```sql
-- Check user data
SELECT * FROM users;

-- Check task counts by category
SELECT c.name, COUNT(t.id) as task_count 
FROM category c 
LEFT JOIN task t ON c.id = t.category_id 
GROUP BY c.name;

-- Check recent to-dos
SELECT title, status, due_date 
FROM to_do 
WHERE created_at > '2025-06-01' 
ORDER BY created_at DESC;
```

## Next Steps

After successful import:

1. **Deploy to Render**: Follow `DEPLOYMENT_GUIDE.md`
2. **Update OAuth**: Configure Google OAuth redirect URIs
3. **Test Features**: Verify all functionality works with imported data

## Backup and Recovery

- **Supabase Backups**: Automatic daily backups enabled
- **Export Data**: Use SQL Editor to export specific tables
- **Version Control**: Keep `supabase_import.sql` in your repository

Your data is now safely migrated to a production-ready cloud database with automatic scaling and backups.