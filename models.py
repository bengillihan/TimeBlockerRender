from datetime import datetime
from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    daily_plans = db.relationship('DailyPlan', backref='user', lazy=True)

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
    content = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)
