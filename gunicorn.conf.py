# Gunicorn configuration for Ubuntu VPS with 4 cores
# Optimized for the label printer application

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = 4  # Match your VPS core count
worker_class = "sync"  # Use sync workers for I/O bound operations
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/label-printer/gunicorn_access.log"
errorlog = "/var/log/label-printer/gunicorn_error.log"
loglevel = "warning"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'label-printer'

# Server mechanics
daemon = False
pidfile = '/var/run/label-printer/gunicorn.pid'
user = 'www-data'
group = 'www-data'
tmp_upload_dir = None

# SSL (uncomment and configure if using HTTPS)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Preload app for better performance
preload_app = True

# Worker timeout for graceful shutdown
graceful_timeout = 30

# Environment variables
raw_env = [
    'FLASK_ENV=production',
    'PYTHONPATH=/opt/label-printer',
]

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Label Printer server is ready. Workers: %s", workers)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")
