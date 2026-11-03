"""
Gunicorn उत्पादन संरूपण (Production Gunicorn Configuration)
श्री देवस्थान विश्वस्त व्यवस्था संकेतस्थळ
"""

import multiprocessing
import os

# सर्व्हर बाइंडिंग
bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:8000")
backlog = 2048

# वर्कर प्रक्रिया (Worker Processes = 2 * CPU + 1)
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 5

# लॉगिंग (Logging)
accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "/var/log/temple_trust/gunicorn_access.log")
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "/var/log/temple_trust/gunicorn_error.log")
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# सुरक्षा आणि प्रक्रिया नाव
proc_name = "temple_trust_flask"
daemon = False
preload_app = True
