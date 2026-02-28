import os

bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 100

workers = 1
threads = 4
worker_class = "gthread"
timeout = 30
keepalive = 2

preload_app = True
max_requests = 500
max_requests_jitter = 50

errorlog = "-"
loglevel = "info"
accesslog = "-"

proc_name = "timeblock_gunicorn"

graceful_timeout = 15
