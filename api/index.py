import os
import sys

# Ensure root directory is in python path for Vercel Serverless Function
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import create_app

env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)

# Vercel looks for the WSGI handler named 'app'
