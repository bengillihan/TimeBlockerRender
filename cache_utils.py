from functools import wraps
from flask import current_app
from datetime import datetime, timedelta
import json
from flask_caching import Cache

cache = Cache()

def init_cache(app):
    """Initialize cache with Redis or simple memory cache"""
    cache_config = {
        'CACHE_TYPE': 'redis' if app.config.get('REDIS_URL') else 'simple',
        'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes default timeout
        'CACHE_KEY_PREFIX': 'timeblocker_'
    }
    
    if app.config.get('REDIS_URL'):
        cache_config['CACHE_REDIS_URL'] = app.config['REDIS_URL']
    
    cache.init_app(app, config=cache_config)

def cache_key_prefix():
    """Generate cache key prefix based on user and date"""
    from flask_login import current_user
    if not current_user.is_authenticated:
        return 'anonymous'
    return f"user_{current_user.id}"

def cached(timeout=300, key_prefix='view'):
    """Cache decorator with user-specific keys"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_login import current_user
            if not current_user.is_authenticated:
                return f(*args, **kwargs)
            
            cache_key = f"{cache_key_prefix()}_{key_prefix}_{f.__name__}"
            if kwargs:
                cache_key += f"_{json.dumps(kwargs, sort_keys=True)}"
            
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

def invalidate_cache(pattern):
    """Invalidate cache entries matching pattern"""
    from flask_login import current_user
    if not current_user.is_authenticated:
        return
    
    prefix = f"{cache_key_prefix()}_{pattern}"
    cache.delete_many(prefix)

def get_paginated_results(query, page, per_page=20):
    """Helper function for pagination"""
    return query.paginate(page=page, per_page=per_page, error_out=False)

def get_cache_stats():
    """Get cache statistics"""
    return {
        'hits': cache.get('cache_hits') or 0,
        'misses': cache.get('cache_misses') or 0,
        'size': cache.get('cache_size') or 0
    }