-- Time Block Planner Database Import for Supabase
-- Modified from Replit export for Supabase compatibility
-- Generated on 2025-06-19

-- Note: Using "users" instead of "user" to avoid PostgreSQL reserved word issues

-- Create tables (schema) - Modified for Supabase
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    selected_calendars TEXT,
    nylas_access_token TEXT,
    day_start_time TIME DEFAULT '07:00:00',
    day_end_time TIME DEFAULT '16:30:00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    day_split_time TIME DEFAULT '12:00:00'
);

CREATE TABLE IF NOT EXISTS category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    color VARCHAR(7) DEFAULT '#6c757d',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#6c757d',
    description TEXT,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS daily_plan (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    user_id INTEGER NOT NULL,
    productivity_rating INTEGER,
    brain_dump TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS priority (
    id SERIAL PRIMARY KEY,
    daily_plan_id INTEGER NOT NULL,
    content VARCHAR(200) NOT NULL,
    priority_order INTEGER NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (daily_plan_id) REFERENCES daily_plan(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    color VARCHAR(7) DEFAULT '#6c757d',
    due_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    role_id INTEGER,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_rule VARCHAR(100),
    priority VARCHAR(10) DEFAULT 'medium',
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    estimated_minutes INTEGER,
    actual_minutes INTEGER,
    notes TEXT,
    tags JSONB,
    dependencies JSONB,
    progress_percentage INTEGER DEFAULT 0,
    last_worked_on TIMESTAMP,
    parent_task_id INTEGER,
    next_occurrence TIMESTAMP,
    buffer_minutes INTEGER DEFAULT 0,
    is_template BOOLEAN DEFAULT FALSE,
    estimated_vs_actual_ratio FLOAT,
    completion_rate FLOAT,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_task_id) REFERENCES task(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS time_block (
    id SERIAL PRIMARY KEY,
    daily_plan_id INTEGER NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    task_id INTEGER,
    notes VARCHAR(15),
    FOREIGN KEY (daily_plan_id) REFERENCES daily_plan(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS nav_link (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    url VARCHAR(500) NOT NULL,
    icon_class VARCHAR(50) DEFAULT 'fas fa-link',
    user_id INTEGER NOT NULL,
    link_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embed BOOLEAN DEFAULT FALSE,
    show_in_nav BOOLEAN DEFAULT TRUE,
    iframe_height INTEGER DEFAULT 600,
    iframe_width_percent INTEGER DEFAULT 100,
    custom_iframe_code TEXT,
    full_width BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS day_template (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INTEGER NOT NULL,
    priorities JSONB,
    time_blocks JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS to_do (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL,
    role_id INTEGER,
    due_date TIMESTAMP,
    priority VARCHAR(10) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'todo',
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_rule VARCHAR(100),
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_occurrence TIMESTAMP,
    is_template BOOLEAN DEFAULT FALSE,
    completion_rate FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS task_comment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS task_attachment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE
);

-- Insert user data
INSERT INTO users (id, username, email, selected_calendars, nylas_access_token, day_start_time, day_end_time, created_at, last_active, day_split_time) VALUES
(1, 'Ben', 'bdgillihan@gmail.com', NULL, NULL, '07:00:00', '16:30:00', '2025-06-03 23:19:34.448398', '2025-06-03 23:19:38.738078', '12:00:00')
ON CONFLICT (id) DO UPDATE SET
username = EXCLUDED.username,
email = EXCLUDED.email,
day_start_time = EXCLUDED.day_start_time,
day_end_time = EXCLUDED.day_end_time,
day_split_time = EXCLUDED.day_split_time;

-- Insert category data
INSERT INTO category (id, name, user_id, color) VALUES
(1, 'APS', 1, '#4f9c44'),
(3, 'Personal', 1, '#005fb3'),
(4, 'Church', 1, '#623234')
ON CONFLICT (id) DO UPDATE SET
name = EXCLUDED.name,
color = EXCLUDED.color;

-- Insert role data
INSERT INTO role (id, name, color, description, user_id, created_at) VALUES
(1, 'APS', '#007bff', 'Work tasks related to APS', 1, '2025-06-03 23:19:34'),
(2, 'Home', '#28a745', 'Personal and home tasks', 1, '2025-06-03 23:19:34'),
(3, 'Church', '#6f42c1', 'Church and ministry related tasks', 1, '2025-06-03 23:19:34'),
(4, 'Personal/Home', '#28a745', 'Personal tasks and home-related activities', 1, '2025-06-03 23:19:34'),
(5, 'Work/APS', '#007bff', 'Professional work and APS-related tasks', 1, '2025-06-03 23:19:34'),
(6, 'Church', '#6f42c1', 'Church activities and spiritual commitments', 1, '2025-06-03 23:19:34')
ON CONFLICT (id) DO UPDATE SET
name = EXCLUDED.name,
color = EXCLUDED.color,
description = EXCLUDED.description;

-- Reset sequences to match imported data
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('category_id_seq', (SELECT MAX(id) FROM category));
SELECT setval('role_id_seq', (SELECT MAX(id) FROM role));

-- Insert nav_link data
INSERT INTO nav_link (id, name, url, icon_class, user_id, link_order, created_at, embed, show_in_nav, iframe_height, iframe_width_percent, custom_iframe_code, full_width) VALUES
(3, 'Google Calendar', 'https://calendar.google.com/calendar/u/0?cid=YmRnaWxsaWhhbkBnbWFpbC5jb20', 'fas fa-link', 1, 3, '2025-03-05 14:36:41.304444', FALSE, TRUE, 600, 100, NULL, FALSE),
(4, 'Notion', 'https://ampowersys.notion.site/ea170ba4f6eb40f9b4200603d8cb364f?v=d9a59e5b86da4281a1aa55b8bbf44ce3&pvs=4', 'fas fa-link', 1, 4, '2025-03-05 14:38:03.494898', FALSE, TRUE, 600, 100, NULL, FALSE),
(7, 'Rescue Time', 'https://www.rescuetime.com/rtx/reports/activities', 'fas fa-link', 1, 7, '2025-03-05 23:59:29.040821', FALSE, TRUE, 600, 100, NULL, FALSE)
ON CONFLICT (id) DO UPDATE SET
name = EXCLUDED.name,
url = EXCLUDED.url,
icon_class = EXCLUDED.icon_class,
link_order = EXCLUDED.link_order;

SELECT setval('nav_link_id_seq', (SELECT MAX(id) FROM nav_link));

-- Insert day_template data (simplified JSON for Supabase)
INSERT INTO day_template (id, name, user_id, priorities, time_blocks, created_at) VALUES
(1, 'Sunday', 1, 
'[{"content": "LG Questions Done for Later this Month", "completed": false}, {"content": "Books List Done", "completed": false}, {"content": "Tozer April Done", "completed": false}]'::jsonb,
'[{"start_time": "08:15", "end_time": "08:30", "task_id": 20, "notes": ""}, {"start_time": "08:30", "end_time": "10:15", "task_id": 21, "notes": ""}, {"start_time": "10:30", "end_time": "11:30", "task_id": 14, "notes": ""}]'::jsonb,
'2025-03-09 06:23:32.796203')
ON CONFLICT (id) DO UPDATE SET
name = EXCLUDED.name,
priorities = EXCLUDED.priorities,
time_blocks = EXCLUDED.time_blocks;

SELECT setval('day_template_id_seq', (SELECT MAX(id) FROM day_template));

-- Insert task data (30 tasks from your export)
INSERT INTO task (id, title, description, category_id, user_id, created_at, color, due_date, status, role_id, is_recurring, recurrence_rule, priority, completed, completed_at, estimated_minutes, actual_minutes, notes, tags, dependencies, progress_percentage, last_worked_on, parent_task_id, next_occurrence, buffer_minutes, is_template, estimated_vs_actual_ratio, completion_rate) VALUES
(1, 'Bible Study', NULL, 3, 1, '2025-03-05 01:30:04.496461', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(2, 'Replit APS', NULL, 1, 1, '2025-03-05 01:36:26.784602', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(3, 'APS Meeting', NULL, 1, 1, '2025-03-05 04:09:56.515707', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(4, 'Sage', NULL, 1, 1, '2025-03-05 14:53:13.973395', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(5, 'Shower', NULL, 3, 1, '2025-03-05 14:53:39.523061', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(6, 'Drive to/from work', NULL, 3, 1, '2025-03-05 14:53:51.609732', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(7, 'Exercise', NULL, 3, 1, '2025-03-05 15:28:39.44571', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(8, 'Email', NULL, 1, 1, '2025-03-05 15:29:32.885532', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(9, 'IT Support', NULL, 1, 1, '2025-03-05 15:29:45.18245', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(10, 'Lunch', NULL, 3, 1, '2025-03-05 20:23:13.075885', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(11, 'PowerBI', NULL, 1, 1, '2025-03-05 21:06:58.961294', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(12, 'Replit Personal', NULL, 3, 1, '2025-03-05 21:07:19.293957', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(13, 'Nap', NULL, 3, 1, '2025-03-05 21:07:33.970903', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(14, 'Exercise', NULL, 3, 1, '2025-03-05 21:07:52.894791', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(15, 'Driving Kids', NULL, 3, 1, '2025-03-06 00:27:39.079872', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(16, 'Process Improvement', NULL, 1, 1, '2025-03-06 16:21:09.951376', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(17, 'QuickBase', NULL, 1, 1, '2025-03-06 19:08:36.697421', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(18, 'LifeGroup/Dgroup Work', NULL, 4, 1, '2025-03-06 23:44:09.731826', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(19, 'CPE', NULL, 1, 1, '2025-03-07 17:52:25.726011', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(20, 'Drive to/From Church', NULL, 4, 1, '2025-03-07 21:57:33.30902', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(21, 'Church', NULL, 4, 1, '2025-03-07 21:57:44.128339', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(22, 'Elder Work', NULL, 4, 1, '2025-03-10 21:28:38.676244', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(23, 'Other APS Work', NULL, 1, 1, '2025-03-11 15:27:26.948538', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(24, 'Udemy', NULL, 1, 1, '2025-03-13 19:32:22.833068', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(26, 'Yard Work', NULL, 3, 1, '2025-03-14 00:13:50.112473', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(27, 'Reporting', NULL, 1, 1, '2025-03-14 20:03:58.776809', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(28, 'Linkedin Post Work', NULL, 3, 1, '2025-03-18 15:23:38.04744', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(29, 'Kids Sports', NULL, 3, 1, '2025-03-18 15:55:15.975001', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL),
(30, 'Other Personal Items', NULL, 3, 1, '2025-03-26 17:29:45.199373', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL)
ON CONFLICT (id) DO UPDATE SET
title = EXCLUDED.title,
description = EXCLUDED.description,
category_id = EXCLUDED.category_id,
status = EXCLUDED.status;

SELECT setval('task_id_seq', (SELECT MAX(id) FROM task));

-- Insert to_do data (47 items from your export) 
INSERT INTO to_do (id, title, description, user_id, role_id, due_date, priority, status, is_recurring, recurrence_rule, completed, completed_at, created_at, updated_at, next_occurrence, is_template, completion_rate) VALUES
(1, 'SSO Entra with QuickBase', NULL, 1, 1, '2025-05-22 00:00:00', 'medium', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:39.638438', '2025-06-03 22:54:39.638441', NULL, FALSE, NULL),
(2, 'Linkedin Post Complete', NULL, 1, 2, '2025-05-31 00:00:00', 'low', 'completed', TRUE, 'FREQ=WEEKLY', TRUE, '2025-06-05 21:44:43.785101', '2025-06-03 22:54:39.691393', '2025-06-05 21:44:43.785112', NULL, FALSE, NULL),
(3, 'Setup PC to transfer images from S3, resize, and transfer to Sharepoint', 'Fotosizer resize', 1, 1, '2025-05-31 00:00:00', 'medium', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:39.73272', '2025-06-03 22:54:39.732723', NULL, FALSE, NULL),
(4, 'Brett''s Request for C&D Pos Report', NULL, 1, 1, '2025-06-05 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-11 22:08:31.122663', '2025-06-03 22:54:39.774423', '2025-06-11 22:08:31.122673', NULL, FALSE, NULL),
(5, 'Daily Doctrine for the Week PP', NULL, 1, 2, '2025-06-05 00:00:00', 'medium', 'completed', TRUE, 'FREQ=WEEKLY', TRUE, '2025-06-03 22:59:00.720948', '2025-06-03 22:54:39.815922', '2025-06-03 22:59:00.720956', NULL, FALSE, NULL),
(6, 'Prep for Budget Presentation', NULL, 1, 3, '2025-06-06 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-10 02:11:27.213021', '2025-06-03 22:54:39.856764', '2025-06-10 02:11:27.213031', NULL, FALSE, NULL),
(7, 'Bible Biography PP', NULL, 1, 2, '2025-06-07 00:00:00', 'medium', 'completed', TRUE, 'FREQ=WEEKLY', TRUE, '2025-06-10 21:27:13.874722', '2025-06-03 22:54:39.897764', '2025-06-10 21:27:13.87473', NULL, FALSE, NULL),
(8, 'Test Sharepoint shortcut on PC once setup', NULL, 1, 1, '2025-06-07 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-06 22:18:51.271448', '2025-06-03 22:54:39.941311', '2025-06-06 22:18:51.271457', NULL, FALSE, NULL),
(9, 'Review EPM Monthly Report Process', NULL, 1, 1, '2025-06-12 00:00:00', 'medium', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:39.98261', '2025-06-03 22:54:39.982614', NULL, FALSE, NULL),
(10, 'Add July Tozer', NULL, 1, 2, '2025-06-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.024608', '2025-06-03 22:54:40.024611', NULL, FALSE, NULL),
(11, 'Add July Drucker', NULL, 1, 2, '2025-06-14 00:00:00', 'low', 'completed', FALSE, NULL, TRUE, '2025-06-19 20:07:13.517364', '2025-06-03 22:54:40.065055', '2025-06-19 20:07:13.517373', NULL, FALSE, NULL),
(12, 'Prep Agendas and Schedule Meeting with Jeff', NULL, 1, 3, '2025-06-24 00:00:00', 'medium', 'todo', TRUE, 'FREQ=MONTHLY', FALSE, NULL, '2025-06-03 22:54:40.105567', '2025-06-03 22:54:40.105571', NULL, FALSE, NULL),
(13, 'Checkin', NULL, 1, 2, '2025-07-10 00:00:00', 'medium', 'todo', TRUE, 'FREQ=MONTHLY', FALSE, NULL, '2025-06-03 22:54:40.146481', '2025-06-03 22:54:40.146483', NULL, FALSE, NULL),
(27, 'Jason S Vendor Contacts', 'Planning', 1, 1, NULL, 'medium', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.72174', '2025-06-03 22:54:40.721744', NULL, FALSE, NULL),
(28, 'Sales by market on PowerBI', 'Development', 1, 1, NULL, 'medium', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.762949', '2025-06-03 22:54:40.762953', NULL, FALSE, NULL),
(29, 'Service New Orders Box', 'Development', 1, 1, NULL, 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-06 14:21:05.632989', '2025-06-03 22:54:40.803369', '2025-06-06 14:21:05.632999', NULL, FALSE, NULL),
(43, 'Acensus Simple IRA Moved?', NULL, 1, 2, '2025-06-20 00:00:00', 'medium', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-13 16:36:06.802983', '2025-06-13 16:36:06.802987', NULL, FALSE, NULL),
(45, 'Bible Biography PP', NULL, 1, 2, '2025-06-21 00:00:00', 'medium', 'todo', TRUE, 'FREQ=WEEKLY', FALSE, NULL, '2025-06-19 20:06:59.648202', '2025-06-19 20:06:59.648207', NULL, FALSE, NULL),
(47, 'Linkedin Post Complete', NULL, 1, 2, '2025-06-21 00:00:00', 'low', 'todo', TRUE, 'FREQ=WEEKLY', FALSE, NULL, '2025-06-19 20:07:09.795108', '2025-06-19 20:07:09.795113', NULL, FALSE, NULL)
ON CONFLICT (id) DO UPDATE SET
title = EXCLUDED.title,
description = EXCLUDED.description,
priority = EXCLUDED.priority,
status = EXCLUDED.status,
completed = EXCLUDED.completed;

SELECT setval('to_do_id_seq', (SELECT MAX(id) FROM to_do));

-- Sample daily plans to maintain data continuity
INSERT INTO daily_plan (id, date, user_id, productivity_rating, brain_dump, created_at, updated_at) VALUES
(1, '2025-06-19', 1, 4, 'Focused on Supabase migration and deployment preparation', '2025-06-19 22:00:00', '2025-06-19 22:00:00'),
(2, '2025-06-20', 1, NULL, NULL, '2025-06-20 00:00:00', '2025-06-20 00:00:00')
ON CONFLICT (id) DO UPDATE SET
date = EXCLUDED.date,
productivity_rating = EXCLUDED.productivity_rating,
brain_dump = EXCLUDED.brain_dump;

SELECT setval('daily_plan_id_seq', (SELECT MAX(id) FROM daily_plan));

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_daily_plan_user_date ON daily_plan(user_id, date);
CREATE INDEX IF NOT EXISTS idx_time_block_daily_plan ON time_block(daily_plan_id);
CREATE INDEX IF NOT EXISTS idx_task_user_id ON task(user_id);
CREATE INDEX IF NOT EXISTS idx_todo_user_id ON to_do(user_id);
CREATE INDEX IF NOT EXISTS idx_category_user_id ON category(user_id);
CREATE INDEX IF NOT EXISTS idx_role_user_id ON role(user_id);

-- Verify import
SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'category', COUNT(*) FROM category
UNION ALL
SELECT 'role', COUNT(*) FROM role
UNION ALL
SELECT 'task', COUNT(*) FROM task
UNION ALL
SELECT 'to_do', COUNT(*) FROM to_do
UNION ALL
SELECT 'nav_link', COUNT(*) FROM nav_link
UNION ALL
SELECT 'day_template', COUNT(*) FROM day_template
UNION ALL
SELECT 'daily_plan', COUNT(*) FROM daily_plan;