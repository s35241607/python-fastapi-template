"""
Gunicorn configuration for production deployment.

This configuration file is used when running:
    gunicorn app.main:app -c gunicorn.conf.py

Environment variables:
    GUNICORN_WORKERS: Number of worker processes (default: 4)
    GUNICORN_THREADS: Threads per worker (default: 1)
    GUNICORN_TIMEOUT: Worker timeout in seconds (default: 120)
"""

import os

# =============================================================================
# Worker Configuration
# =============================================================================

# Number of worker processes
# Recommended: (2 x CPU cores) + 1
# Can be overridden via GUNICORN_WORKERS environment variable
workers = int(os.environ.get("GUNICORN_WORKERS", 4))

# Worker class - use Uvicorn's async worker for FastAPI
worker_class = "uvicorn.workers.UvicornWorker"

# Threads per worker (for sync workers, not used with UvicornWorker)
threads = int(os.environ.get("GUNICORN_THREADS", 1))

# =============================================================================
# Server Socket
# =============================================================================

# Bind address
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")

# =============================================================================
# Timeouts
# =============================================================================

# Worker timeout (seconds)
# Workers silent for more than this many seconds are killed and restarted
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 120))

# Timeout for graceful workers restart
graceful_timeout = 30

# Keep-alive connections timeout
keepalive = 5

# =============================================================================
# Logging
# =============================================================================

# Access log - write to stdout for Docker/container logging
accesslog = "-"

# Error log - write to stderr for Docker/container logging
errorlog = "-"

# Log level (debug, info, warning, error, critical)
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# Access log format
# Use a simple format since our middleware handles detailed access logging
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s'

# =============================================================================
# Security
# =============================================================================

# Limit request line size
limit_request_line = 4096

# Limit number of request headers
limit_request_fields = 100

# Limit request header field size
limit_request_field_size = 8190

# =============================================================================
# Process Naming
# =============================================================================

# Process name prefix
proc_name = "fastapi-app"

# =============================================================================
# Server Mechanics
# =============================================================================

# Daemonize the process (False for Docker)
daemon = False

# PID file location (None for Docker)
pidfile = None

# User/Group to run as (None = current user)
user = None
group = None

# Tmp upload directory
tmp_upload_dir = None

# =============================================================================
# Hooks
# =============================================================================


def on_starting(server):
    """Called just before the master process is initialized."""
    pass


def on_reload(server):
    """Called when receiving SIGHUP signal."""
    pass


def worker_int(worker):
    """Called when a worker receives SIGINT or SIGQUIT."""
    pass


def worker_abort(worker):
    """Called when a worker receives SIGABRT."""
    pass
