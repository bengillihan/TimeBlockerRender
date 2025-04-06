# Gunicorn configuration file
# Optimize for PostgreSQL efficiency and resource usage

# Server socket settings
bind = "0.0.0.0:5000"
backlog = 100

# Worker processes
workers = 2  # Start with a minimal number of workers
worker_class = "sync"
worker_connections = 200
timeout = 60
keepalive = 2

# Server mechanics
preload_app = True  # Load application code before worker processes are forked
max_requests = 500  # Restart workers after serving this many requests
max_requests_jitter = 50  # Prevent all workers from restarting at once

# Logging
errorlog = "-"
loglevel = "info"
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process Naming
proc_name = "timeblock_gunicorn"

# Shutdown behavior for database connection cleanup
graceful_timeout = 30  # Graceful shutdown timeout

# Database optimization hooks
def on_starting(server):
    """Log that the server is starting."""
    server.log.info("Starting TimeBlocker with optimized PostgreSQL settings")
    
def worker_int(worker):
    """Handle worker interruption to clean up database connections."""
    worker.log.info("Worker shutting down, closing DB connections")
    from app import db
    db.session.remove()
    db.engine.dispose()

def pre_fork(server, worker):
    """Actions to take before forking - reset database connections."""
    server.log.info("Pre-fork operations: cleaning DB state")
    from app import db
    db.session.remove()
    db.engine.dispose()

def post_fork(server, worker):
    """Actions to take after forking."""
    server.log.info(f"Worker {worker.pid} initialized")

def child_exit(server, worker):
    """Clean up when child worker exits."""
    server.log.info(f"Worker {worker.pid} exited, cleaning up resources")
    from app import db
    db.session.remove()
    db.engine.dispose()

def on_exit(server):
    """Actions to take before server shutdown."""
    server.log.info("Shutting down TimeBlocker server, releasing database resources")
    from app import db
    db.session.remove()
    db.engine.dispose()