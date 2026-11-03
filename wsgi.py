"""
उत्पादन WSGI प्रवेशद्वार (Production WSGI Entrypoint)
Gunicorn, uWSGI किंवा इतर WSGI सर्व्हरद्वारे चालवण्यासाठी.
वापर: gunicorn -c gunicorn_config.py wsgi:app
"""

import os
from dotenv import load_dotenv

# .env लोड करा
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app

# उत्पादन पर्यावरणामध्ये सुरू करा
env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)

if __name__ == "__main__":
    app.run()
