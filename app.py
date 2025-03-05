import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
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
from models import User, DailyPlan, Priority, TimeBlock, Category, Task
from google_auth import google_auth

app.register_blueprint(google_auth)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_default_categories(user):
    default_categories = ['APS', 'Church', 'Personal']
    for cat_name in default_categories:
        if not Category.query.filter_by(name=cat_name, user_id=user.id).first():
            category = Category(name=cat_name, user_id=user.id)
            db.session.add(category)
    db.session.commit()

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    daily_plan = DailyPlan.query.filter_by(
        user_id=current_user.id,
        date=datetime.strptime(date, '%Y-%m-%d').date()
    ).first()

    # Get categories and their tasks for the time block selector
    categories = Category.query.filter_by(user_id=current_user.id).all()

    # If there's a daily plan, get its time blocks with task information
    time_blocks = []
    if daily_plan:
        time_blocks = [{
            'start_time': block.start_time.strftime('%H:%M'),
            'task_id': block.task_id,
            'completed': block.completed
        } for block in daily_plan.time_blocks]

    return render_template('index.html', 
                         daily_plan=daily_plan, 
                         date=date, 
                         categories=categories,
                         time_blocks=time_blocks)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/tasks')
@login_required
def tasks():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', categories=categories)

@app.route('/api/categories', methods=['POST'])
@login_required
def add_category():
    name = request.json.get('name')
    color = request.json.get('color', '#6c757d')
    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    category = Category(name=name, color=color, user_id=current_user.id)
    db.session.add(category)
    db.session.commit()
    return jsonify({'id': category.id, 'name': category.name, 'color': category.color})

@app.route('/api/categories/<int:category_id>', methods=['PUT', 'DELETE'])
@login_required
def category_operations(category_id):
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()

    if request.method == 'DELETE':
        # Delete all tasks in the category
        Task.query.filter_by(category_id=category.id).delete()
        db.session.delete(category)
        db.session.commit()
        return '', 204

    data = request.json
    category.name = data.get('name', category.name)
    category.color = data.get('color', category.color)
    db.session.commit()
    return jsonify({
        'id': category.id,
        'name': category.name,
        'color': category.color
    })

@app.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def manage_tasks():
    if request.method == 'GET':
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'category_id': task.category_id,
            'color': task.color
        } for task in tasks])

    data = request.json
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        category_id=data['category_id'],
        color=data.get('color', '#6c757d'),
        user_id=current_user.id
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'category_id': task.category_id,
        'color': task.color
    })

@app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
@login_required
def task_operations(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return '', 204

    data = request.json
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.category_id = data.get('category_id', task.category_id)
    task.color = data.get('color', task.color)
    db.session.commit()
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'category_id': task.category_id,
        'color': task.color
    })

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
            task_id=block.get('task_id'),
            completed=block.get('completed', False)
        )
        db.session.add(tb)

    db.session.commit()
    return jsonify({'status': 'success'})

with app.app_context():
    db.create_all()