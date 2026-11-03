from datetime import datetime, timezone
from app.extensions import db

class LiveStreamSettings(db.Model):
    """
    थेट आरती प्रक्षेपण सेटिंग्ज टेबल
    """
    __tablename__ = 'live_stream_settings'

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False, default='youtube') # youtube, cloudflare, custom
    video_id = db.Column(db.String(100), nullable=True, default='jfKfPfyJRdk')
    embed_url = db.Column(db.String(500), nullable=True)
    is_enabled = db.Column(db.Boolean, default=True)
    unavailable_message = db.Column(
        db.Text, 
        nullable=False, 
        default='सध्या थेट आरती सुरू नाही. कृपया पुढील आरतीच्या वेळी पुन्हा भेट द्या.'
    )
    notice = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def current_embed_url(self):
        """डायनॅमिक एम्बेड URL जनरेटर"""
        if self.provider == 'youtube' and self.video_id:
            return f"https://www.youtube.com/embed/{self.video_id}?autoplay=1&mute=0&rel=0&modestbranding=1"
        return self.embed_url or ""

    def __repr__(self):
        return f"<LiveStreamSettings provider={self.provider} enabled={self.is_enabled}>"


class AartiSchedule(db.Model):
    """
    दैनिक आरती वेळापत्रक टेबल
    """
    __tablename__ = 'aarti_schedule'

    id = db.Column(db.Integer, primary_key=True)
    aarti_name = db.Column(db.String(150), nullable=False) # उदा. काकड आरती, महापूजा
    start_time = db.Column(db.String(50), nullable=False) # उदा. 05:30
    end_time = db.Column(db.String(50), nullable=True) # उदा. 06:15
    marathi_time = db.Column(db.String(100), nullable=True) # उदा. पहाटे ०५:३० वाजता
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=1, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)

    def __repr__(self):
        return f"<AartiSchedule {self.aarti_name} at {self.start_time}>"
