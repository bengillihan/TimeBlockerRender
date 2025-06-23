from datetime import datetime
import secrets
from app import db
from flask_login import UserMixin
from sqlalchemy import Index

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    daily_plans = db.relationship('DailyPlan', backref='user', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)
# nav_links relationship removed
    # Day start/end time preferences
    day_start_time = db.Column(db.Time, default=datetime.strptime('07:00', '%H:%M').time())
    day_end_time = db.Column(db.Time, default=datetime.strptime('16:30', '%H:%M').time())
    day_split_time = db.Column(db.Time, default=datetime.strptime('12:00', '%H:%M').time())
    roles = db.relationship('Role', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    current_session_id = db.Column(db.String(64), nullable=True)  # Track current active session
    
    def generate_new_session(self):
        """Generate a new session ID and invalidate old sessions"""
        self.current_session_id = secrets.token_urlsafe(32)
        db.session.commit()
        return self.current_session_id
    
    def is_session_valid(self, session_id):
        """Check if the provided session ID matches the current session"""
        return self.current_session_id == session_id
    
    def invalidate_session(self):
        """Invalidate the current session"""
        self.current_session_id = None
        db.session.commit()

# NavLink model removed - simplified navigation

class DailyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    productivity_rating = db.Column(db.Integer)
    brain_dump = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    priorities = db.relationship('Priority', backref='daily_plan', lazy=True)
    time_blocks = db.relationship('TimeBlock', backref='daily_plan', lazy=True)

class Priority(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    daily_plan_id = db.Column(db.Integer, db.ForeignKey('daily_plan.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)

class TimeBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    daily_plan_id = db.Column(db.Integer, db.ForeignKey('daily_plan.id'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.String(15))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)
    color = db.Column(db.String(7), default='#6c757d')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    time_blocks = db.relationship('TimeBlock', backref='task', lazy=True)
    
    # Enhanced task tracking fields
    due_date = db.Column(db.DateTime, nullable=True, index=True)
    status = db.Column(db.String(20), default='pending', index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    is_recurring = db.Column(db.Boolean, default=False, index=True)
    recurrence_rule = db.Column(db.String(100), nullable=True)
    next_occurrence = db.Column(db.DateTime, nullable=True, index=True)  # New field for recurring tasks
    priority = db.Column(db.String(10), default='medium', index=True)
    completed = db.Column(db.Boolean, default=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    estimated_minutes = db.Column(db.Integer, nullable=True)
    actual_minutes = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text)
    tags = db.Column(db.JSON)
    dependencies = db.Column(db.JSON)
    
    # Progress tracking
    progress_percentage = db.Column(db.Integer, default=0)
    last_worked_on = db.Column(db.DateTime, nullable=True)
    
    # Subtasks relationship
    parent_task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    subtasks = db.relationship('Task', backref=db.backref('parent_task', remote_side=[id]), lazy=True)
    
    # Add buffer time for time blocks
    buffer_minutes = db.Column(db.Integer, default=0)
    
    # Template flag
    is_template = db.Column(db.Boolean, default=False)
    
    # Analytics fields
    estimated_vs_actual_ratio = db.Column(db.Float, nullable=True)
    completion_rate = db.Column(db.Float, nullable=True)
    
    def get_total_time_spent(self):
        """Calculate total time spent on this task from time blocks"""
        from sqlalchemy.orm import Session
        total_minutes = 0
        # Use db.session to query time blocks for this task
        blocks = db.session.query(TimeBlock).filter(
            TimeBlock.task_id == self.id, 
            TimeBlock.completed == True
        ).all()
        for block in blocks:
            # Each time block represents 15 minutes
            total_minutes += 15
        return total_minutes
    
    def update_analytics(self):
        """Update task analytics"""
        if self.estimated_minutes and self.actual_minutes:
            self.estimated_vs_actual_ratio = self.actual_minutes / self.estimated_minutes
        
        # Calculate completion rate based on subtasks
        if self.subtasks:
            completed_subtasks = sum(1 for subtask in self.subtasks if subtask.completed)
            self.completion_rate = (completed_subtasks / len(self.subtasks)) * 100
    
    def get_status_color(self):
        """Return Bootstrap color class for task status"""
        status_colors = {
            'pending': 'secondary',
            'in_progress': 'primary',
            'completed': 'success',
            'blocked': 'danger'
        }
        return status_colors.get(self.status, 'secondary')
    
    def get_priority_color(self):
        """Return Bootstrap color class for task priority"""
        priority_colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'orange',
            'urgent': 'danger'
        }
        return priority_colors.get(self.priority, 'warning')
    
    def is_overdue(self):
        """Check if task is overdue"""
        return self.due_date and self.due_date < datetime.utcnow() and not self.completed

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#6c757d')
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='assigned_role', lazy=True)

class TaskComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    task = db.relationship('Task', backref=db.backref('comments', lazy=True))

class TaskAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    task = db.relationship('Task', backref=db.backref('attachments', lazy=True))

class DayTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    priorities = db.Column(db.JSON, nullable=True)
    time_blocks = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('templates', lazy=True))

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    due_date = db.Column(db.DateTime, nullable=True, index=True)
    priority = db.Column(db.String(10), default='medium', index=True)
    status = db.Column(db.String(20), default='todo', index=True)
    is_recurring = db.Column(db.Boolean, default=False, index=True)
    recurrence_rule = db.Column(db.String(100), nullable=True)
    next_occurrence = db.Column(db.DateTime, nullable=True, index=True)  # New field for recurring todos
    completed = db.Column(db.Boolean, default=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Template flag
    is_template = db.Column(db.Boolean, default=False)
    
    # Analytics fields
    completion_rate = db.Column(db.Float, nullable=True)
    
    user = db.relationship('User', backref=db.backref('todos', lazy=True))
    assigned_role = db.relationship('Role', backref=db.backref('todos', lazy=True))
    
    def get_priority_color(self):
        """Return Bootstrap color class for todo priority"""
        colors = {
            'low': 'secondary',
            'medium': 'warning',
            'high': 'orange',
            'urgent': 'danger'
        }
        return colors.get(self.priority, 'secondary')
    
    def get_status_color(self):
        """Return Bootstrap color class for todo status"""
        colors = {
            'todo': 'secondary',
            'in_progress': 'primary',
            'completed': 'success'
        }
        return colors.get(self.status, 'secondary')
    
    def is_overdue(self):
        """Check if todo is overdue"""
        if not self.due_date or self.completed:
            return False
        return self.due_date.date() < datetime.now().date()

# Add indexes for frequently queried fields
Index('idx_daily_plan_user_date', DailyPlan.user_id, DailyPlan.date)
Index('idx_task_user_completed', Task.user_id, Task.completed)
Index('idx_task_user_due_date', Task.user_id, Task.due_date)
Index('idx_todo_user_completed', ToDo.user_id, ToDo.completed)
Index('idx_todo_user_due_date', ToDo.user_id, ToDo.due_date)
Index('idx_timeblock_daily_plan', TimeBlock.daily_plan_id)
Index('idx_task_category', Task.category_id)
Index('idx_task_role', Task.role_id)