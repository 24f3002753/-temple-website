from datetime import datetime, timezone
from app.extensions import db

class Donor(db.Model):
    """
    देणगीदार भाविक टेबल
    """
    __tablename__ = 'donors'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False, index=True)
    email = db.Column(db.String(150), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    address = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    donations = db.relationship('Donation', backref='donor', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Donor {self.full_name} ({self.phone})>"


class Donation(db.Model):
    """
    देणगी व्यवहार टेबल (Donations)
    """
    __tablename__ = 'donations'

    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donors.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(10), default='INR')
    status = db.Column(db.String(20), default='PENDING', index=True) # PENDING, PAID, FAILED, REFUNDED
    receipt_number = db.Column(db.String(50), unique=True, nullable=True, index=True)
    notes = db.Column(db.String(255), nullable=True, default='सर्वसाधारण देवस्थान निधी')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    paid_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    payment = db.relationship('Payment', backref='donation', uselist=False, cascade='all, delete-orphan')
    receipt = db.relationship('Receipt', backref='donation', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Donation ID={self.id} Amount=₹{self.amount} Status={self.status}>"


class Payment(db.Model):
    """
    Razorpay पेमेंट व्यवहार व पडताळणी तपशील
    """
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donations.id', ondelete='CASCADE'), nullable=False, unique=True)
    razorpay_order_id = db.Column(db.String(100), nullable=False, index=True)
    razorpay_payment_id = db.Column(db.String(100), nullable=True, index=True)
    razorpay_signature = db.Column(db.String(255), nullable=True)
    signature_verified = db.Column(db.Boolean, default=False)
    payment_status = db.Column(db.String(50), default='created') # created, authorized, captured, failed
    error_code = db.Column(db.String(100), nullable=True)
    error_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Payment Order={self.razorpay_order_id} Verified={self.signature_verified}>"


class Receipt(db.Model):
    """
    तयार झालेली अधिकृत देवस्थान पावती मेटाडेटा
    """
    __tablename__ = 'receipts'

    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.Integer, db.ForeignKey('donations.id', ondelete='CASCADE'), nullable=False, unique=True)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    pdf_path = db.Column(db.String(255), nullable=False)
    issued_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Receipt {self.receipt_number}>"


class WebhookEvent(db.Model):
    """
    Razorpay Webhook इडेम्पोटन्सी (Idempotency) टेबल
    एकाच इव्हेंटमुळे दुहेरी पावती किंवा दुहेरी ईमेल तयार होणार नाही.
    """
    __tablename__ = 'webhook_events'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    event_type = db.Column(db.String(100), nullable=False)
    payload_hash = db.Column(db.String(128), nullable=True)
    processing_status = db.Column(db.String(50), default='PROCESSED') # PENDING, PROCESSED, FAILED, IGNORED
    processed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<WebhookEvent {self.event_id} ({self.processing_status})>"
