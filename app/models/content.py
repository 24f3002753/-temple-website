from datetime import datetime, timezone
from app.extensions import db

class GalleryImage(db.Model):
    """
    छायाचित्र संग्रह टेबल
    """
    __tablename__ = 'gallery'

    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default='aarti', index=True) # aarti, festival, campus, social
    display_order = db.Column(db.Integer, default=1)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return f"<GalleryImage {self.title} ({self.category})>"


class TrustUpdate(db.Model):
    """
    संस्थेच्या बातम्या व उपक्रम टेबल
    """
    __tablename__ = 'trust_updates'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), default='धार्मिक उत्सव') # धार्मिक उत्सव, सामाजिक सेवा, विकास प्रकल्प, परिपत्रक
    image_path = db.Column(db.String(255), nullable=True)
    published_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    is_published = db.Column(db.Boolean, default=True, index=True)

    def __repr__(self):
        return f"<TrustUpdate {self.title}>"
