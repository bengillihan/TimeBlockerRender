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

class DayTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priorities = db.Column(db.JSON, nullable=True)
    time_blocks = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('templates', lazy=True))