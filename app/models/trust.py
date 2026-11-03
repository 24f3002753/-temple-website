from datetime import datetime, timezone
from app.extensions import db

class TrustDetails(db.Model):
    """
    मंदिर संस्थानाची सर्वसाधारण माहिती टेबल
    """
    __tablename__ = 'trust_details'

    id = db.Column(db.Integer, primary_key=True)
    trust_name = db.Column(db.String(255), nullable=False, default='श्री देवस्थान विश्वस्त व्यवस्था')
    establishment_year = db.Column(db.String(50), nullable=True, default='१९६५')
    history = db.Column(db.Text, nullable=True)
    introduction = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(500), nullable=True)
    registration_number = db.Column(db.String(100), nullable=True, default='महा./१२३४/ट्रस्ट')
    logo_path = db.Column(db.String(255), nullable=True, default='images/logo.svg')
    helpline_phone = db.Column(db.String(100), nullable=True, default='०२२-१२३४५६७८')
    contact_email = db.Column(db.String(100), nullable=True, default='info@templetrust.org')
    visiting_hours = db.Column(db.String(255), nullable=True, default='सकाळी ०५:०० ते रात्री १०:००')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<TrustDetails {self.trust_name}>"


class TrustMember(db.Model):
    """
    विश्वस्त मंडळ सदस्य टेबल
    """
    __tablename__ = 'trust_members'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    designation = db.Column(db.String(100), nullable=False) # अध्यक्ष, उपाध्यक्ष, सचिव, सहसचिव, खजिनदार, विश्वस्त
    photograph = db.Column(db.String(255), nullable=True, default='images/default-trustee.svg')
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=1, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<TrustMember {self.full_name} ({self.designation})>"


class ChairpersonMessage(db.Model):
    """
    अध्यक्षांचा संदेश टेबल
    """
    __tablename__ = 'chairperson_message'

    id = db.Column(db.Integer, primary_key=True)
    chairperson_name = db.Column(db.String(150), nullable=False, default='श्री. रमेशचंद्र जोशी')
    designation = db.Column(db.String(100), nullable=False, default='अध्यक्ष')
    photograph = db.Column(db.String(255), nullable=True, default='images/default-trustee.svg')
    message = db.Column(db.Text, nullable=False)
    vision = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<ChairpersonMessage {self.chairperson_name}>"


class PublicDocument(db.Model):
    """
    पारदर्शकता आणि अधिकृत कागदपत्रे टेबल (वार्षिक अहवाल, ऑडिट रिपोर्ट)
    """
    __tablename__ = 'public_documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(100), nullable=False) # नोंदणी प्रमाणपत्र, ऑडिट रिपोर्ट, कार्यवृत्तांत
    file_path = db.Column(db.String(255), nullable=False)
    published_year = db.Column(db.String(50), nullable=True)
    is_public = db.Column(db.Boolean, default=True)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<PublicDocument {self.title}>"
