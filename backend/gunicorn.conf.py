"""
Gunicorn configuration for production deployment
"""

import multiprocessing
import os

# Server socket
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '8080')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Timeout settings
timeout = 300
keepalive = 2
graceful_timeout = 30

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "animathic-backend"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance
worker_tmp_dir = "/dev/shm"
preload_app = True
reload = False

# Health checks
check_config = True
