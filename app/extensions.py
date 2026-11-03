from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

# Graceful import for Flask-Migrate
try:
    from flask_migrate import Migrate
    migrate = Migrate()
except ImportError:
    class DummyMigrate:
        def init_app(self, app, db=None):
            pass
    migrate = DummyMigrate()

# Graceful import for Flask-WTF CSRFProtect
try:
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
except ImportError:
    class DummyCSRF:
        def init_app(self, app):
            pass
        def exempt(self, view):
            return view
    csrf = DummyCSRF()

login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message = 'कृपया पुढे जाण्यासाठी प्रथम लॉगिन करा.'
login_manager.login_message_category = 'warning'
