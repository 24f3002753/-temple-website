import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'temple-trust-marathi-default-secret-key-replace-in-prod')
    
    # Database Settings
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'postgresql://postgres:postgres@localhost:5432/temple_trust_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # Uploads and Receipt Storage (Use /tmp on Vercel serverless)
    IS_VERCEL = bool(os.environ.get('VERCEL'))
    if IS_VERCEL:
        UPLOAD_FOLDER = '/tmp/uploads'
        RECEIPT_FOLDER = '/tmp/receipts'
    else:
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
        RECEIPT_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'receipts')

    FONT_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'fonts')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)) # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'pdf'}

    # Razorpay Payment Gateway
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')
    RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET', '')

    # Email / SMTP Settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get(
        'MAIL_DEFAULT_SENDER', 
        'श्री देवस्थान विश्वस्त व्यवस्था <info@templetrust.org>'
    )

    # Session & Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_TIME_LIMIT = 3600

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Fallback to SQLite if PostgreSQL is not locally running during development/testing
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'temple_dev.db')}"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {}

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    # Ensure production strictly uses PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
