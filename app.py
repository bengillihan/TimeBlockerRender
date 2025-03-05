import os
import logging
import pytz
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import func

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__) # Added logger for error handling

# Configure timezone
pacific_tz = pytz.timezone('America/Los_Angeles')

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

def get_current_pacific_date():
    return datetime.now(pacific_tz).date()

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Convert date parameter to Pacific time if provided, otherwise use current Pacific time
    date_param = request.args.get('date')
    if date_param:
        date = datetime.strptime(date_param, '%Y-%m-%d').date()
    else:
        date = get_current_pacific_date()

    daily_plan = DailyPlan.query.filter_by(
        user_id=current_user.id,
        date=date
    ).first()

    # Get categories and their tasks for the time block selector
    categories = Category.query.filter_by(user_id=current_user.id).all()

    # Get calendar events for the selected date
    calendar_events = []
    if hasattr(current_user, 'credentials_info'):
        try:
            from calendar_service import get_calendar_events
            # Use selected calendars if available, otherwise default to primary
            selected_calendars = current_user.selected_calendars or ['primary']
            logger.debug(f"Fetching calendar events for user {current_user.id} with selected calendars: {selected_calendars}")
            calendar_events = get_calendar_events(
                current_user.credentials_info, 
                date,
                calendar_ids=selected_calendars
            )
            logger.debug(f"Retrieved {len(calendar_events)} calendar events")
        except Exception as e:
            logger.error(f"Error fetching calendar events: {str(e)}")
            flash("Could not fetch calendar events. Please try logging in again.", "warning")

    # If there's a daily plan, get its time blocks with task information
    time_blocks = []
    category_stats = {}
    total_minutes = 0

    if daily_plan:
        # Process time blocks and calculate statistics
        for block in daily_plan.time_blocks:
            time_blocks.append({
                'start_time': block.start_time.strftime('%H:%M'),
                'task_id': block.task_id,
                'completed': block.completed,
                'notes': block.notes
            })

            if block.task_id:
                task = Task.query.get(block.task_id)
                if task:
                    # Calculate minutes (each block is 15 minutes)
                    minutes = 15
                    total_minutes += minutes

                    # Update category statistics
                    if task.category_id not in category_stats:
                        category_stats[task.category_id] = {
                            'name': task.category.name,
                            'color': task.category.color,
                            'minutes': 0,
                        }
                    category_stats[task.category_id]['minutes'] += minutes

    # Format date for display in Pacific time
    formatted_date = date.strftime('%Y-%m-%d')

    return render_template('index.html', 
                         daily_plan=daily_plan, 
                         date=formatted_date, 
                         categories=categories,
                         time_blocks=time_blocks,
                         category_stats=category_stats,
                         total_minutes=total_minutes,
                         calendar_events=calendar_events)

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
            'color': task.category.color
        } for task in tasks])

    data = request.json
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        category_id=data['category_id'],
        user_id=current_user.id
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'category_id': task.category_id,
        'color': task.category.color
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
    db.session.commit()
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'category_id': task.category_id,
        'color': task.category.color
    })

@app.route('/api/daily-plan', methods=['POST'])
@login_required
def save_daily_plan():
    data = request.json
    # Convert date to Pacific time
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

    # Update time blocks with Pacific time and notes
    TimeBlock.query.filter_by(daily_plan_id=daily_plan.id).delete()
    for block in data.get('time_blocks', []):
        time_str = block['start_time']
        # Create time object in Pacific timezone
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        end_time = datetime.strptime(block['end_time'], '%H:%M').time()

        tb = TimeBlock(
            daily_plan_id=daily_plan.id,
            start_time=time_obj,
            end_time=end_time,
            task_id=block.get('task_id'),
            completed=block.get('completed', False),
            notes=block.get('notes', '')[:15]  # Limit notes to 15 characters
        )
        db.session.add(tb)

    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/summary')
@login_required
def summary():
    # Get the date range parameters
    period = request.args.get('period', '7')  # Default to 7 days
    days = int(period)
    end_date = datetime.now(pacific_tz).date()
    start_date = end_date - timedelta(days=days)

    # Query for all daily plans in the date range
    daily_plans = DailyPlan.query.filter(
        DailyPlan.user_id == current_user.id,
        DailyPlan.date >= start_date,
        DailyPlan.date <= end_date
    ).all()

    # Initialize statistics dictionaries
    category_stats = {}
    task_stats = {}
    total_minutes = 0

    # Calculate statistics
    for plan in daily_plans:
        for block in plan.time_blocks:
            if block.task_id:
                task = Task.query.get(block.task_id)
                if task:
                    # Each block is 15 minutes
                    minutes = 15
                    total_minutes += minutes

                    # Update task statistics
                    if task.id not in task_stats:
                        task_stats[task.id] = {
                            'title': task.title,
                            'minutes': 0,
                            'category_id': task.category_id,
                            'category_name': task.category.name,
                            'category_color': task.category.color
                        }
                    task_stats[task.id]['minutes'] += minutes

                    # Update category statistics
                    if task.category_id not in category_stats:
                        category_stats[task.category_id] = {
                            'name': task.category.name,
                            'color': task.category.color,
                            'minutes': 0,
                            'days_used': set()
                        }
                    category_stats[task.category_id]['minutes'] += minutes
                    category_stats[task.category_id]['days_used'].add(plan.date)

    # Calculate average daily hours for categories
    for cat_stats in category_stats.values():
        days_used = len(cat_stats['days_used'])
        cat_stats['avg_daily_minutes'] = cat_stats['minutes'] / (days_used if days_used > 0 else 1)
        del cat_stats['days_used']  # Remove set before passing to template

    return render_template('summary.html',
                         days=days,
                         start_date=start_date,
                         end_date=end_date,
                         category_stats=category_stats,
                         task_stats=task_stats,
                         total_minutes=total_minutes)

@app.route('/calendar/settings', methods=['GET', 'POST'])
@login_required
def calendar_settings():
    if request.method == 'POST':
        selected_ids = request.json.get('calendar_ids', [])
        current_user.selected_calendars = selected_ids
        db.session.commit()
        return jsonify({'status': 'success'})

    try:
        # Check if user has Google credentials
        if not hasattr(current_user, 'credentials_info'):
            logger.warning(f"User {current_user.id} missing Google credentials")
            flash("Please connect your Google account first", "warning")
            return redirect(url_for('google_auth.login'))

        logger.debug(f"Fetching calendar list for user {current_user.id}")
        from calendar_service import get_calendar_list
        calendars = get_calendar_list(current_user.credentials_info)

        if not calendars:
            logger.warning("No calendars found in response")
            flash("No calendars found. Please ensure you've granted calendar access.", "warning")
            return render_template('calendar_settings.html', 
                                calendars=[],
                                selected_calendars=[])

        logger.debug(f"Found {len(calendars)} calendars")
        return render_template('calendar_settings.html', 
                            calendars=calendars,
                            selected_calendars=current_user.selected_calendars or [])
    except Exception as e:
        logger.error(f"Error fetching calendar list: {str(e)}")
        flash("Could not fetch calendars. Please try logging in again.", "warning")
        return redirect(url_for('google_auth.login'))

with app.app_context():
    db.create_all()