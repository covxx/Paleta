# Gunicorn Configuration for QuickBooks Label Printer
# Production-ready configuration for VPS deployment

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:5002"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Optimal for I/O bound applications
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/opt/label-printer/logs/gunicorn_access.log"
errorlog = "/opt/label-printer/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "label-printer"

# Server mechanics
daemon = False
pidfile = "/opt/label-printer/gunicorn.pid"
user = "labelprinter"
group = "labelprinter"
tmp_upload_dir = "/tmp"

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
preload_app = True
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance

# Environment variables
raw_env = [
    'FLASK_ENV=production',
    'FLASK_APP=app.py',
]

# Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting QuickBooks Label Printer server...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading QuickBooks Label Printer server...")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("QuickBooks Label Printer server is ready. PID: %s", os.getpid())

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")

def pre_request(worker, req):
    """Called just before a worker processes the request."""
    worker.log.debug("%s %s", req.method, req.uri)

def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    worker.log.debug("%s %s - %s", req.method, req.uri, resp.status_code)

def child_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info("Worker exited (pid: %s)", worker.pid)

def max_requests_jitter_handler(server, worker):
    """Called when max_requests_jitter is reached."""
    server.log.info("Worker %s reached max_requests_jitter", worker.pid)

# Error handling
def on_exit(server):
    """Called just before exiting."""
    server.log.info("Shutting down QuickBooks Label Printer server...")

# Custom error pages
def error_handler(worker, req, environ, exc_info):
    """Custom error handler."""
    worker.log.error("Error processing request: %s", exc_info)

# Health check
def health_check(worker):
    """Health check for worker."""
    return True

# Graceful timeout
graceful_timeout = 30

# Worker timeout
worker_timeout = 30

# Restart workers
max_requests = 1000
max_requests_jitter = 100

# Memory management
worker_memory_limit = 200 * 1024 * 1024  # 200MB per worker

# CPU affinity (if needed)
# cpu_affinity = [0, 1, 2, 3]

# Threading
threads = 2
worker_class = "gthread"

# SSL configuration (if using HTTPS directly)
# keyfile = "/path/to/ssl/key.pem"
# certfile = "/path/to/ssl/cert.pem"
# ca_certs = "/path/to/ssl/ca.pem"

# Security headers
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Proxy headers
forwarded_allow_ips = '*'

# Request handling
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Response handling
response_buffer_size = 8192

# File uploads
max_requests_jitter = 100

# Logging configuration
disable_redirect_access_to_syslog = True
enable_stdio_inheritance = True

# Process management
preload_app = True
worker_tmp_dir = "/dev/shm"

# Environment
env = {
    'FLASK_ENV': 'production',
    'FLASK_APP': 'app.py',
    'PYTHONPATH': '/opt/label-printer',
    'PATH': '/opt/label-printer/venv/bin:/usr/local/bin:/usr/bin:/bin',
}

# Worker lifecycle
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting QuickBooks Label Printer server...")
    # Create necessary directories
    os.makedirs("/opt/label-printer/logs", exist_ok=True)
    os.makedirs("/opt/label-printer/uploads", exist_ok=True)
    os.makedirs("/opt/label-printer/sessions", exist_ok=True)

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("QuickBooks Label Printer server is ready. PID: %s", os.getpid())
    server.log.info("Server listening on %s", server.address)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")

def pre_request(worker, req):
    """Called just before a worker processes the request."""
    worker.log.debug("%s %s", req.method, req.uri)

def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    worker.log.debug("%s %s - %s", req.method, req.uri, resp.status_code)

def child_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info("Worker exited (pid: %s)", worker.pid)

def on_exit(server):
    """Called just before exiting."""
    server.log.info("Shutting down QuickBooks Label Printer server...")

# Custom error handling
def error_handler(worker, req, environ, exc_info):
    """Custom error handler."""
    worker.log.error("Error processing request: %s", exc_info)

# Health check endpoint
def health_check(worker):
    """Health check for worker."""
    return True

# Memory management
def worker_memory_limit_handler(worker):
    """Called when worker memory limit is reached."""
    worker.log.warning("Worker %s reached memory limit", worker.pid)

# Request timeout handling
def timeout_handler(worker):
    """Called when request timeout is reached."""
    worker.log.warning("Worker %s request timeout", worker.pid)

# Graceful shutdown
def graceful_shutdown(worker):
    """Called during graceful shutdown."""
    worker.log.info("Worker %s shutting down gracefully", worker.pid)

# Worker recycling
def worker_recycle(worker):
    """Called when worker is recycled."""
    worker.log.info("Worker %s recycled", worker.pid)

# Performance monitoring
def performance_monitor(worker):
    """Monitor worker performance."""
    worker.log.debug("Worker %s performance check", worker.pid)

# Error recovery
def error_recovery(worker, exc_info):
    """Handle worker errors."""
    worker.log.error("Worker %s error recovery: %s", worker.pid, exc_info)

# Custom logging
def custom_log(worker, message):
    """Custom logging function."""
    worker.log.info("Custom log: %s", message)

# Worker statistics
def worker_stats(worker):
    """Collect worker statistics."""
    return {
        'pid': worker.pid,
        'requests': worker.requests_count,
        'memory': worker.memory_usage,
        'uptime': worker.uptime
    }

# Configuration validation
def validate_config():
    """Validate configuration."""
    required_dirs = [
        "/opt/label-printer/logs",
        "/opt/label-printer/uploads",
        "/opt/label-printer/sessions"
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
    
    return True

# Initialize configuration
validate_config()