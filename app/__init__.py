import os
from flask import Flask
from config import config_by_name
from app.extensions import db, migrate, login_manager, csrf

def create_app(config_name='development'):
    """
    श्री देवस्थान ॲप्लिकेशन फॅक्टरी (Flask Application Factory)
    """
    app = Flask(__name__)
    config_obj = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_obj)

    # आवश्यक डिरेक्टरी तयार करा
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'app/static/uploads'), exist_ok=True)
    os.makedirs(app.config.get('RECEIPT_FOLDER', 'app/static/receipts'), exist_ok=True)
    os.makedirs(app.config.get('FONT_FOLDER', 'app/static/fonts'), exist_ok=True)

    # विस्तारक (Extensions) सुरू करा
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    # ब्लूप्रिंट्स नोंदणी करा
    from app.routes.public import public_bp
    from app.routes.donations import donations_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(donations_bp)
    app.register_blueprint(admin_bp)

    return app
