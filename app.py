import os
import logging
import pytz
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import func
from nylas_auth import nylas_auth # Added import for Nylas auth blueprint

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
from models import User, DailyPlan, Priority, TimeBlock, Category, Task, NavLink, DayTemplate # Added NavLink and DayTemplate imports
from google_auth import google_auth

app.register_blueprint(google_auth)
app.register_blueprint(nylas_auth) # Added Nylas blueprint registration

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
    has_google_calendar = False
    if hasattr(current_user, 'credentials_info') and current_user.credentials_info:
        try:
            from calendar_service import get_calendar_events
            # Use selected calendars if available, otherwise default to primary
            selected_calendars = current_user.selected_calendars or ['primary']
            logger.info(f"Fetching calendar events for date: {date} with calendars: {selected_calendars}")

            calendar_events = get_calendar_events(
                current_user.credentials_info, 
                date,
                calendar_ids=selected_calendars
            )
            has_google_calendar = True
            logger.info(f"Retrieved {len(calendar_events)} calendar events")
            for event in calendar_events:
                logger.debug(f"Event: {event['summary']} at {event['start_time']}")
        except Exception as e:
            logger.error(f"Error fetching calendar events: {str(e)}")
            flash("Could not fetch calendar events. Please try reconnecting your Google Calendar.", "warning")
    else:
        logger.warning(f"User {current_user.id} is missing Google credentials")
        has_google_calendar = False

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
                         calendar_events=calendar_events,
                         has_google_calendar=has_google_calendar)

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
    # Validate required fields
    if not data.get('title') or not data.get('category_id'):
        return jsonify({'error': 'Title and category are required'}), 400

    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating task: {str(e)}")
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
            if block_data.get('start_time'):
                time_block = TimeBlock(
                    daily_plan_id=daily_plan.id,
                    start_time=datetime.strptime(block_data['start_time'], '%H:%M').time(),
                    end_time=datetime.strptime(block_data['end_time'], '%H:%M').time(),
                    task_id=block_data.get('task_id'),
                    completed=block_data.get('completed', False),
                    notes=block_data.get('notes', '')[:15]  # Ensure notes don't exceed 15 chars
                )
                db.session.add(time_block)

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
        logger.debug(f"Received calendar IDs to save: {selected_ids}")

        # Store the selected calendars
        current_user.selected_calendars = selected_ids
        db.session.commit()
        logger.info(f"Saved selected calendars for user {current_user.id}: {selected_ids}")
        return jsonify({'status': 'success'})

    try:
        calendars = []
        has_google_auth = hasattr(current_user, 'credentials_info') and current_user.credentials_info
        has_nylas_auth = bool(current_user.nylas_access_token)

        logger.info(f"User {current_user.id} auth status - Google: {has_google_auth}, Nylas: {has_nylas_auth}")

        # If Google Calendar is connected, fetch calendars
        if has_google_auth:
            logger.debug(f"Fetching calendar list for user {current_user.id}")
            from calendar_service import get_calendar_list
            calendars = get_calendar_list(current_user.credentials_info)

            if not calendars:
                logger.warning("No calendars found in response")
                flash("No calendars found. Please ensure you've granted calendar access.", "warning")

        # If neither service is connected, show appropriate message
        if not has_google_auth and not has_nylas_auth:
            flash("Please connect at least one calendar service to continue.", "info")

        logger.debug(f"Found {len(calendars)} calendars")
        logger.debug(f"Currently selected calendars: {current_user.selected_calendars}")

        return render_template('calendar_settings.html', 
                            calendars=calendars,
                            selected_calendars=current_user.selected_calendars or [])

    except Exception as e:
        logger.error(f"Error in calendar settings: {str(e)}")
        flash("An error occurred while loading calendar settings. Please try again.", "error")
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint to verify server status."""
    try:
        # Check if we can access the database
        db.session.execute('SELECT 1')
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


@app.route('/nav_links')
@login_required
def nav_links():
    """Show navigation links management page."""
    nav_links = NavLink.query.filter_by(user_id=current_user.id).order_by(NavLink.order).all()
    return render_template('nav_links.html', nav_links=nav_links)

@app.route('/api/nav_links', methods=['POST'])
@login_required
def add_nav_link():
    """Add a new navigation link."""
    data = request.json
    if not data.get('name') or not data.get('url'):
        return jsonify({'error': 'Name and URL are required'}), 400

    # Get the highest order number and add 1
    max_order = db.session.query(func.max(NavLink.order)).filter_by(user_id=current_user.id).scalar()
    new_order = (max_order or 0) + 1

    link = NavLink(
        name=data['name'],
        url=data['url'],
        icon_class=data.get('icon_class', 'fas fa-link'),
        user_id=current_user.id,
        order=new_order,
        embed=data.get('embed', False),
        show_in_nav=data.get('show_in_nav', True),
        iframe_height=data.get('iframe_height', 600)
    )
    db.session.add(link)
    db.session.commit()

    return jsonify({
        'id': link.id,
        'name': link.name,
        'url': link.url,
        'icon_class': link.icon_class,
        'embed': link.embed,
        'show_in_nav': link.show_in_nav,
        'iframe_height': link.iframe_height
    })

@app.route('/api/nav_links/<int:link_id>', methods=['PUT', 'DELETE'])
@login_required
def nav_link_operations(link_id):
    """Update or delete a navigation link."""
    link = NavLink.query.filter_by(id=link_id, user_id=current_user.id).first_or_404()

    if request.method == 'DELETE':
        db.session.delete(link)
        db.session.commit()
        return '', 204

    data = request.json
    if 'embed' in data:
        link.embed = data['embed']
    if 'show_in_nav' in data:
        link.show_in_nav = data['show_in_nav']
    if 'name' in data:
        link.name = data['name']
    if 'url' in data:
        link.url = data['url']
    if 'icon_class' in data:
        link.icon_class = data['icon_class']
    if 'iframe_height' in data:
        link.iframe_height = data['iframe_height']

    db.session.commit()
    return jsonify({
        'id': link.id,
        'name': link.name,
        'url': link.url,
        'icon_class': link.icon_class,
        'embed': link.embed,
        'show_in_nav': link.show_in_nav,
        'iframe_height': link.iframe_height
    })

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

with app.app_context():
    db.create_all()