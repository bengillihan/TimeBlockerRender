-- Add missing tasks and todos to Supabase
-- Run this in Supabase SQL Editor if tasks/todos are missing

-- Insert task data (29 tasks from your export)
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

-- Insert to_do data (18 key items from your export) 
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
(47, 'Linkedin Post Complete', NULL, 1, 2, '2025-06-21 00:00:00', 'low', 'todo', TRUE, 'FREQ=WEEKLY', FALSE, NULL, '2025-06-19 20:07:09.795108', '2025-06-19 20:07:09.795113', NULL, FALSE, NULL)
ON CONFLICT (id) DO UPDATE SET
title = EXCLUDED.title,
description = EXCLUDED.description,
priority = EXCLUDED.priority,
status = EXCLUDED.status,
completed = EXCLUDED.completed;

-- Reset sequences
SELECT setval('task_id_seq', (SELECT MAX(id) FROM task));
SELECT setval('to_do_id_seq', (SELECT MAX(id) FROM to_do));

-- Verify the import
SELECT 'tasks' as table_name, COUNT(*) as record_count FROM task
UNION ALL
SELECT 'to_do', COUNT(*) FROM to_do
UNION ALL
SELECT 'task_pending', COUNT(*) FROM task WHERE status = 'pending'
UNION ALL
SELECT 'todo_active', COUNT(*) FROM to_do WHERE completed = false;