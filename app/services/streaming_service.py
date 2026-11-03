import re
from datetime import datetime
from abc import ABC, abstractmethod
from app.extensions import db
from app.models.stream import LiveStreamSettings, AartiSchedule

class BaseStreamingProvider(ABC):
    """
    थेट व्हिडिओ प्रदात्याचा मूळ अमूर्त वर्ग (Abstract Base Provider)
    भविष्यात YouTube ऐवजी Cloudflare Stream किंवा इतर सेवा जोडण्यासाठी लवचिक डिझाइन.
    """
    @abstractmethod
    def get_embed_url(self, video_id: str, custom_url: str = None) -> str:
        pass

    @abstractmethod
    def get_player_type(self) -> str:
        pass


class YouTubeStreamingProvider(BaseStreamingProvider):
    """
    YouTube Live थेट प्रक्षेपण प्रदाता
    """
    def clean_video_id(self, video_input: str) -> str:
        """वापरकर्त्याने पूर्ण URL किंवा थेट Video ID टाकला तरीही अचूक ID काढणे"""
        if not video_input:
            return ""
        video_input = video_input.strip()
        # जर वापरकर्त्याने https://www.youtube.com/watch?v=XXXX टाकला असेल
        match = re.search(r'(?:v=|\/embed\/|youtu\.be\/)([a-zA-Z0-9_-]{11})', video_input)
        if match:
            return match.group(1)
        return video_input

    def get_embed_url(self, video_id: str, custom_url: str = None) -> str:
        clean_id = self.clean_video_id(video_id)
        if not clean_id:
            return ""
        return f"https://www.youtube.com/embed/{clean_id}?autoplay=1&mute=0&rel=0&modestbranding=1"

    def get_player_type(self) -> str:
        return "youtube"


class CloudflareStreamProvider(BaseStreamingProvider):
    """
    Cloudflare Stream थेट प्रक्षेपण प्रदाता (भविष्यातील अपग्रेडसाठी सज्ज)
    """
    def get_embed_url(self, video_id: str, custom_url: str = None) -> str:
        if custom_url:
            return custom_url
        if not video_id:
            return ""
        return f"https://iframe.videodelivery.net/{video_id}"

    def get_player_type(self) -> str:
        return "cloudflare"


class CustomHLSProvider(BaseStreamingProvider):
    """
    सानुकूल HLS / RTMP थेट प्रक्षेपण प्रदाता
    """
    def get_embed_url(self, video_id: str, custom_url: str = None) -> str:
        return custom_url or video_id or ""

    def get_player_type(self) -> str:
        return "custom_hls"


class StreamingService:
    """
    थेट आरती व्यवस्थापन सेवा (Streaming Business Logic Layer)
    """
    _providers = {
        'youtube': YouTubeStreamingProvider(),
        'cloudflare': CloudflareStreamProvider(),
        'custom_hls': CustomHLSProvider()
    }

    @classmethod
    def get_provider(cls, provider_name: str) -> BaseStreamingProvider:
        return cls._providers.get(provider_name.lower(), cls._providers['youtube'])

    @classmethod
    def get_stream_settings(cls) -> LiveStreamSettings:
        setting = LiveStreamSettings.query.first()
        if not setting:
            setting = LiveStreamSettings(
                provider='youtube',
                video_id='jfKfPfyJRdk',
                is_enabled=True,
                unavailable_message='सध्या थेट आरती सुरू नाही. कृपया पुढील आरतीच्या वेळी पुन्हा भेट द्या.'
            )
            db.session.add(setting)
            db.session.commit()
        return setting

    @classmethod
    def get_live_aarti_context(cls) -> dict:
        """
        थेट आरती पृष्ठासाठी आवश्यक सर्व माहिती गोळा करणे
        """
        setting = cls.get_stream_settings()
        provider = cls.get_provider(setting.provider)
        
        embed_url = ""
        if setting.is_enabled and setting.video_id:
            embed_url = provider.get_embed_url(setting.video_id, setting.embed_url)

        # सर्व सक्रिय आरत्या
        aartis = AartiSchedule.query.filter_by(is_active=True).order_by(AartiSchedule.display_order.asc()).all()

        # पुढील आरती शोधणे
        next_aarti, seconds_left = cls.calculate_next_aarti(aartis)

        return {
            'settings': setting,
            'is_stream_active': setting.is_enabled and bool(embed_url),
            'video_id': setting.video_id,
            'embed_url': embed_url,
            'provider_type': provider.get_player_type(),
            'unavailable_message': setting.unavailable_message,
            'notice': setting.notice,
            'aarti_list': aartis,
            'next_aarti': next_aarti,
            'seconds_to_next_aarti': seconds_left
        }

    @classmethod
    def calculate_next_aarti(cls, aartis):
        """
        सध्याच्या वेळेनुसार पुढील नियोजित आरती आणि शिल्लक वेळ काढणे
        """
        if not aartis:
            return None, 0

        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute

        next_aarti = None
        min_diff = 24 * 60 # २४ तास

        for aarti in aartis:
            try:
                # start_time हे "HH:MM" स्वरूपात असते (उदा. "05:30", "12:00")
                parts = aarti.start_time.strip().split(':')
                aarti_mins = int(parts[0]) * 60 + int(parts[1])
                diff = aarti_mins - current_minutes
                if diff > 0 and diff < min_diff:
                    min_diff = diff
                    next_aarti = aarti
            except (ValueError, IndexError):
                continue

        # जर दिवसातील सर्व आरत्या संपल्या असतील तर दुसऱ्या दिवसाची पहिली आरती
        if not next_aarti and aartis:
            next_aarti = aartis[0]
            try:
                parts = next_aarti.start_time.strip().split(':')
                first_mins = int(parts[0]) * 60 + int(parts[1])
                min_diff = (24 * 60 - current_minutes) + first_mins
            except (ValueError, IndexError):
                min_diff = 3600

        return next_aarti, max(min_diff * 60, 0)

    @classmethod
    def update_settings(cls, provider: str, video_id: str, is_enabled: bool, unavailable_message: str, notice: str = None):
        """
        प्रशासकाकडून थेट आरती सेटिंग्ज सुरक्षितपणे अद्ययावत करणे
        """
        setting = cls.get_stream_settings()
        
        # YouTube ID असल्यास स्वच्छ करा
        if provider == 'youtube':
            yt_provider = cls.get_provider('youtube')
            video_id = yt_provider.clean_video_id(video_id)

        setting.provider = provider
        setting.video_id = video_id
        setting.is_enabled = is_enabled
        if unavailable_message and unavailable_message.strip():
            setting.unavailable_message = unavailable_message.strip()
        setting.notice = notice.strip() if notice else None

        db.session.commit()
        return setting
