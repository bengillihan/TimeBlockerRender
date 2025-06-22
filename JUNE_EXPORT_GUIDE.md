# Step-by-Step: Export June 2025 Data from Replit to Supabase

## Overview
This guide helps you transfer your June 2025 time blocking data from your Replit development database to your production Supabase database.

## Step 1: Check Current June Data in Supabase
Your Supabase database currently has minimal June data:
- June 19: 1 daily plan (productivity rating 4)
- June 20: 1 daily plan (no rating)
- No priorities or time blocks for June

## Step 2: Export from Replit Database

Run these commands in the Replit SQL tool to generate export SQL:

### Export Daily Plans
```sql
SELECT 
    'INSERT INTO daily_plan (id, date, user_id, productivity_rating, brain_dump, created_at, updated_at) VALUES' as sql_start
UNION ALL
SELECT 
    '(' || id || ', ''' || date || ''', ' || user_id || ', ' || 
    COALESCE(productivity_rating::text, 'NULL') || ', ' ||
    CASE WHEN brain_dump IS NULL THEN 'NULL' 
         ELSE '''' || REPLACE(brain_dump, '''', '''''') || '''' END || ', ' ||
    '''' || created_at || ''', ''' || updated_at || ''')' ||
    CASE WHEN ROW_NUMBER() OVER (ORDER BY date) = COUNT(*) OVER () 
         THEN ' ON CONFLICT (id) DO UPDATE SET productivity_rating = EXCLUDED.productivity_rating, brain_dump = EXCLUDED.brain_dump, updated_at = EXCLUDED.updated_at;' ELSE ',' END
FROM daily_plan 
WHERE user_id = 1 AND date >= '2025-06-01' AND date < '2025-07-01'
ORDER BY CASE WHEN sql_start IS NOT NULL THEN 0 ELSE 1 END, date;
```

### Export Priorities
```sql
SELECT 
    'INSERT INTO priority (id, daily_plan_id, content, "order", completed, created_at) VALUES'
UNION ALL
SELECT 
    '(' || p.id || ', ' || p.daily_plan_id || ', ''' || 
    REPLACE(p.content, '''', '''''') || ''', ' || 
    p."order" || ', ' || p.completed || ', ''' || 
    COALESCE(p.created_at::text, NOW()::text) || ''')' ||
    CASE WHEN ROW_NUMBER() OVER (ORDER BY p.daily_plan_id) = COUNT(*) OVER () 
         THEN ' ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, completed = EXCLUDED.completed;' 
         ELSE ',' END
FROM priority p
JOIN daily_plan dp ON p.daily_plan_id = dp.id
WHERE dp.user_id = 1 AND dp.date >= '2025-06-01' AND dp.date < '2025-07-01'
ORDER BY CASE WHEN sql_start IS NOT NULL THEN 0 ELSE 1 END, p.daily_plan_id;
```

### Export Time Blocks
```sql
SELECT 
    'INSERT INTO time_block (id, daily_plan_id, start_time, end_time, completed, task_id, notes, created_at) VALUES'
UNION ALL
SELECT 
    '(' || tb.id || ', ' || tb.daily_plan_id || ', ''' || tb.start_time || ''', ''' || 
    tb.end_time || ''', ' || tb.completed || ', ' || 
    COALESCE(tb.task_id::text, 'NULL') || ', ' ||
    CASE WHEN tb.notes IS NULL THEN 'NULL' 
         ELSE '''' || REPLACE(tb.notes, '''', '''''') || '''' END || ', ''' ||
    COALESCE(tb.created_at::text, NOW()::text) || ''')' ||
    CASE WHEN ROW_NUMBER() OVER (ORDER BY tb.daily_plan_id) = COUNT(*) OVER () 
         THEN ' ON CONFLICT (id) DO UPDATE SET completed = EXCLUDED.completed, notes = EXCLUDED.notes;' 
         ELSE ',' END
FROM time_block tb
JOIN daily_plan dp ON tb.daily_plan_id = dp.id
WHERE dp.user_id = 1 AND dp.date >= '2025-06-01' AND dp.date < '2025-07-01'
ORDER BY CASE WHEN sql_start IS NOT NULL THEN 0 ELSE 1 END, tb.daily_plan_id;
```

## Step 3: Execute in Supabase

1. Copy the generated SQL output from each query above
2. Open your Supabase SQL Editor 
3. Paste and execute each SQL statement
4. Verify the import with:

```sql
SELECT 
    dp.date,
    COUNT(DISTINCT p.id) as priorities,
    COUNT(DISTINCT tb.id) as time_blocks,
    dp.productivity_rating
FROM daily_plan dp
LEFT JOIN priority p ON dp.id = p.daily_plan_id  
LEFT JOIN time_block tb ON dp.id = tb.daily_plan_id
WHERE dp.user_id = 1 AND dp.date >= '2025-06-01' AND dp.date < '2025-07-01'
GROUP BY dp.id, dp.date, dp.productivity_rating
ORDER BY dp.date;
```

## Step 4: Verify on Production

After import, check your TimeBlocker at https://timeblocker.onrender.com to see your June data restored.

## Alternative: Direct Database Export

If you have shell access to your Replit database file:

```bash
# Export specific June data
sqlite3 timeblock_dev.db << EOF
.mode insert daily_plan
.output june_daily_plans.sql
SELECT * FROM daily_plan WHERE user_id = 1 AND date >= '2025-06-01' AND date < '2025-07-01';
.quit
EOF
```

Then convert the SQLite INSERT statements to PostgreSQL format for Supabase.