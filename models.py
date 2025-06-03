from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    daily_plans = db.relationship('DailyPlan', backref='user', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)
    nav_links = db.relationship('NavLink', backref='user', lazy=True)
    selected_calendars = db.Column(db.JSON)
    nylas_access_token = db.Column(db.String(512))
    # Add day start/end time preferences
    day_start_time = db.Column(db.Time, default=datetime.strptime('07:00', '%H:%M').time())
    day_end_time = db.Column(db.Time, default=datetime.strptime('16:30', '%H:%M').time())
    roles = db.relationship('Role', backref='user', lazy=True)

class NavLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    icon_class = db.Column(db.String(50), default='fas fa-link')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    embed = db.Column(db.Boolean, default=False)
    show_in_nav = db.Column(db.Boolean, default=True)
    iframe_height = db.Column(db.Integer, default=600)
    iframe_width_percent = db.Column(db.Integer, default=100)
    custom_iframe_code = db.Column(db.Text)
    full_width = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DailyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)
    color = db.Column(db.String(7), default='#6c757d')

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_blocks = db.relationship('TimeBlock', backref='task', lazy=True)
    
    # Enhanced task tracking fields
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, blocked
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_rule = db.Column(db.String(100), nullable=True)  # For storing cron-like rules
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, urgent
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    estimated_minutes = db.Column(db.Integer, nullable=True)
    actual_minutes = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text)
    tags = db.Column(db.JSON)  # Store array of tags
    dependencies = db.Column(db.JSON)  # Store array of task IDs this task depends on
    
    # Progress tracking
    progress_percentage = db.Column(db.Integer, default=0)  # 0-100
    last_worked_on = db.Column(db.DateTime, nullable=True)
    
    # Subtasks relationship
    parent_task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    subtasks = db.relationship('Task', backref=db.backref('parent_task', remote_side=[id]), lazy=True)
    
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='assigned_role', lazy=True)

class TaskComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priorities = db.Column(db.JSON, nullable=True)
    time_blocks = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('templates', lazy=True))