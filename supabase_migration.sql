-- TimeBlocker Database Migration for Supabase
-- This file contains all the necessary SQL to set up the database schema

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    day_start_time TIME DEFAULT '07:00:00',
    day_end_time TIME DEFAULT '16:30:00',
    day_split_time TIME DEFAULT '12:00:00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS nav_link (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    url VARCHAR(500) NOT NULL,
    icon_class VARCHAR(50) DEFAULT 'fas fa-link',
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    "order" INTEGER DEFAULT 0,
    embed BOOLEAN DEFAULT FALSE,
    show_in_nav BOOLEAN DEFAULT TRUE,
    iframe_height INTEGER DEFAULT 600,
    iframe_width_percent INTEGER DEFAULT 100,
    custom_iframe_code TEXT,
    full_width BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_plan (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    productivity_rating INTEGER,
    brain_dump TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS priority (
    id SERIAL PRIMARY KEY,
    daily_plan_id INTEGER REFERENCES daily_plan(id) ON DELETE CASCADE,
    content VARCHAR(200) NOT NULL,
    "order" INTEGER NOT NULL,
    completed BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS time_block (
    id SERIAL PRIMARY KEY,
    daily_plan_id INTEGER REFERENCES daily_plan(id) ON DELETE CASCADE,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    task_id INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    notes VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    color VARCHAR(7) DEFAULT '#6c757d'
);

CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#6c757d',
    description TEXT,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES category(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES role(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_rule VARCHAR(100),
    next_occurrence TIMESTAMP,
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
    parent_task_id INTEGER REFERENCES task(id) ON DELETE CASCADE,
    buffer_minutes INTEGER DEFAULT 0,
    is_template BOOLEAN DEFAULT FALSE,
    estimated_vs_actual_ratio FLOAT,
    completion_rate FLOAT
);

CREATE TABLE IF NOT EXISTS task_comment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES task(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS task_attachment (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES task(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS day_template (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    priorities JSONB,
    time_blocks JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS todo (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    user_id INTEGER REFERENCES "user"(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES role(id) ON DELETE SET NULL,
    due_date TIMESTAMP,
    priority VARCHAR(10) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'todo',
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_rule VARCHAR(100),
    next_occurrence TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_template BOOLEAN DEFAULT FALSE,
    completion_rate FLOAT
);

-- Add foreign key constraint for time_block.task_id
ALTER TABLE time_block ADD CONSTRAINT fk_time_block_task 
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE SET NULL;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
CREATE INDEX IF NOT EXISTS idx_user_username ON "user"(username);
CREATE INDEX IF NOT EXISTS idx_task_title ON task(title);
CREATE INDEX IF NOT EXISTS idx_task_created_at ON task(created_at);
CREATE INDEX IF NOT EXISTS idx_task_due_date ON task(due_date);
CREATE INDEX IF NOT EXISTS idx_task_status ON task(status);
CREATE INDEX IF NOT EXISTS idx_task_is_recurring ON task(is_recurring);
CREATE INDEX IF NOT EXISTS idx_task_next_occurrence ON task(next_occurrence);
CREATE INDEX IF NOT EXISTS idx_task_priority ON task(priority);
CREATE INDEX IF NOT EXISTS idx_task_completed ON task(completed);
CREATE INDEX IF NOT EXISTS idx_todo_title ON todo(title);
CREATE INDEX IF NOT EXISTS idx_todo_due_date ON todo(due_date);
CREATE INDEX IF NOT EXISTS idx_todo_status ON todo(status);
CREATE INDEX IF NOT EXISTS idx_todo_is_recurring ON todo(is_recurring);
CREATE INDEX IF NOT EXISTS idx_todo_next_occurrence ON todo(next_occurrence);
CREATE INDEX IF NOT EXISTS idx_todo_priority ON todo(priority);
CREATE INDEX IF NOT EXISTS idx_todo_completed ON todo(completed);
CREATE INDEX IF NOT EXISTS idx_todo_created_at ON todo(created_at);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_task_user_completed ON task(user_id, completed);
CREATE INDEX IF NOT EXISTS idx_todo_user_completed ON todo(user_id, completed);
CREATE INDEX IF NOT EXISTS idx_daily_plan_user_date ON daily_plan(user_id, date);