# Fix Missing Tasks and Todos in Supabase

## Issue
Your Supabase import was successful for basic data (users, categories, roles, etc.) but tasks and todos didn't get imported properly.

## Solution
Run the additional import script `add_tasks_todos.sql` in your Supabase SQL Editor.

## Steps to Fix

### 1. Access Supabase SQL Editor
1. Go to your Supabase dashboard
2. Click **SQL Editor** in the sidebar
3. Create a **New Query**

### 2. Import Missing Data
1. Copy the entire contents of `add_tasks_todos.sql`
2. Paste into the SQL Editor
3. Click **Run**

### 3. Verify Import
After running, you should see:
```
table_name    | record_count
--------------+-------------
tasks         | 29
to_do         | 18
task_pending  | 29 (all your tasks)
todo_active   | 12 (active todos)
```

## What Gets Added

### Tasks (29 items)
- Bible Study, Exercise, Shower, Lunch
- Work tasks: Replit APS, Sage, Email, IT Support, PowerBI
- APS tasks: Meetings, Process Improvement, QuickBase, CPE
- Personal: Driving Kids, Yard Work, Other Personal Items
- Church: LifeGroup Work, Elder Work, Drive to/From Church

### Todos (18 items)
- Work todos: SSO Entra with QuickBase, Setup PC transfer, EPM Report
- Development: Sales by market PowerBI, Service New Orders Box
- Personal: LinkedIn posts, Bible study materials, Tozer/Drucker books
- Church: Budget presentations, agendas, communion prep

## Verification Queries
Run these in Supabase to confirm data:

```sql
-- Check task counts by category
SELECT c.name, COUNT(t.id) as task_count 
FROM category c 
LEFT JOIN task t ON c.id = t.category_id 
GROUP BY c.name;

-- Check active todos
SELECT title, status, due_date 
FROM to_do 
WHERE completed = false 
ORDER BY due_date;
```

After running this fix, your TimeBlocker application will have all your original tasks and todos available in the cloud database.