import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_caching import Cache
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
cache = Cache()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Import and apply configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Import and register blueprints
    from google_auth import google_auth
    app.register_blueprint(google_auth)
    
    # Import models after db initialization
    from models import User, DailyPlan, Priority, TimeBlock, Category, Task, NavLink, DayTemplate, ToDo, Role, TaskComment
    
    # Register user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Import routes after app initialization
    from app import register_routes
    register_routes(app)
    
    # Initialize cache utilities
    from cache_utils import init_cache
    init_cache(app)
    
    return app