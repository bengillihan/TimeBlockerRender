import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import routes after app initialization to avoid circular imports
from models import User, DailyPlan, Priority, TimeBlock
from google_auth import google_auth

app.register_blueprint(google_auth)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    daily_plan = DailyPlan.query.filter_by(
        user_id=current_user.id,
        date=datetime.strptime(date, '%Y-%m-%d').date()
    ).first()
    
    return render_template('index.html', daily_plan=daily_plan, date=date)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/daily-plan', methods=['POST'])
@login_required
def save_daily_plan():
    data = request.json
    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    
    daily_plan = DailyPlan.query.filter_by(
        user_id=current_user.id,
        date=date
    ).first()
    
    if not daily_plan:
        daily_plan = DailyPlan(user_id=current_user.id, date=date)
        db.session.add(daily_plan)
    
    daily_plan.productivity_rating = data.get('productivity_rating')
    daily_plan.brain_dump = data.get('brain_dump')
    
    # Update priorities
    Priority.query.filter_by(daily_plan_id=daily_plan.id).delete()
    for i, priority in enumerate(data.get('priorities', [])):
        p = Priority(
            daily_plan_id=daily_plan.id,
            content=priority['content'],
            order=i,
            completed=priority.get('completed', False)
        )
        db.session.add(p)
    
    # Update time blocks
    TimeBlock.query.filter_by(daily_plan_id=daily_plan.id).delete()
    for block in data.get('time_blocks', []):
        tb = TimeBlock(
            daily_plan_id=daily_plan.id,
            start_time=datetime.strptime(block['start_time'], '%H:%M').time(),
            end_time=datetime.strptime(block['end_time'], '%H:%M').time(),
            content=block['content'],
            completed=block.get('completed', False)
        )
        db.session.add(tb)
    
    db.session.commit()
    return jsonify({'status': 'success'})

with app.app_context():
    db.create_all()
