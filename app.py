import os
import logging
import pytz
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, func
from cache_utils import init_cache, cached, invalidate_cache, get_paginated_results
from dateutil.rrule import rrule, rrulestr

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure timezone
pacific_tz = pytz.timezone('America/Los_Angeles')

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable resource-intensive event system
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,  # Recycle connections after 5 minutes
    "pool_pre_ping": True,  # Check connection validity before using it
    "pool_size": 2,  # Lower limit on max connections for cloud
    "max_overflow": 1,  # Reduce connections over pool_size 
    "pool_timeout": 20,  # Seconds to wait before timing out
    "connect_args": {
        "client_encoding": "utf8",
        "application_name": "timeblocker_replit",
        "connect_timeout": 10,
        "options": "-c default_transaction_isolation=read_committed"
    },
    "echo": False,  # Disable SQL query logging to reduce overhead
}

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize cache
init_cache(app)

# Set session lifetime (8 hours) for better user experience
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# Import routes after app initialization to avoid circular imports
from models import User, DailyPlan, Priority, TimeBlock, Category, Task, DayTemplate, ToDo, Role, TaskComment
from google_auth import google_auth

app.register_blueprint(google_auth)

# Set session to permanent but with defined lifetime
@app.before_request
def make_session_permanent():
    session.permanent = True
    # Marks the user's session as active to prevent premature disconnect
    if current_user.is_authenticated:
        session.modified = True

# Ensure database connections are properly closed after each request
@app.teardown_request
def cleanup_request(exception=None):
    db.session.close()
    if exception:
        db.session.rollback()
        logger.error(f"Request exception: {str(exception)}")

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

    # Get user's preferred start and end times, or use defaults
    day_start = current_user.day_start_time or datetime.strptime('09:00', '%H:%M').time()
    day_end = current_user.day_end_time or datetime.strptime('17:00', '%H:%M').time()

    # Get categories and their tasks for the time block selector
    categories = Category.query.filter_by(user_id=current_user.id).all()
    

    
    # Get all open tasks for the open tasks section, sorted by due date
    all_open_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.completed == False
    ).order_by(
        Task.due_date.asc().nullslast(),  # Due date ascending, nulls last
        Task.priority.desc()
    ).all()
    
    # Get all open todos sorted by due date
    all_todos = db.session.query(ToDo).filter(
        ToDo.user_id == current_user.id,
        ToDo.completed == False
    ).order_by(
        ToDo.due_date.asc().nullslast(),
        ToDo.priority.desc()
    ).all()
    
    # Get recurring todos specifically
    recurring_todos = db.session.query(ToDo).filter(
        ToDo.user_id == current_user.id,
        ToDo.is_recurring == True,
        ToDo.completed == False
    ).order_by(
        ToDo.next_occurrence.asc().nullslast(),
        ToDo.priority.desc()
    ).all()
    
    # Get all roles for filtering
    from models import Role
    all_roles = db.session.query(Role).filter(Role.user_id == current_user.id).all()



    # Initialize empty lists/dicts for data
    time_blocks = []
    category_stats = {}
    total_minutes = 0
    priorities = []
    brain_dump = ''
    productivity_rating = 0

    if daily_plan:
        # Load priorities
        priorities = [{
            'content': p.content,
            'completed': p.completed
        } for p in daily_plan.priorities]

        # Load brain dump and rating
        brain_dump = daily_plan.brain_dump or ''
        productivity_rating = daily_plan.productivity_rating or 0

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
                         priorities=priorities,
                         brain_dump=brain_dump,
                         productivity_rating=productivity_rating,
                         day_start=day_start,
                         day_end=day_end,
                         all_open_tasks=all_open_tasks,
                         all_todos=all_todos,
                         all_roles=all_roles,
                         recurring_todos=recurring_todos,
                         today=date)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/tasks')
@login_required
def tasks():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', categories=categories)

@app.route('/task-dashboard')
@login_required
def task_dashboard():
    """Enhanced task dashboard with robust tracking features"""
    return render_template('task_dashboard.html')

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
        # Get query parameters for filtering
        status = request.args.get('status')
        priority = request.args.get('priority')
        role_id = request.args.get('role_id')
        category_id = request.args.get('category_id')
        overdue_only = request.args.get('overdue') == 'true'
        
        query = Task.query.filter_by(user_id=current_user.id)
        
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if role_id:
            query = query.filter(Task.role_id == role_id)
        if category_id:
            query = query.filter(Task.category_id == category_id)
        if overdue_only:
            query = query.filter(Task.due_date < datetime.utcnow(), Task.completed == False)
        
        tasks = query.order_by(Task.created_at.desc()).all()
        
        return jsonify([{
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'category_id': task.category_id,
            'category_name': task.category.name,
            'category_color': task.category.color,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'status': task.status,
            'status_color': task.get_status_color(),
            'role_id': task.role_id,
            'role_name': task.assigned_role.name if task.assigned_role else None,
            'is_recurring': task.is_recurring,
            'recurrence_rule': task.recurrence_rule,
            'priority': task.priority,
            'priority_color': task.get_priority_color(),
            'completed': task.completed,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'estimated_minutes': task.estimated_minutes,
            'actual_minutes': task.actual_minutes,
            'total_time_spent': task.get_total_time_spent(),
            'notes': task.notes,
            'tags': task.tags or [],
            'dependencies': task.dependencies or [],
            'progress_percentage': task.progress_percentage,
            'last_worked_on': task.last_worked_on.isoformat() if task.last_worked_on else None,
            'parent_task_id': task.parent_task_id,
            'subtask_count': len(task.subtasks),
            'is_overdue': task.is_overdue(),
            'created_at': task.created_at.isoformat()
        } for task in tasks])

    data = request.json
    # Validate required fields
    if not data.get('title') or not data.get('category_id'):
        return jsonify({'error': 'Title and category are required'}), 400

    try:
        # Parse due_date if provided
        due_date = None
        if data.get('due_date'):
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            category_id=data['category_id'],
            user_id=current_user.id,
            due_date=due_date,
            status=data.get('status', 'pending'),
            role_id=data.get('role_id'),
            is_recurring=data.get('is_recurring', False),
            recurrence_rule=data.get('recurrence_rule'),
            priority=data.get('priority', 'medium'),
            estimated_minutes=data.get('estimated_minutes'),
            notes=data.get('notes', ''),
            tags=data.get('tags', []),
            dependencies=data.get('dependencies', []),
            parent_task_id=data.get('parent_task_id')
        )
        db.session.add(task)
        db.session.commit()

        return jsonify({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'category_id': task.category_id,
            'category_name': task.category.name,
            'category_color': task.category.color,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'status': task.status,
            'status_color': task.get_status_color(),
            'role_id': task.role_id,
            'is_recurring': task.is_recurring,
            'recurrence_rule': task.recurrence_rule,
            'priority': task.priority,
            'priority_color': task.get_priority_color(),
            'completed': task.completed,
            'estimated_minutes': task.estimated_minutes,
            'notes': task.notes,
            'tags': task.tags or [],
            'dependencies': task.dependencies or [],
            'progress_percentage': task.progress_percentage,
            'parent_task_id': task.parent_task_id,
            'created_at': task.created_at.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({'error': 'Failed to create task'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
@login_required
def task_operations(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return '', 204

    data = request.json
    
    # Update basic fields
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.category_id = data.get('category_id', task.category_id)
    
    # Update enhanced tracking fields
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')) if data['due_date'] else None
    
    task.status = data.get('status', task.status)
    task.role_id = data.get('role_id', task.role_id)
    task.is_recurring = data.get('is_recurring', task.is_recurring)
    task.recurrence_rule = data.get('recurrence_rule', task.recurrence_rule)
    task.priority = data.get('priority', task.priority)
    task.estimated_minutes = data.get('estimated_minutes', task.estimated_minutes)
    task.actual_minutes = data.get('actual_minutes', task.actual_minutes)
    task.notes = data.get('notes', task.notes)
    task.tags = data.get('tags', task.tags)
    task.dependencies = data.get('dependencies', task.dependencies)
    task.progress_percentage = data.get('progress_percentage', task.progress_percentage)
    task.parent_task_id = data.get('parent_task_id', task.parent_task_id)
    
    # Handle completion status
    if 'completed' in data:
        task.completed = data['completed']
        if data['completed'] and not task.completed_at:
            task.completed_at = datetime.utcnow()
            task.status = 'completed'
        elif not data['completed']:
            task.completed_at = None
            if task.status == 'completed':
                task.status = 'pending'
    
    # Update last worked on timestamp if task is being modified
    task.last_worked_on = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'category_id': task.category_id,
        'category_name': task.category.name,
        'category_color': task.category.color,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'status': task.status,
        'status_color': task.get_status_color(),
        'role_id': task.role_id,
        'role_name': task.assigned_role.name if task.assigned_role else None,
        'is_recurring': task.is_recurring,
        'recurrence_rule': task.recurrence_rule,
        'priority': task.priority,
        'priority_color': task.get_priority_color(),
        'completed': task.completed,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None,
        'estimated_minutes': task.estimated_minutes,
        'actual_minutes': task.actual_minutes,
        'total_time_spent': task.get_total_time_spent(),
        'notes': task.notes,
        'tags': task.tags or [],
        'dependencies': task.dependencies or [],
        'progress_percentage': task.progress_percentage,
        'last_worked_on': task.last_worked_on.isoformat() if task.last_worked_on else None,
        'parent_task_id': task.parent_task_id,
        'subtask_count': len(task.subtasks),
        'is_overdue': task.is_overdue(),
        'created_at': task.created_at.isoformat()
    })

# Role Management API Endpoints
@app.route('/api/roles', methods=['GET', 'POST'])
@login_required
def manage_roles():
    if request.method == 'GET':
        roles = Role.query.filter_by(user_id=current_user.id).order_by(Role.created_at.desc()).all()
        return jsonify([{
            'id': role.id,
            'name': role.name,
            'color': role.color,
            'description': role.description,
            'task_count': len(role.tasks),
            'created_at': role.created_at.isoformat()
        } for role in roles])
    
    data = request.json
    if not data.get('name'):
        return jsonify({'error': 'Role name is required'}), 400
    
    try:
        role = Role(
            name=data['name'],
            color=data.get('color', '#6c757d'),
            description=data.get('description', ''),
            user_id=current_user.id
        )
        db.session.add(role)
        db.session.commit()
        
        return jsonify({
            'id': role.id,
            'name': role.name,
            'color': role.color,
            'description': role.description,
            'task_count': 0,
            'created_at': role.created_at.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating role: {str(e)}")
        return jsonify({'error': 'Failed to create role'}), 500

@app.route('/api/roles/<int:role_id>', methods=['PUT', 'DELETE'])
@login_required
def role_operations(role_id):
    role = Role.query.filter_by(id=role_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'DELETE':
        # Update tasks to remove role assignment before deleting role
        Task.query.filter_by(role_id=role.id).update({'role_id': None})
        db.session.delete(role)
        db.session.commit()
        return '', 204
    
    data = request.json
    role.name = data.get('name', role.name)
    role.color = data.get('color', role.color)
    role.description = data.get('description', role.description)
    db.session.commit()
    
    return jsonify({
        'id': role.id,
        'name': role.name,
        'color': role.color,
        'description': role.description,
        'task_count': len(role.tasks),
        'created_at': role.created_at.isoformat()
    })

# Task Analytics and Reporting Endpoints
@app.route('/api/tasks/analytics')
@login_required
def task_analytics():
    """Get task analytics and statistics"""
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    
    analytics = {
        'total_tasks': len(tasks),
        'completed_tasks': len([t for t in tasks if t.completed]),
        'pending_tasks': len([t for t in tasks if t.status == 'pending']),
        'in_progress_tasks': len([t for t in tasks if t.status == 'in_progress']),
        'blocked_tasks': len([t for t in tasks if t.status == 'blocked']),
        'overdue_tasks': len([t for t in tasks if t.is_overdue()]),
        'priority_breakdown': {
            'urgent': len([t for t in tasks if t.priority == 'urgent']),
            'high': len([t for t in tasks if t.priority == 'high']),
            'medium': len([t for t in tasks if t.priority == 'medium']),
            'low': len([t for t in tasks if t.priority == 'low'])
        },
        'total_estimated_hours': sum([t.estimated_minutes or 0 for t in tasks]) / 60,
        'total_actual_hours': sum([t.actual_minutes or 0 for t in tasks]) / 60,
        'total_tracked_hours': sum([t.get_total_time_spent() for t in tasks]) / 60,
        'completion_rate': (len([t for t in tasks if t.completed]) / len(tasks) * 100) if tasks else 0
    }
    
    return jsonify(analytics)

@app.route('/api/tasks/<int:task_id>/comments', methods=['GET', 'POST'])
@login_required
def task_comments(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'GET':
        comments = TaskComment.query.filter_by(task_id=task_id).order_by(TaskComment.created_at.desc()).all()
        return jsonify([{
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat()
        } for comment in comments])
    
    data = request.json
    if not data.get('content'):
        return jsonify({'error': 'Comment content is required'}), 400
    
    try:
        comment = TaskComment(
            task_id=task_id,
            user_id=current_user.id,
            content=data['content']
        )
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating comment: {str(e)}")
        return jsonify({'error': 'Failed to create comment'}), 500

@app.route('/api/tasks/<int:task_id>/progress', methods=['PUT'])
@login_required
def update_task_progress(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    data = request.json
    progress = data.get('progress_percentage', 0)
    
    if not 0 <= progress <= 100:
        return jsonify({'error': 'Progress must be between 0 and 100'}), 400
    
    task.progress_percentage = progress
    task.last_worked_on = datetime.utcnow()
    
    # Auto-update status based on progress
    if progress == 0:
        task.status = 'pending'
    elif progress == 100:
        task.status = 'completed'
        task.completed = True
        task.completed_at = datetime.utcnow()
    elif progress > 0:
        task.status = 'in_progress'
    
    db.session.commit()
    
    return jsonify({
        'id': task.id,
        'progress_percentage': task.progress_percentage,
        'status': task.status,
        'last_worked_on': task.last_worked_on.isoformat()
    })

@app.route('/api/daily-plan/backup', methods=['GET'])
@login_required
def get_daily_plan_backup():
    """Get backup data for a specific date."""
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Date parameter required'}), 400
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get all daily plans for the last 7 days for potential recovery
        end_date = date
        start_date = date - timedelta(days=6)
        
        daily_plans = DailyPlan.query.filter(
            DailyPlan.user_id == current_user.id,
            DailyPlan.date >= start_date,
            DailyPlan.date <= end_date
        ).order_by(DailyPlan.date.desc()).all()
        
        backup_data = []
        for plan in daily_plans:
            plan_data = {
                'date': plan.date.strftime('%Y-%m-%d'),
                'updated_at': plan.updated_at.isoformat(),
                'priorities': [{'content': p.content, 'completed': p.completed} for p in plan.priorities],
                'time_blocks': [{
                    'start_time': block.start_time.strftime('%H:%M'),
                    'task_id': block.task_id,
                    'notes': block.notes
                } for block in plan.time_blocks],
                'brain_dump': plan.brain_dump,
                'productivity_rating': plan.productivity_rating
            }
            backup_data.append(plan_data)
        
        return jsonify({'success': True, 'backup_data': backup_data})
        
    except Exception as e:
        logger.error(f"Error getting backup data: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get backup data'}), 500

@app.route('/api/restore-today-plan', methods=['POST'])
@login_required
def restore_today_plan():
    """Restore today's plan from existing database data."""
    try:
        today = get_current_pacific_date()
        
        # Find existing daily plan for today
        daily_plan = DailyPlan.query.filter_by(
            user_id=current_user.id,
            date=today
        ).first()
        
        if not daily_plan:
            return jsonify({'success': False, 'message': 'No plan found for today'})
        
        # Count existing data
        priorities_count = len(daily_plan.priorities)
        time_blocks_count = len([b for b in daily_plan.time_blocks if b.task_id])
        
        if priorities_count == 0 and time_blocks_count == 0:
            return jsonify({'success': False, 'message': 'No data to restore'})
        
        # The data is already in the database, just return success
        # The page will reload and display the existing data
        return jsonify({
            'success': True,
            'priorities_count': priorities_count,
            'time_blocks_count': time_blocks_count,
            'message': f'Found {priorities_count} priorities and {time_blocks_count} scheduled blocks'
        })
        
    except Exception as e:
        logger.error(f"Error restoring today's plan: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to restore plan'}), 500

@app.route('/api/daily-plan', methods=['POST'])
@login_required
def save_daily_plan():
    """Update user's daily plan with conflict detection."""
    data = request.json
    # Convert date to Pacific time
    date = datetime.strptime(data['date'], '%Y-%m-%d').date()

    daily_plan = DailyPlan.query.filter_by(
        user_id=current_user.id,
        date=date
    ).first()
    
    # Check for conflicts if plan exists
    if daily_plan and 'last_update_check' in data:
        last_check = datetime.fromisoformat(data['last_update_check'].replace('Z', '+00:00'))
        # Make both datetimes timezone-aware for comparison
        if daily_plan.updated_at.replace(tzinfo=last_check.tzinfo if last_check.tzinfo else None) > last_check:
            return jsonify({
                'success': False,
                'conflict': True,
                'message': 'Data was modified on another device. Please refresh to see latest changes.',
                'server_updated_at': daily_plan.updated_at.isoformat()
            }), 409

    if not daily_plan:
        daily_plan = DailyPlan(user_id=current_user.id, date=date)
        db.session.add(daily_plan)

    # Update basic fields only if provided
    if 'productivity_rating' in data:
        daily_plan.productivity_rating = data.get('productivity_rating')
    if 'brain_dump' in data:
        daily_plan.brain_dump = data.get('brain_dump')

    # Handle priorities - preserve existing ones if this is just carrying over incomplete priorities
    if data.get('priorities'):
        existing_priorities = {p.content.strip(): p for p in daily_plan.priorities}
        # Only delete existing priorities if we're doing a full save, not when carrying over
        if len(data.get('time_blocks', [])) > 0:  # Full save
            Priority.query.filter_by(daily_plan_id=daily_plan.id).delete()
            existing_priorities = {}

        # Add new priorities
        for i, priority_data in enumerate(data.get('priorities', [])):
            content = priority_data.get('content', '').strip()
            if content and content not in existing_priorities:
                priority = Priority(
                    daily_plan_id=daily_plan.id,
                    content=content,
                    order=len(existing_priorities) + i,
                    completed=priority_data.get('completed', False)
                )
                db.session.add(priority)

    # Handle time blocks - only update if explicitly provided with data
    if data.get('time_blocks'):
        TimeBlock.query.filter_by(daily_plan_id=daily_plan.id).delete()
        for block_data in data.get('time_blocks', []):
            # Validate that both start_time and end_time exist
            if not block_data.get('start_time') or not block_data.get('end_time'):
                logger.warning(f"Skipping time block with missing time data: {block_data}")
                continue
                
            try:
                time_block = TimeBlock(
                    daily_plan_id=daily_plan.id,
                    start_time=datetime.strptime(block_data['start_time'], '%H:%M').time(),
                    end_time=datetime.strptime(block_data['end_time'], '%H:%M').time(),
                    task_id=block_data.get('task_id'),
                    completed=block_data.get('completed', False),
                    notes=block_data.get('notes', '')[:15]  # Ensure notes don't exceed 15 chars
                )
                db.session.add(time_block)
            except (ValueError, KeyError) as e:
                logger.error(f"Error processing time block {block_data}: {str(e)}")
                continue

    try:
        db.session.commit()
        last_saved = datetime.now(pacific_tz).strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'status': 'success', 'last_saved': last_saved})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving daily plan: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/summary')
@login_required
def summary():
    # Get the date range parameters
    period = request.args.get('period', '7')  # Default to 7 days
    days = int(period)
    end_date = datetime.now(pacific_tz).date()
    start_date = end_date - timedelta(days=days-1)

    # Query for all daily plans in the date range
    daily_plans = DailyPlan.query.filter(
        DailyPlan.user_id == current_user.id,
        DailyPlan.date >= start_date,
        DailyPlan.date <= end_date
    ).all()

    # Initialize statistics dictionaries
    category_stats = {}
    task_stats = {}
    daily_category_breakdown = {}
    total_minutes = 0

    # Get all dates in range for consistent daily breakdown
    all_dates = []
    current_date = start_date
    while current_date <= end_date:
        all_dates.append(current_date)
        current_date += timedelta(days=1)

    # Calculate statistics
    for plan in daily_plans:
        plan_date = plan.date
        if plan_date not in daily_category_breakdown:
            daily_category_breakdown[plan_date] = {}
            
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

                    # Update daily category breakdown
                    if task.category_id not in daily_category_breakdown[plan_date]:
                        daily_category_breakdown[plan_date][task.category_id] = {
                            'name': task.category.name,
                            'color': task.category.color,
                            'minutes': 0
                        }
                    daily_category_breakdown[plan_date][task.category_id]['minutes'] += minutes

    # Calculate average daily hours for categories
    for cat_stats in category_stats.values():
        days_used = len(cat_stats['days_used'])
        cat_stats['avg_daily_minutes'] = cat_stats['minutes'] / (days_used if days_used > 0 else 1)
        del cat_stats['days_used']  # Remove set before passing to template

    # Prepare daily breakdown for template (convert to list format)
    daily_breakdown_list = []
    for date in sorted(all_dates, reverse=True):  # Most recent first
        day_data = {
            'date': date,
            'categories': daily_category_breakdown.get(date, {}),
            'total_minutes': sum(cat['minutes'] for cat in daily_category_breakdown.get(date, {}).values())
        }
        daily_breakdown_list.append(day_data)

    return render_template('summary.html',
                         days=days,
                         start_date=start_date,
                         end_date=end_date,
                         category_stats=category_stats,
                         task_stats=task_stats,
                         total_minutes=total_minutes,
                         daily_breakdown=daily_breakdown_list)



@app.route('/health')
def health_check():
    """Health check endpoint to verify server status."""
    try:
        # Check if we can access the database
        db.session.execute(text('SELECT 1'))
        # Check if environment variables are set
        nylas_configured = bool(os.environ.get('NYLAS_CLIENT_ID') and os.environ.get('NYLAS_CLIENT_SECRET'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'nylas_configured': nylas_configured
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# Navigation links functionality removed - simplified navigation

@app.route('/api/templates', methods=['POST'])
@login_required
def save_template():
    """Save the current day's plan as a template."""
    data = request.json
    template_name = data.get('name')

    if not template_name:
        return jsonify({'error': 'Template name is required'}), 400

    existing_template = DayTemplate.query.filter_by(
        name=template_name, 
        user_id=current_user.id
    ).first()

    if existing_template:
        return jsonify({'error': 'Template with this name already exists'}), 400

    new_template = DayTemplate(
        name=template_name,
        user_id=current_user.id,
        priorities=data.get('priorities', []),
        time_blocks=data.get('time_blocks', [])
    )
    db.session.add(new_template)
    db.session.commit()

    return jsonify({'message': 'Template saved successfully'}), 200

@app.route('/api/templates', methods=['GET'])
@login_required
def get_templates():
    """Fetch all saved templates for the user."""
    templates = DayTemplate.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': t.id, 
        'name': t.name,
        'created_at': t.created_at.isoformat()
    } for t in templates])

@app.route('/api/templates/<int:template_id>', methods=['GET'])
@login_required
def get_template(template_id):
    """Retrieve a specific template's details."""
    template = DayTemplate.query.filter_by(
        id=template_id, 
        user_id=current_user.id
    ).first_or_404()

    return jsonify({
        'id': template.id,
        'name': template.name,
        'priorities': template.priorities,
        'time_blocks': template.time_blocks
    })

@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
@login_required
def delete_template(template_id):
    """Delete a saved template."""
    template = DayTemplate.query.filter_by(
        id=template_id, 
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(template)
    db.session.commit()
    return jsonify({'message': 'Template deleted successfully'}), 200

@app.route('/api/apply-template', methods=['POST'])
@login_required
def apply_template():
    """Apply a saved template to a selected date."""
    data = request.json
    template_id = data.get('template_id')
    date_str = data.get('date')

    if not template_id or not date_str:
        return jsonify({'error': 'Template ID and date are required'}), 400

    template = DayTemplate.query.filter_by(
        id=template_id, 
        user_id=current_user.id
    ).first_or_404()

    # Convert date string to date object
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    # Check if there's already a daily plan for this date
    daily_plan = DailyPlan.query.filter_by(
        user_id=current_user.id, 
        date=date
    ).first()

    if not daily_plan:
        daily_plan = DailyPlan(user_id=current_user.id, date=date)
        db.session.add(daily_plan)

    # Clear existing priorities and time blocks
    Priority.query.filter_by(daily_plan_id=daily_plan.id).delete()
    TimeBlock.query.filter_by(daily_plan_id=daily_plan.id).delete()

    # Apply template priorities
    for i, priority_data in enumerate(template.priorities or []):
        if priority_data.get('content', '').strip():
            priority = Priority(
                daily_plan_id=daily_plan.id,
                content=priority_data['content'],
                order=i,
                completed=False  # Start fresh with uncompleted priorities
            )
            db.session.add(priority)

    # Apply template time blocks
    for block_data in template.time_blocks or []:
        if block_data.get('start_time'):
            time_block = TimeBlock(
                daily_plan_id=daily_plan.id,
                start_time=datetime.strptime(block_data['start_time'], '%H:%M').time(),
                end_time=datetime.strptime(block_data['end_time'], '%H:%M').time(),
                task_id=block_data.get('task_id'),
                completed=False,  # Start fresh with uncompleted blocks
                notes=block_data.get('notes', '')[:15]  # Maintain the 15-char limit
            )
            db.session.add(time_block)

    try:
        db.session.commit()
        return jsonify({'message': 'Template applied successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error applying template: {str(e)}")
        return jsonify({'error': 'Failed to apply template'}), 500

def generate_embed_token(user_id):
    """Generate a secure token for embedded views."""
    token = secrets.token_urlsafe(32)
    # Store token in session with expiry (180 days)
    if 'embed_tokens' not in session:
        session['embed_tokens'] = {}
    session['embed_tokens'][token] = {
        'user_id': user_id,
        'expires': (datetime.utcnow() + timedelta(days=180)).timestamp()
    }
    return token

def validate_embed_token(token):
    """Validate an embed token and return the associated user_id."""
    if not token or 'embed_tokens' not in session:
        return None

    token_data = session['embed_tokens'].get(token)
    if not token_data:
        return None

    # Check if token has expired
    if datetime.utcnow().timestamp() > token_data['expires']:
        del session['embed_tokens'][token]
        return None

    return token_data['user_id']

def embed_auth_required(f):
    """Decorator for routes that need embed authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')
        user_id = validate_embed_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Log in the user for this request
        login_user(user)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/embed/generate_token')
@login_required
def generate_embed_token_route():
    """Generate a new embed token for the current user."""
    token = generate_embed_token(current_user.id)
    return jsonify({'token': token})

@app.route('/embed/<path:subpath>')
@embed_auth_required
def embedded_view(subpath):
    """Handle embedded views with token authentication."""
    if subpath == 'tasks':
        return render_template('tasks.html', 
                            categories=Category.query.filter_by(user_id=current_user.id).all(),
                            embedded=True)
    else:
        return 'Invalid embed path', 404


# Add these routes after the existing routes
@app.route('/time-preferences')
@login_required
def time_preferences():
    """Show time preferences page."""
    return render_template('time_preferences.html')

@app.route('/api/seven-day-stats', methods=['GET'])
@login_required
def get_seven_day_stats():
    """Get 7-day time statistics for the current user, ending on the specified date."""
    try:
        # Get the end date from the request, default to today if not provided
        date_str = request.args.get('date')
        if date_str:
            end_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            end_date = datetime.now(pacific_tz).date()

        # Calculate date range for the 7 days ending on end_date
        start_date = end_date - timedelta(days=6)
        
        # Query for all daily plans in the date range
        daily_plans = DailyPlan.query.filter(
            DailyPlan.user_id == current_user.id,
            DailyPlan.date >= start_date,
            DailyPlan.date <= end_date
        ).all()
        
        # Initialize statistics
        total_minutes = 0
        aps_minutes = 0
        category_stats = {}
        
        # Calculate statistics from time blocks
        for plan in daily_plans:
            for block in plan.time_blocks:
                if block.task_id:
                    task = Task.query.get(block.task_id)
                    if task and task.category:
                        # Each block is 15 minutes
                        minutes = 15
                        total_minutes += minutes
                        
                        # Check if this is APS/Work category
                        if task.category.name.lower() in ['aps', 'work']:
                            aps_minutes += minutes
                        
                        # Update category statistics
                        category_name = task.category.name
                        if category_name not in category_stats:
                            category_stats[category_name] = {
                                'name': category_name,
                                'color': task.category.color,
                                'minutes': 0
                            }
                        category_stats[category_name]['minutes'] += minutes
        
        # Calculate progress percentage for APS goal (32 hours = 1920 minutes)
        aps_goal_minutes = 32 * 60  # 32 hours in minutes
        aps_progress_percentage = min((aps_minutes / aps_goal_minutes) * 100, 100) if aps_goal_minutes > 0 else 0
        
        return jsonify({
            'success': True,
            'total_hours': round(total_minutes / 60, 1),
            'aps_hours': round(aps_minutes / 60, 1),
            'aps_progress_percentage': round(aps_progress_percentage, 1),
            'category_stats': list(category_stats.values()),
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching 7-day stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch 7-day statistics'
        }), 500

@app.route('/api/time-preferences', methods=['POST'])
@login_required
def update_time_preferences():
    """Update user's time preferences."""
    data = request.json
    try:
        # Parse and validate the times
        start_time = datetime.strptime(data['day_start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['day_end_time'], '%H:%M').time()
        split_time = datetime.strptime(data['day_split_time'], '%H:%M').time()

        # Update user preferences
        current_user.day_start_time = start_time
        current_user.day_end_time = end_time
        current_user.day_split_time = split_time
        db.session.commit()

        return jsonify({'message': 'Preferences updated successfully'})
    except Exception as e:
        logger.error(f"Error updating time preferences: {str(e)}")
        return jsonify({'error': 'Failed to update preferences'}), 500

# ToDo Management Endpoints
@app.route('/api/todos', methods=['GET'])
@login_required
def get_todos():
    """Get all todos for the current user."""
    todos = db.session.query(ToDo).filter(
        ToDo.user_id == current_user.id,
        ToDo.completed == False
    ).order_by(
        ToDo.due_date.asc().nullslast(),
        ToDo.priority.desc()
    ).all()
    
    todo_list = []
    for todo in todos:
        todo_data = {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'priority': todo.priority,
            'status': todo.status,
            'due_date': todo.due_date.isoformat() if todo.due_date else None,
            'is_recurring': todo.is_recurring,
            'recurrence_rule': todo.recurrence_rule,
            'role_id': todo.role_id,
            'role_name': todo.assigned_role.name if todo.assigned_role else None,
            'is_overdue': todo.is_overdue(),
            'created_at': todo.created_at.isoformat()
        }
        todo_list.append(todo_data)
    
    return jsonify({'todos': todo_list})

@app.route('/api/todos', methods=['POST'])
@login_required
def create_todo():
    """Create a new todo."""
    data = request.get_json()
    
    try:
        # Parse due date if provided
        due_date = None
        if data.get('due_date'):
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        
        todo = ToDo(
            title=data['title'],
            description=data.get('description', ''),
            user_id=current_user.id,
            role_id=data.get('role_id'),
            due_date=due_date,
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'todo'),
            is_recurring=data.get('is_recurring', False),
            recurrence_rule=data.get('recurrence_rule')
        )
        
        db.session.add(todo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Todo created successfully',
            'todo_id': todo.id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating todo: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to create todo'
        }), 500

@app.route('/api/todos/<int:todo_id>/complete', methods=['POST'])
@login_required
def complete_todo(todo_id):
    """Mark a todo as completed and create next occurrence if recurring."""
    todo = db.session.query(ToDo).filter(
        ToDo.id == todo_id,
        ToDo.user_id == current_user.id
    ).first()
    
    if not todo:
        return jsonify({'success': False, 'message': 'Todo not found'}), 404
    
    try:
        # Mark current todo as completed
        todo.completed = True
        todo.completed_at = datetime.utcnow()
        todo.status = 'completed'
        todo.updated_at = datetime.utcnow()
        
        # If it's recurring, create the next occurrence
        if todo.is_recurring and todo.recurrence_rule:
            next_due = calculate_next_due_date(todo.due_date, todo.recurrence_rule)
            if next_due:
                new_todo = ToDo(
                    title=todo.title,
                    description=todo.description,
                    user_id=todo.user_id,
                    role_id=todo.role_id,
                    due_date=next_due,
                    priority=todo.priority,
                    status='todo',
                    is_recurring=True,
                    recurrence_rule=todo.recurrence_rule,
                    next_occurrence=next_due
                )
                db.session.add(new_todo)
                # Pass back the next occurrence info
                result = {
                    'success': True,
                    'message': 'Todo marked as completed and next occurrence created',
                    'next_occurrence': new_todo.next_occurrence.isoformat()
                }
        else:
            result = {
                'success': True,
                'message': 'Todo marked as completed'
            }
        
        db.session.commit()
        return jsonify(result)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error completing todo {todo_id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

def calculate_next_due_date(current_due_date, recurrence_rule):
    """
    Calculates the next due date based on an iCalendar RRULE string.
    """
    if not current_due_date:
        current_due_date = datetime.utcnow()

    try:
        # Ensure the start date for the rule is the current due date
        rule = rrulestr(recurrence_rule, dtstart=current_due_date)
        # Get the next occurrence after the current due date
        next_date = rule.after(current_due_date)
        return next_date
    except Exception as e:
        logger.error(f"Error parsing recurrence rule '{recurrence_rule}': {e}")
        return None

@app.route('/api/import-todos', methods=['POST'])
@login_required
def import_todos():
    """Import todos from the provided list."""
    from models import Role
    
    # Get or create roles
    aps_role = db.session.query(Role).filter(Role.user_id == current_user.id, Role.name == 'APS').first()
    if not aps_role:
        aps_role = Role(name='APS', user_id=current_user.id, color='#007bff', description='APS work tasks')
        db.session.add(aps_role)
        db.session.flush()
    
    home_role = db.session.query(Role).filter(Role.user_id == current_user.id, Role.name == 'Home').first()
    if not home_role:
        home_role = Role(name='Home', user_id=current_user.id, color='#28a745', description='Personal tasks')
        db.session.add(home_role)
        db.session.flush()
    
    church_role = db.session.query(Role).filter(Role.user_id == current_user.id, Role.name == 'Church').first()
    if not church_role:
        church_role = Role(name='Church', user_id=current_user.id, color='#6f42c1', description='Church tasks')
        db.session.add(church_role)
        db.session.flush()
    
    # Todo items from the document
    todo_items = [
        {"title": "SSO Entra with QuickBase", "priority": "medium", "due_date": "2025-05-22", "role": "APS"},
        {"title": "Linkedin Post Complete", "priority": "low", "due_date": "2025-05-31", "role": "Home", "recurring": True, "recurrence": "FREQ=WEEKLY"},
        {"title": "Setup PC to transfer images from S3, resize, and transfer to Sharepoint", "priority": "medium", "due_date": "2025-05-31", "role": "APS", "description": "Fotosizer resize"},
        {"title": "Brett's Request for C&D Pos Report", "priority": "medium", "due_date": "2025-06-05", "role": "APS"},
        {"title": "Daily Doctrine for the Week PP", "priority": "medium", "due_date": "2025-06-05", "role": "Home", "recurring": True, "recurrence": "FREQ=WEEKLY"},
        {"title": "Prep for Budget Presentation", "priority": "medium", "due_date": "2025-06-06", "role": "Church"},
        {"title": "Bible Biography PP", "priority": "medium", "due_date": "2025-06-07", "role": "Home", "recurring": True, "recurrence": "FREQ=WEEKLY"},
        {"title": "Test Sharepoint shortcut on PC once setup", "priority": "medium", "due_date": "2025-06-07", "role": "APS"},
        {"title": "Review EPM Monthly Report Process", "priority": "medium", "due_date": "2025-06-12", "role": "APS"},
        {"title": "Add July Tozer", "priority": "low", "due_date": "2025-06-14", "role": "Home"},
        {"title": "Add July Drucker", "priority": "low", "due_date": "2025-06-14", "role": "Home"},
        {"title": "Prep Agendas and Schedule Meeting with Jeff", "priority": "medium", "due_date": "2025-06-24", "role": "Church", "recurring": True, "recurrence": "FREQ=MONTHLY"},
        {"title": "Checkin", "priority": "medium", "due_date": "2025-07-10", "role": "Home", "recurring": True, "recurrence": "FREQ=MONTHLY"},
        {"title": "Add August Drucker", "priority": "low", "due_date": "2025-07-14", "role": "Home"},
        {"title": "Add August Tozer", "priority": "low", "due_date": "2025-07-14", "role": "Home"},
        {"title": "Add Sept Tozer", "priority": "low", "due_date": "2025-08-14", "role": "Home"},
        {"title": "Add Sept Drucker", "priority": "low", "due_date": "2025-08-14", "role": "Home"},
        {"title": "Add Oct Tozer", "priority": "low", "due_date": "2025-09-14", "role": "Home"},
        {"title": "Add Oct Drucker", "priority": "low", "due_date": "2025-09-14", "role": "Home"},
        {"title": "Tech Wage Review", "priority": "low", "due_date": "2025-09-15", "role": "APS", "recurring": True, "recurrence": "FREQ=MONTHLY;INTERVAL=6"},
        {"title": "Add Nov Drucker", "priority": "low", "due_date": "2025-10-14", "role": "Home"},
        {"title": "Add Nov Tozer", "priority": "low", "due_date": "2025-10-14", "role": "Home"},
        {"title": "Add Jan Drucker", "priority": "low", "due_date": "2025-11-14", "role": "Home"},
        {"title": "Add Dec Drucker", "priority": "low", "due_date": "2025-11-14", "role": "Home"},
        {"title": "Add Dec Tozer", "priority": "low", "due_date": "2025-11-14", "role": "Home"},
        {"title": "Add Jan Tozer", "priority": "low", "due_date": "2025-12-14", "role": "Home"},
        {"title": "Jason S Vendor Contacts", "priority": "medium", "role": "APS", "description": "Planning"},
        {"title": "Sales by market on PowerBI", "priority": "medium", "role": "APS", "description": "Development"},
        {"title": "Service New Orders Box", "priority": "medium", "role": "APS", "description": "Development"}
    ]
    
    try:
        role_map = {
            'APS': aps_role.id,
            'Home': home_role.id,
            'Church': church_role.id
        }
        
        for item in todo_items:
            # Skip if todo already exists
            existing = db.session.query(ToDo).filter(
                ToDo.user_id == current_user.id,
                ToDo.title == item['title']
            ).first()
            
            if existing:
                continue
            
            due_date = None
            if item.get('due_date'):
                due_date = datetime.strptime(item['due_date'], '%Y-%m-%d')
            
            todo = ToDo(
                title=item['title'],
                description=item.get('description', ''),
                user_id=current_user.id,
                role_id=role_map.get(item['role']),
                due_date=due_date,
                priority=item['priority'],
                status='todo',
                is_recurring=item.get('recurring', False),
                recurrence_rule=item.get('recurrence')
            )
            
            db.session.add(todo)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Todos imported successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error importing todos: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to import todos'
        }), 500

# Enhanced Time Tracking Analytics
@app.route('/api/time-analytics', methods=['GET'])
@login_required
def get_time_analytics():
    """Get comprehensive time tracking analytics"""
    # Get date range from request
    days = int(request.args.get('days', 30))
    end_date = datetime.now(pacific_tz).date()
    start_date = end_date - timedelta(days=days)
    
    # Query daily plans in range
    daily_plans = DailyPlan.query.filter(
        DailyPlan.user_id == current_user.id,
        DailyPlan.date >= start_date,
        DailyPlan.date <= end_date
    ).all()
    
    analytics = {
        'total_hours': 0,
        'productive_hours': 0,
        'category_breakdown': {},
        'daily_patterns': {},
        'weekly_patterns': {},
        'most_productive_hours': {},
        'completion_rates': {},
        'time_distribution': {}
    }
    
    # Calculate analytics
    for plan in daily_plans:
        day_total = 0
        for block in plan.time_blocks:
            if block.task_id and block.completed:
                minutes = 15
                analytics['total_hours'] += minutes / 60
                day_total += minutes / 60
                
                # Get task and category info
                task = Task.query.get(block.task_id)
                if task:
                    category_name = task.category.name
                    
                    # Category breakdown
                    if category_name not in analytics['category_breakdown']:
                        analytics['category_breakdown'][category_name] = {
                            'hours': 0,
                            'color': task.category.color,
                            'completion_rate': 0,
                            'total_blocks': 0,
                            'completed_blocks': 0
                        }
                    
                    analytics['category_breakdown'][category_name]['hours'] += minutes / 60
                    analytics['category_breakdown'][category_name]['total_blocks'] += 1
                    analytics['category_breakdown'][category_name]['completed_blocks'] += 1
                    
                    # Hourly productivity
                    hour = block.start_time.hour
                    if hour not in analytics['most_productive_hours']:
                        analytics['most_productive_hours'][hour] = 0
                    analytics['most_productive_hours'][hour] += 1
        
        # Daily patterns
        day_name = plan.date.strftime('%A')
        if day_name not in analytics['daily_patterns']:
            analytics['daily_patterns'][day_name] = {'total_hours': 0, 'days_counted': 0}
        analytics['daily_patterns'][day_name]['total_hours'] += day_total
        analytics['daily_patterns'][day_name]['days_counted'] += 1
    
    # Calculate averages and percentages
    for category in analytics['category_breakdown'].values():
        if category['total_blocks'] > 0:
            category['completion_rate'] = (category['completed_blocks'] / category['total_blocks']) * 100
    
    for day in analytics['daily_patterns'].values():
        if day['days_counted'] > 0:
            day['average_hours'] = day['total_hours'] / day['days_counted']
    
    return jsonify(analytics)

@app.route('/api/productivity-insights', methods=['GET'])
@login_required
def get_productivity_insights():
    """Get personalized productivity insights"""
    # Get user's most productive times
    productive_hours = get_productive_hours(current_user.id)
    
    # Get category performance
    categories = Category.query.filter_by(user_id=current_user.id).all()
    category_performance = []
    
    for category in categories:
        tasks = Task.query.filter_by(category_id=category.id, user_id=current_user.id).all()
        completed_tasks = [t for t in tasks if t.completed]
        
        category_performance.append({
            'name': category.name,
            'color': category.color,
            'total_tasks': len(tasks),
            'completed_tasks': len(completed_tasks),
            'completion_rate': (len(completed_tasks) / len(tasks) * 100) if tasks else 0,
            'avg_time_spent': sum(t.get_total_time_spent() for t in tasks) / len(tasks) if tasks else 0
        })
    
    # Get time estimation accuracy
    tasks_with_estimates = Task.query.filter(
        Task.user_id == current_user.id,
        Task.estimated_minutes.isnot(None),
        Task.actual_minutes.isnot(None),
        Task.completed == True
    ).all()
    
    estimation_accuracy = 0
    if tasks_with_estimates:
        total_error = 0
        for task in tasks_with_estimates:
            error = abs(task.actual_minutes - task.estimated_minutes) / task.estimated_minutes
            total_error += error
        estimation_accuracy = (1 - (total_error / len(tasks_with_estimates))) * 100
    
    insights = {
        'productive_hours': productive_hours,
        'category_performance': category_performance,
        'estimation_accuracy': estimation_accuracy,
        'recommendations': generate_productivity_recommendations(productive_hours, category_performance)
    }
    
    return jsonify(insights)

def generate_productivity_recommendations(productive_hours, category_performance):
    """Generate personalized productivity recommendations"""
    recommendations = []
    
    # Find most productive hours
    if productive_hours:
        best_hours = sorted(productive_hours.items(), key=lambda x: x[1], reverse=True)[:3]
        recommendations.append({
            'type': 'optimal_timing',
            'title': 'Schedule Important Tasks During Your Peak Hours',
            'description': f'You\'re most productive at {", ".join([f"{h}:00" for h, _ in best_hours])}. Schedule your most important tasks during these times.',
            'priority': 'high'
        })
    
    # Category recommendations
    low_performing = [cat for cat in category_performance if cat['completion_rate'] < 50]
    if low_performing:
        recommendations.append({
            'type': 'category_focus',
            'title': 'Focus on Improving Completion Rates',
            'description': f'Consider breaking down tasks in {", ".join([cat["name"] for cat in low_performing])} into smaller, more manageable pieces.',
            'priority': 'medium'
        })
    
    return recommendations

# Smart Todo Management Features
@app.route('/api/todos/smart-schedule', methods=['POST'])
@login_required
def smart_schedule_todos():
    """Automatically schedule todos based on priority, due date, and available time"""
    data = request.json
    date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    
    # Get todos that need scheduling
    todos = ToDo.query.filter(
        ToDo.user_id == current_user.id,
        ToDo.completed == False,
        ToDo.due_date <= datetime.combine(date, datetime.max.time())
    ).order_by(ToDo.priority.desc(), ToDo.due_date.asc()).all()
    
    # Get available time blocks for the date
    daily_plan = DailyPlan.query.filter_by(user_id=current_user.id, date=date).first()
    if not daily_plan:
        daily_plan = DailyPlan(user_id=current_user.id, date=date)
        db.session.add(daily_plan)
        db.session.commit()
    
    available_blocks = [block for block in daily_plan.time_blocks if not block.task_id]
    
    scheduled_todos = []
    for todo in todos[:len(available_blocks)]:  # Only schedule as many as we have blocks
        if available_blocks:
            block = available_blocks.pop(0)
            
            # Create a task for this todo if it doesn't exist
            task = Task.query.filter_by(title=todo.title, user_id=current_user.id).first()
            if not task:
                # Find or create a category for this todo
                category = Category.query.filter_by(name=todo.assigned_role.name if todo.assigned_role else 'Personal', user_id=current_user.id).first()
                if not category:
                    category = Category(name='Personal', user_id=current_user.id, color='#6c757d')
                    db.session.add(category)
                    db.session.commit()
                
                task = Task(
                    title=todo.title,
                    description=todo.description,
                    category_id=category.id,
                    user_id=current_user.id,
                    priority=todo.priority,
                    due_date=todo.due_date
                )
                db.session.add(task)
                db.session.commit()
            
            # Assign task to time block
            block.task_id = task.id
            scheduled_todos.append({
                'todo_id': todo.id,
                'title': todo.title,
                'time': block.start_time.strftime('%H:%M'),
                'priority': todo.priority
            })
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'scheduled_count': len(scheduled_todos),
        'scheduled_todos': scheduled_todos
    })

@app.route('/api/todos/batch-operations', methods=['POST'])
@login_required
def batch_todo_operations():
    """Perform batch operations on todos"""
    data = request.json
    operation = data.get('operation')
    todo_ids = data.get('todo_ids', [])
    
    if not todo_ids:
        return jsonify({'success': False, 'message': 'No todos selected'})
    
    todos = ToDo.query.filter(
        ToDo.id.in_(todo_ids),
        ToDo.user_id == current_user.id
    ).all()
    
    if operation == 'complete':
        for todo in todos:
            todo.completed = True
            todo.completed_at = datetime.utcnow()
            
            # Handle recurring todos
            if todo.is_recurring and todo.recurrence_rule:
                next_date = calculate_next_due_date(todo.due_date, todo.recurrence_rule)
                if next_date:
                    new_todo = ToDo(
                        title=todo.title,
                        description=todo.description,
                        user_id=todo.user_id,
                        role_id=todo.role_id,
                        due_date=next_date,
                        priority=todo.priority,
                        is_recurring=True,
                        recurrence_rule=todo.recurrence_rule,
                        next_occurrence=next_date
                    )
                    db.session.add(new_todo)
    
    elif operation == 'delete':
        for todo in todos:
            db.session.delete(todo)
    
    elif operation == 'update_priority':
        new_priority = data.get('priority')
        for todo in todos:
            todo.priority = new_priority
    
    elif operation == 'move_to_role':
        role_id = data.get('role_id')
        for todo in todos:
            todo.role_id = role_id
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Successfully {operation}d {len(todos)} todos'
    })

@app.route('/api/todos/priority-suggestions', methods=['GET'])
@login_required
def get_priority_suggestions():
    """Get AI-powered priority suggestions for todos"""
    # Get todos without due dates or with low priority
    todos = ToDo.query.filter(
        ToDo.user_id == current_user.id,
        ToDo.completed == False,
        (ToDo.due_date.is_(None) | (ToDo.priority.in_(['low', 'medium'])))
    ).all()
    
    suggestions = []
    for todo in todos:
        score = 0
        reasons = []
        
        # Factor 1: Due date proximity
        if todo.due_date:
            days_until_due = (todo.due_date.date() - datetime.now().date()).days
            if days_until_due <= 1:
                score += 30
                reasons.append('Due today/tomorrow')
            elif days_until_due <= 3:
                score += 20
                reasons.append('Due soon')
            elif days_until_due <= 7:
                score += 10
                reasons.append('Due this week')
        
        # Factor 2: Role importance (you can customize this)
        if todo.assigned_role:
            if todo.assigned_role.name.lower() in ['work', 'aps', 'urgent']:
                score += 15
                reasons.append('High-priority role')
        
        # Factor 3: Current priority
        if todo.priority == 'low':
            score += 5
        elif todo.priority == 'medium':
            score += 10
        
        # Factor 4: Recurring todos
        if todo.is_recurring:
            score += 5
            reasons.append('Recurring task')
        
        if score > 15:  # Only suggest if score is significant
            suggestions.append({
                'todo_id': todo.id,
                'title': todo.title,
                'current_priority': todo.priority,
                'suggested_priority': 'high' if score >= 25 else 'medium',
                'score': score,
                'reasons': reasons
            })
    
    # Sort by score descending
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({
        'success': True,
        'suggestions': suggestions[:10]  # Top 10 suggestions
    })

# Database tables will be created automatically on first request
if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("✅ Database tables created successfully")
    app.run(debug=True)
else:
    # For production deployment, create tables on startup
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables verified/created")
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")
            # Continue running even if table creation fails (tables might already exist)

@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard page"""
    # Get all roles and todos for the analytics page
    all_roles = Role.query.filter_by(user_id=current_user.id).all()
    all_todos = ToDo.query.filter_by(user_id=current_user.id, completed=False).all()
    
    return render_template('analytics.html', all_roles=all_roles, all_todos=all_todos)