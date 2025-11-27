"""
Gunicorn Configuration File
Loads settings from environment variables via config module
"""

import multiprocessing
import sys
import os
from pathlib import Path

# Add web_app to path to import config
sys.path.insert(0, str(Path(__file__).parent / 'web_app'))
from config import config

# =============================================================================
# Server Socket
# =============================================================================
bind = config.GUNICORN_BIND

# =============================================================================
# Worker Processes
# =============================================================================
workers = config.GUNICORN_WORKERS
worker_class = config.GUNICORN_WORKER_CLASS
worker_connections = 1000
timeout = config.GUNICORN_TIMEOUT
keepalive = 5

# Graceful timeout for workers to finish requests before restarting
graceful_timeout = 30

# Max requests a worker will process before restarting (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50

# =============================================================================
# Logging
# =============================================================================
accesslog = config.GUNICORN_ACCESS_LOG
errorlog = config.GUNICORN_ERROR_LOG
loglevel = config.GUNICORN_LOGLEVEL

# Log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# =============================================================================
# Process Naming
# =============================================================================
proc_name = 'nvidia_course_advisor'

# =============================================================================
# Server Mechanics
# =============================================================================
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# =============================================================================
# SSL (for HTTPS)
# =============================================================================
# Uncomment and configure for HTTPS
# keyfile = '/path/to/keyfile.key'
# certfile = '/path/to/certfile.crt'

# =============================================================================
# Callbacks
# =============================================================================
def on_starting(server):
    """Called just before the master process is initialized."""
    print(f"Starting Gunicorn with {workers} {worker_class} workers")
    print(f"Binding to {bind}")
    print(f"Timeout: {timeout}s")


def on_reload(server):
    """Called when Gunicorn is reloading."""
    print("Reloading Gunicorn...")


def when_ready(server):
    """Called just after the server is started."""
    print("Gunicorn is ready. Spawning workers...")


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"Worker spawned (pid: {worker.pid})")


def pre_exec(server):
    """Called just before a new master process is forked."""
    print("Forking new master process...")


def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    print(f"Worker received INT or QUIT signal (pid: {worker.pid})")


def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    print(f"Worker aborted (pid: {worker.pid})")


def pre_request(worker, req):
    """Called just before a worker processes the request."""
    worker.log.debug(f"Request: {req.method} {req.path}")


def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    pass


def child_exit(server, worker):
    """Called just after a worker has been exited."""
    print(f"Worker exited (pid: {worker.pid})")


def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    print(f"Worker shutdown (pid: {worker.pid})")


def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    print(f"Number of workers changed from {old_value} to {new_value}")


def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("Shutting down Gunicorn...")
