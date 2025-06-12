# Simplified Gunicorn configuration file
# Basic settings without complex hooks to prevent import issues

# Server socket settings
bind = "0.0.0.0:5000"
backlog = 100

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 200
timeout = 60
keepalive = 2

# Server mechanics
preload_app = True
max_requests = 500
max_requests_jitter = 50

# Logging
errorlog = "-"
loglevel = "info"
accesslog = "-"

# Process Naming
proc_name = "timeblock_gunicorn"

# Shutdown behavior
graceful_timeout = 30