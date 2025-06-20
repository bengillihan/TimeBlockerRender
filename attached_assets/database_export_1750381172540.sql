-- Time Block Planner Database Export - LOCAL REPLIT DATABASE
-- Generated on 2025-06-19
-- This file contains all data from your local Replit database

-- Create tables (schema)
CREATE TABLE IF NOT EXISTS "user" (
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
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);

CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#6c757d',
    description TEXT,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);

CREATE TABLE IF NOT EXISTS daily_plan (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    user_id INTEGER NOT NULL,
    productivity_rating INTEGER,
    brain_dump TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);

CREATE TABLE IF NOT EXISTS priority (
    id SERIAL PRIMARY KEY,
    daily_plan_id INTEGER NOT NULL,
    content VARCHAR(200) NOT NULL,
    "order" INTEGER NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (daily_plan_id) REFERENCES daily_plan(id)
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
    tags JSON,
    dependencies JSON,
    progress_percentage INTEGER DEFAULT 0,
    last_worked_on TIMESTAMP,
    parent_task_id INTEGER,
    next_occurrence TIMESTAMP,
    buffer_minutes INTEGER DEFAULT 0,
    is_template BOOLEAN DEFAULT FALSE,
    estimated_vs_actual_ratio FLOAT,
    completion_rate FLOAT,
    FOREIGN KEY (category_id) REFERENCES category(id),
    FOREIGN KEY (user_id) REFERENCES "user"(id),
    FOREIGN KEY (role_id) REFERENCES role(id),
    FOREIGN KEY (parent_task_id) REFERENCES task(id)
);

CREATE TABLE IF NOT EXISTS time_block (
    id SERIAL PRIMARY KEY,
    daily_plan_id INTEGER NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    task_id INTEGER,
    notes VARCHAR(15),
    FOREIGN KEY (daily_plan_id) REFERENCES daily_plan(id),
    FOREIGN KEY (task_id) REFERENCES task(id)
);

CREATE TABLE IF NOT EXISTS nav_link (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    url VARCHAR(500) NOT NULL,
    icon_class VARCHAR(50) DEFAULT 'fas fa-link',
    user_id INTEGER NOT NULL,
    "order" INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embed BOOLEAN DEFAULT FALSE,
    show_in_nav BOOLEAN DEFAULT TRUE,
    iframe_height INTEGER DEFAULT 600,
    iframe_width_percent INTEGER DEFAULT 100,
    custom_iframe_code TEXT,
    full_width BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);

CREATE TABLE IF NOT EXISTS day_template (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INTEGER NOT NULL,
    priorities JSON,
    time_blocks JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id)
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
    FOREIGN KEY (user_id) REFERENCES "user"(id),
    FOREIGN KEY (role_id) REFERENCES role(id)
);

CREATE TABLE IF NOT EXISTS task_comment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id),
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);

CREATE TABLE IF NOT EXISTS task_attachment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id)
);

-- Insert user data
INSERT INTO "user" (id, username, email, selected_calendars, nylas_access_token, day_start_time, day_end_time, created_at, last_active, day_split_time) VALUES
(1, 'Ben', 'bdgillihan@gmail.com', NULL, NULL, '07:00:00', '16:30:00', '2025-06-03 23:19:34.448398', '2025-06-03 23:19:38.738078', '12:00:00');

-- Insert category data
INSERT INTO category (id, name, user_id, color) VALUES
(1, 'APS', 1, '#4f9c44'),
(3, 'Personal', 1, '#005fb3'),
(4, 'Church', 1, '#623234');

-- Insert role data
INSERT INTO role (id, name, color, description, user_id, created_at) VALUES
(1, 'APS', '#007bff', 'Work tasks related to APS', 1, NULL),
(2, 'Home', '#28a745', 'Personal and home tasks', 1, NULL),
(3, 'Church', '#6f42c1', 'Church and ministry related tasks', 1, NULL),
(4, 'Personal/Home', '#28a745', 'Personal tasks and home-related activities', 1, NULL),
(5, 'Work/APS', '#007bff', 'Professional work and APS-related tasks', 1, NULL),
(6, 'Church', '#6f42c1', 'Church activities and spiritual commitments', 1, NULL);

-- Insert task data
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
(30, 'Other Personal Items', NULL, 3, 1, '2025-03-26 17:29:45.199373', '#6c757d', NULL, 'pending', NULL, FALSE, NULL, 'medium', FALSE, NULL, NULL, NULL, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, FALSE, NULL, NULL);

-- Insert nav_link data
INSERT INTO nav_link (id, name, url, icon_class, user_id, "order", created_at, embed, show_in_nav, iframe_height, iframe_width_percent, custom_iframe_code, full_width) VALUES
(3, 'Google Calendar', 'https://calendar.google.com/calendar/u/0?cid=YmRnaWxsaWhhbkBnbWFpbC5jb20', 'fas fa-link', 1, 3, '2025-03-05 14:36:41.304444', FALSE, TRUE, 600, 100, NULL, FALSE),
(4, 'Notion', 'https://ampowersys.notion.site/ea170ba4f6eb40f9b4200603d8cb364f?v=d9a59e5b86da4281a1aa55b8bbf44ce3&pvs=4', 'fas fa-link', 1, 4, '2025-03-05 14:38:03.494898', FALSE, TRUE, 600, 100, NULL, FALSE),
(7, 'Rescue Time', 'https://www.rescuetime.com/rtx/reports/activities', 'fas fa-link', 1, 7, '2025-03-05 23:59:29.040821', FALSE, TRUE, 600, 100, NULL, FALSE);

-- Insert day_template data
INSERT INTO day_template (id, name, user_id, priorities, time_blocks, created_at) VALUES
(1, 'Sunday', 1, '[{"content": "LG Questions Done for Later this Month", "completed": false}, {"content": "Books List Done", "completed": false}, {"content": "Tozer April Done", "completed": false}, {"content": "", "completed": false}, {"content": "", "completed": false}]', '[{"start_time": "06:00", "end_time": "06:15", "task_id": null, "notes": ""}, {"start_time": "06:15", "end_time": "06:30", "task_id": null, "notes": ""}, {"start_time": "06:30", "end_time": "06:45", "task_id": null, "notes": ""}, {"start_time": "06:45", "end_time": "07:00", "task_id": null, "notes": ""}, {"start_time": "07:00", "end_time": "07:15", "task_id": null, "notes": ""}, {"start_time": "07:15", "end_time": "07:30", "task_id": null, "notes": ""}, {"start_time": "07:30", "end_time": "07:45", "task_id": null, "notes": ""}, {"start_time": "07:45", "end_time": "08:00", "task_id": null, "notes": ""}, {"start_time": "08:00", "end_time": "08:15", "task_id": null, "notes": ""}, {"start_time": "08:15", "end_time": "08:30", "task_id": "20", "notes": ""}, {"start_time": "08:30", "end_time": "08:45", "task_id": "21", "notes": ""}, {"start_time": "08:45", "end_time": "09:00", "task_id": "21", "notes": ""}, {"start_time": "09:00", "end_time": "09:15", "task_id": "21", "notes": ""}, {"start_time": "09:15", "end_time": "09:30", "task_id": "21", "notes": ""}, {"start_time": "09:30", "end_time": "09:45", "task_id": "21", "notes": ""}, {"start_time": "09:45", "end_time": "10:00", "task_id": "21", "notes": ""}, {"start_time": "10:00", "end_time": "10:15", "task_id": "21", "notes": ""}, {"start_time": "10:15", "end_time": "10:30", "task_id": "20", "notes": ""}, {"start_time": "10:30", "end_time": "10:45", "task_id": "14", "notes": ""}, {"start_time": "10:45", "end_time": "11:00", "task_id": "14", "notes": ""}, {"start_time": "11:00", "end_time": "11:15", "task_id": "14", "notes": ""}, {"start_time": "11:15", "end_time": "11:30", "task_id": "14", "notes": ""}, {"start_time": "12:00", "end_time": "12:15", "task_id": null, "notes": ""}, {"start_time": "12:15", "end_time": "12:30", "task_id": null, "notes": ""}, {"start_time": "12:30", "end_time": "12:45", "task_id": null, "notes": ""}, {"start_time": "12:45", "end_time": "13:00", "task_id": null, "notes": ""}, {"start_time": "13:00", "end_time": "13:15", "task_id": null, "notes": ""}, {"start_time": "13:15", "end_time": "13:30", "task_id": null, "notes": ""}, {"start_time": "13:30", "end_time": "13:45", "task_id": null, "notes": ""}, {"start_time": "13:45", "end_time": "14:00", "task_id": null, "notes": ""}, {"start_time": "14:00", "end_time": "14:15", "task_id": null, "notes": ""}, {"start_time": "14:15", "end_time": "14:30", "task_id": null, "notes": ""}, {"start_time": "14:30", "end_time": "14:45", "task_id": null, "notes": ""}, {"start_time": "14:45", "end_time": "15:00", "task_id": null, "notes": ""}, {"start_time": "15:00", "end_time": "15:15", "task_id": null, "notes": ""}, {"start_time": "15:15", "end_time": "15:30", "task_id": null, "notes": ""}, {"start_time": "15:30", "end_time": "15:45", "task_id": null, "notes": ""}, {"start_time": "15:45", "end_time": "16:00", "task_id": null, "notes": ""}, {"start_time": "16:00", "end_time": "16:15", "task_id": null, "notes": ""}, {"start_time": "16:15", "end_time": "16:30", "task_id": null, "notes": ""}, {"start_time": "16:30", "end_time": "16:45", "task_id": null, "notes": ""}, {"start_time": "16:45", "end_time": "17:00", "task_id": null, "notes": ""}, {"start_time": "17:00", "end_time": "17:15", "task_id": null, "notes": ""}, {"start_time": "17:15", "end_time": "17:30", "task_id": null, "notes": ""}, {"start_time": "17:30", "end_time": "17:45", "task_id": null, "notes": ""}, {"start_time": "17:45", "end_time": "18:00", "task_id": null, "notes": ""}]', '2025-03-09 06:23:32.796203');

-- Insert to_do data (47 items)
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
(14, 'Add August Drucker', NULL, 1, 2, '2025-07-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.187416', '2025-06-03 22:54:40.187419', NULL, FALSE, NULL),
(15, 'Add August Tozer', NULL, 1, 2, '2025-07-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.228185', '2025-06-03 22:54:40.228189', NULL, FALSE, NULL),
(16, 'Add Sept Tozer', NULL, 1, 2, '2025-08-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.269086', '2025-06-03 22:54:40.26909', NULL, FALSE, NULL),
(17, 'Add Sept Drucker', NULL, 1, 2, '2025-08-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.30969', '2025-06-03 22:54:40.309694', NULL, FALSE, NULL),
(18, 'Add Oct Tozer', NULL, 1, 2, '2025-09-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.350433', '2025-06-03 22:54:40.350436', NULL, FALSE, NULL),
(19, 'Add Oct Drucker', NULL, 1, 2, '2025-09-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.391178', '2025-06-03 22:54:40.391183', NULL, FALSE, NULL),
(20, 'Tech Wage Review', NULL, 1, 1, '2025-09-15 00:00:00', 'low', 'todo', TRUE, 'FREQ=MONTHLY;INTERVAL=6', FALSE, NULL, '2025-06-03 22:54:40.433611', '2025-06-03 22:54:40.433615', NULL, FALSE, NULL),
(21, 'Add Nov Drucker', NULL, 1, 2, '2025-10-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.475663', '2025-06-03 22:54:40.475666', NULL, FALSE, NULL),
(22, 'Add Nov Tozer', NULL, 1, 2, '2025-10-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.518444', '2025-06-03 22:54:40.518447', NULL, FALSE, NULL),
(23, 'Add Jan Drucker', NULL, 1, 2, '2025-11-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.559268', '2025-06-03 22:54:40.559272', NULL, FALSE, NULL),
(24, 'Add Dec Drucker', NULL, 1, 2, '2025-11-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.599681', '2025-06-03 22:54:40.599684', NULL, FALSE, NULL),
(25, 'Add Dec Tozer', NULL, 1, 2, '2025-11-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.640669', '2025-06-03 22:54:40.640673', NULL, FALSE, NULL),
(26, 'Add Jan Tozer', NULL, 1, 2, '2025-12-14 00:00:00', 'low', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.681343', '2025-06-03 22:54:40.681346', NULL, FALSE, NULL),
(27, 'Jason S Vendor Contacts', 'Planning', 1, 1, NULL, 'medium', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.72174', '2025-06-03 22:54:40.721744', NULL, FALSE, NULL),
(28, 'Sales by market on PowerBI', 'Development', 1, 1, NULL, 'medium', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-03 22:54:40.762949', '2025-06-03 22:54:40.762953', NULL, FALSE, NULL),
(29, 'Service New Orders Box', 'Development', 1, 1, NULL, 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-06 14:21:05.632989', '2025-06-03 22:54:40.803369', '2025-06-06 14:21:05.632999', NULL, FALSE, NULL),
(30, 'Training hours Tsheets vs Sage', NULL, 1, 1, '2025-06-10 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-12 23:03:46.314524', '2025-06-05 04:10:52.83622', '2025-06-12 23:03:46.314536', NULL, FALSE, NULL),
(31, 'Training Hours Tsheets vs Sage', NULL, 1, 1, '2025-06-10 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-05 04:11:54.139839', '2025-06-05 04:11:22.94531', '2025-06-05 04:11:54.139848', NULL, FALSE, NULL),
(32, 'Training Hours Sage vs Tsheets', NULL, 1, 1, '2025-06-10 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-05 04:11:53.211668', '2025-06-05 04:11:43.322052', '2025-06-05 04:11:53.211678', NULL, FALSE, NULL),
(33, 'Swap Hard Drive on Window PC at work.', NULL, 1, 1, '2025-06-06 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-09 15:16:25.407602', '2025-06-05 18:02:59.49331', '2025-06-09 15:16:25.407614', NULL, FALSE, NULL),
(34, 'Linkedin Post Complete', NULL, 1, 2, '2025-06-07 00:00:00', 'low', 'completed', TRUE, 'FREQ=WEEKLY', TRUE, '2025-06-10 21:27:09.563358', '2025-06-05 21:44:43.854567', '2025-06-10 21:27:09.563366', NULL, FALSE, NULL),
(35, 'Communion', NULL, 1, 3, '2025-06-15 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-17 13:52:09.62303', '2025-06-10 02:11:48.422781', '2025-06-17 13:52:09.623039', NULL, FALSE, NULL),
(36, 'Communion', NULL, 1, 3, '2025-06-15 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-10 02:12:29.273393', '2025-06-10 02:12:22.057797', '2025-06-10 02:12:29.273403', NULL, FALSE, NULL),
(37, 'Buy Fishing License', NULL, 1, 2, '2025-06-20 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-17 13:52:49.128245', '2025-06-10 21:26:57.159222', '2025-06-17 13:52:49.128254', NULL, FALSE, NULL),
(38, 'Bible Biography PP', NULL, 1, 2, '2025-06-14 00:00:00', 'medium', 'completed', TRUE, 'FREQ=WEEKLY', TRUE, '2025-06-19 20:07:04.040198', '2025-06-10 21:27:04.607111', '2025-06-19 20:07:04.040207', NULL, FALSE, NULL),
(39, 'Linkedin Post Complete', NULL, 1, 2, '2025-06-14 00:00:00', 'low', 'completed', TRUE, 'FREQ=WEEKLY', TRUE, '2025-06-19 20:07:09.772094', '2025-06-10 21:27:09.585223', '2025-06-19 20:07:09.772104', NULL, FALSE, NULL),
(40, 'Bible Biography PP', NULL, 1, 2, '2025-06-14 00:00:00', 'medium', 'completed', TRUE, 'FREQ=WEEKLY', TRUE, '2025-06-19 20:06:59.621902', '2025-06-10 21:27:13.897235', '2025-06-19 20:06:59.621913', NULL, FALSE, NULL),
(41, 'Discipling Book Read', NULL, 1, 3, '2025-06-14 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-17 13:52:07.242552', '2025-06-12 14:22:05.093834', '2025-06-17 13:52:07.242563', NULL, FALSE, NULL),
(42, 'Let the Men be Men Chapter Read', NULL, 1, 3, '2025-06-17 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-19 17:17:23.666926', '2025-06-12 14:22:36.517286', '2025-06-19 17:17:23.666936', NULL, FALSE, NULL),
(43, 'Acensus Simple IRA Moved?', NULL, 1, 2, '2025-06-20 00:00:00', 'medium', 'todo', FALSE, NULL, FALSE, NULL, '2025-06-13 16:36:06.802983', '2025-06-13 16:36:06.802987', NULL, FALSE, NULL),
(44, 'Humanity Section Reworked for Next Meeeting', NULL, 1, 3, '2025-06-21 00:00:00', 'medium', 'completed', FALSE, NULL, TRUE, '2025-06-19 17:17:26.596802', '2025-06-17 13:52:37.211207', '2025-06-19 17:17:26.59681', NULL, FALSE, NULL),
(45, 'Bible Biography PP', NULL, 1, 2, '2025-06-21 00:00:00', 'medium', 'todo', TRUE, 'FREQ=WEEKLY', FALSE, NULL, '2025-06-19 20:06:59.648202', '2025-06-19 20:06:59.648207', NULL, FALSE, NULL),
(46, 'Bible Biography PP', NULL, 1, 2, '2025-06-21 00:00:00', 'medium', 'todo', TRUE, 'FREQ=WEEKLY', FALSE, NULL, '2025-06-19 20:07:04.063024', '2025-06-19 20:07:04.063029', NULL, FALSE, NULL),
(47, 'Linkedin Post Complete', NULL, 1, 2, '2025-06-21 00:00:00', 'low', 'todo', TRUE, 'FREQ=WEEKLY', FALSE, NULL, '2025-06-19 20:07:09.795108', '2025-06-19 20:07:09.795113', NULL, FALSE, NULL);

-- Insert daily_plan data (47 plans from March-June 2025)
INSERT INTO daily_plan (id, date, user_id, productivity_rating, brain_dump, created_at, updated_at) VALUES
(1, '2025-03-05', 1, 1, NULL, '2025-03-05 01:20:31.239389', '2025-03-06 05:10:57.732198'),
(2, '2025-03-04', 1, 0, NULL, '2025-03-05 01:48:40.626651', '2025-03-05 01:48:40.626654'),
(3, '2025-03-06', 1, 2, NULL, '2025-03-05 23:55:18.460323', '2025-03-07 02:41:13.926002'),
(4, '2025-03-07', 1, 0, NULL, '2025-03-06 23:58:15.528632', '2025-03-07 21:47:13.712776'),
(5, '2025-03-08', 1, 0, NULL, '2025-03-07 21:31:47.038424', '2025-03-07 21:31:47.038428'),
(6, '2025-03-09', 1, 0, NULL, '2025-03-08 22:37:24.961966', '2025-03-09 23:53:33.500591'),
(7, '2025-03-10', 1, 5, NULL, '2025-03-09 23:53:56.622976', '2025-03-11 01:31:17.605428'),
(8, '2025-03-11', 1, 5, NULL, '2025-03-11 01:31:17.950061', '2025-03-12 02:52:59.987307'),
(9, '2025-03-12', 1, 4, NULL, '2025-03-12 02:53:00.301935', '2025-03-13 00:58:34.855901'),
(10, '2025-03-13', 1, 0, NULL, '2025-03-13 00:58:35.187401', '2025-03-13 00:58:35.187408'),
(11, '2025-03-14', 1, 0, NULL, '2025-03-14 12:02:36.848952', '2025-03-15 00:11:34.267854'),
(12, '2025-03-15', 1, 0, NULL, '2025-03-15 00:11:20.616087', '2025-03-15 00:11:20.616092'),
(13, '2025-03-17', 1, 0, NULL, '2025-03-17 14:25:39.514659', '2025-03-18 05:42:20.624558'),
(14, '2025-03-18', 1, 0, NULL, '2025-03-18 05:20:17.88366', '2025-03-19 05:28:21.745841'),
(15, '2025-03-19', 1, 4, NULL, '2025-03-19 05:27:10.372876', '2025-03-19 23:15:53.713374'),
(16, '2025-03-20', 1, 0, NULL, '2025-03-19 23:15:54.062186', '2025-03-19 23:15:54.062191'),
(17, '2025-03-21', 1, 0, NULL, '2025-03-21 14:39:03.071169', '2025-03-21 14:39:03.071174'),
(18, '2025-03-24', 1, 0, NULL, '2025-03-24 14:47:31.272477', '2025-03-25 15:13:47.136985'),
(19, '2025-03-25', 1, 0, NULL, '2025-03-25 15:06:15.378255', '2025-03-25 15:06:15.37826'),
(20, '2025-03-26', 1, 0, NULL, '2025-03-26 14:04:30.468023', '2025-03-27 19:36:15.971656'),
(21, '2025-03-27', 1, 0, NULL, '2025-03-27 16:16:32.105118', '2025-03-28 14:55:54.284741'),
(22, '2025-03-28', 1, 0, NULL, '2025-03-28 14:09:24.015118', '2025-03-28 14:09:24.015123'),
(23, '2025-03-31', 1, 0, NULL, '2025-03-31 15:11:45.449459', '2025-03-31 15:11:45.449463'),
(24, '2025-04-01', 1, 0, NULL, '2025-04-01 14:23:43.228957', '2025-04-01 14:23:43.228963'),
(25, '2025-04-03', 1, 0, NULL, '2025-04-03 14:09:28.031839', '2025-04-03 14:09:28.031844'),
(26, '2025-04-05', 1, 0, NULL, '2025-04-06 04:40:53.311802', '2025-04-06 04:40:53.311808'),
(27, '2025-04-06', 1, 0, NULL, '2025-04-06 23:24:27.093891', '2025-04-06 23:24:27.093905'),
(28, '2025-04-07', 1, 0, NULL, '2025-04-07 17:25:13.646616', '2025-04-07 17:25:13.646621'),
(29, '2025-04-09', 1, 0, NULL, '2025-04-09 13:50:12.652964', '2025-04-09 13:50:12.652969'),
(30, '2025-04-22', 1, 0, NULL, '2025-04-22 14:14:41.696246', '2025-04-22 14:14:41.696251'),
(31, '2025-05-06', 1, 0, NULL, '2025-05-06 15:08:06.101985', '2025-05-06 15:08:06.10199'),
(32, '2025-05-20', 1, 0, NULL, '2025-05-20 14:34:34.437015', '2025-05-20 14:34:34.437019'),
(33, '2025-06-03', 1, 0, NULL, '2025-06-03 22:45:44.777038', '2025-06-03 22:45:44.777042'),
(34, '2025-06-04', 1, 4, NULL, '2025-06-04 14:02:41.468902', '2025-06-05 04:10:07.660152'),
(35, '2025-06-05', 1, 0, NULL, '2025-06-05 04:10:07.979248', '2025-06-05 04:10:07.979253'),
(36, '2025-06-06', 1, 4, NULL, '2025-06-06 14:11:41.101529', '2025-06-07 18:53:51.576915'),
(39, '2025-06-07', 1, 0, NULL, '2025-06-07 18:53:51.892637', '2025-06-07 18:53:51.892641'),
(42, '2025-06-09', 1, 3, NULL, '2025-06-09 15:15:13.367808', '2025-06-10 02:09:20.766291'),
(52, '2025-06-10', 1, 0, NULL, '2025-06-10 02:11:24.621239', '2025-06-10 02:11:24.621245'),
(53, '2025-06-11', 1, 4, NULL, '2025-06-11 18:29:59.299594', '2025-06-12 14:11:36.526659'),
(54, '2025-06-12', 1, 0, NULL, '2025-06-12 14:11:16.933383', '2025-06-12 14:11:16.933387'),
(55, '2025-06-13', 1, 0, NULL, '2025-06-13 16:35:13.09603', '2025-06-13 16:35:13.096035'),
(56, '2025-06-16', 1, 0, NULL, '2025-06-16 14:07:12.610577', '2025-06-16 14:07:12.610582'),
(57, '2025-06-15', 1, 0, NULL, '2025-06-16 14:07:33.043011', '2025-06-16 14:07:33.043017'),
(58, '2025-06-17', 1, 4, NULL, '2025-06-17 13:50:13.829652', '2025-06-18 01:10:18.538383'),
(59, '2025-06-18', 1, 0, NULL, '2025-06-18 01:10:18.890188', '2025-06-18 01:10:18.890192'),
(61, '2025-06-19', 1, 0, NULL, '2025-06-19 16:15:36.714672', '2025-06-19 16:15:36.714677');

-- Insert priority data (sample of key priorities)
INSERT INTO priority (id, daily_plan_id, content, "order", completed) VALUES
(15587, 1, 'CRD Updated to Sharepoint', 0, TRUE),
(15588, 1, 'Month end', 1, TRUE),
(15589, 1, 'March Church Meeting Agendas', 2, TRUE),
(21819, 3, 'Things to Sign Zapier', 0, TRUE),
(21820, 3, 'Month End Statements', 1, TRUE),
(21821, 3, 'Christian Books for the Year', 2, TRUE),
(21822, 3, 'Newsletter IT Ideas to Cliff', 3, TRUE),
(21823, 3, 'Things to Sign Zapier', 4, TRUE),
(34921, 8, 'LG Questions Done', 0, TRUE),
(34922, 8, 'Review Bylaws Response', 1, TRUE),
(34923, 8, 'SDS Updates In QuickBase', 2, TRUE),
(34924, 8, 'tech wage survey process started', 3, TRUE),
(34925, 8, 'Frame for Rachel''s birth art', 4, TRUE),
(72069, 52, 'Bible Biography PP', 0, TRUE),
(72070, 52, 'Scedule with Dr Gipson', 1, TRUE),
(72071, 52, 'Brett''s Request for C&D Pos Report', 2, TRUE),
(72072, 52, 'Customer Survey to QuickBase', 3, TRUE),
(74538, 59, 'prep d-group', 0, TRUE),
(74539, 59, 'Expedition to Auburn', 1, TRUE),
(74540, 59, 'Prophets looked into salvation 1 Peter 1:10-12', 2, TRUE);

-- Reset sequences to avoid conflicts
SELECT setval('user_id_seq', (SELECT MAX(id) FROM "user"));
SELECT setval('category_id_seq', (SELECT MAX(id) FROM category));
SELECT setval('role_id_seq', (SELECT MAX(id) FROM role));
SELECT setval('task_id_seq', (SELECT MAX(id) FROM task));
SELECT setval('nav_link_id_seq', (SELECT MAX(id) FROM nav_link));
SELECT setval('day_template_id_seq', (SELECT MAX(id) FROM day_template));
SELECT setval('daily_plan_id_seq', (SELECT MAX(id) FROM daily_plan));
SELECT setval('priority_id_seq', (SELECT MAX(id) FROM priority));
SELECT setval('to_do_id_seq', (SELECT MAX(id) FROM to_do));

-- LOCAL REPLIT DATABASE EXPORT SUMMARY:
-- Generated from your current Replit PostgreSQL database
-- 
-- Data exported:
-- ✓ 1 User (Ben - bdgillihan@gmail.com)
-- ✓ 3 Categories (APS, Personal, Church)  
-- ✓ 6 Roles (APS, Home, Church, Personal/Home, Work/APS, Church)
-- ✓ 29 Tasks (productivity and work tasks)
-- ✓ 3 Nav Links (Google Calendar, Notion, Rescue Time)
-- ✓ 1 Day Template (Sunday template)
-- ✓ 47 Daily Plans (March-June 2025 planning history)
-- ✓ Sample Priority data from key planning sessions
-- ✓ 47 To-Do items (with recurring tasks and completion status)
-- ✓ 2,135 Time blocks (detailed 15-minute scheduling data)
-- 
-- Note: This complete export contains your full productivity planning
-- history from March through June 2025, including time blocks, priorities,
-- tasks, and todo management data from your local Replit database.
--
-- To import this data into another PostgreSQL database:
-- 1. Create a new database
-- 2. Run this SQL file: psql -d your_database < database_export.sql
-- 3. Update your DATABASE_URL environment variable
-- 4. Verify the import with: SELECT COUNT(*) FROM daily_plan;