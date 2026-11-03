from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager

class AdminUser(UserMixin, db.Model):
    """
    प्रशासक खाते टेबल (सुरक्षित पासवर्ड हॅशिंग)
    """
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False, default='व्यवस्थापक')
    role = db.Column(db.String(50), nullable=False, default='superadmin') # superadmin, trustee, editor
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    audit_logs = db.relationship('AuditLog', backref='admin', lazy=True)

    def set_password(self, password):
        """सुरक्षित scrypt/argon2 हॅशिंग"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """गुप्तशब्द पडताळणी"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<AdminUser {self.username} ({self.role})>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(AdminUser, int(user_id))


class AuditLog(db.Model):
    """
    प्रशासक ऑडिट व सुरक्षा नोंद टेबल
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(100), nullable=False) # CREATE, UPDATE, DELETE, LOGIN, SETTINGS_CHANGE
    record_type = db.Column(db.String(100), nullable=False) # TRUSTEE, LIVE_STREAM, AARTI, ANNOUNCEMENT
    record_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<AuditLog Action={self.action} on {self.record_type}:{self.record_id}>"
