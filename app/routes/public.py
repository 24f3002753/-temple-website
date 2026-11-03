from flask import Blueprint, render_template, request
from app.models.trust import TrustDetails, TrustMember, ChairpersonMessage, PublicDocument
from app.models.stream import LiveStreamSettings, AartiSchedule
from app.models.content import GalleryImage, TrustUpdate
from app.services.streaming_service import StreamingService

public_bp = Blueprint('public', __name__)

@public_bp.app_context_processor
def inject_global_trust():
    """सर्व टेम्पलेट्समध्ये संस्थानाची माहिती आपोआप उपलब्ध करून देणे"""
    trust = TrustDetails.query.first()
    stream_setting = LiveStreamSettings.query.first()
    return {
        'trust': trust,
        'global_stream': stream_setting
    }

@public_bp.route('/')
def index():
    """मुख्यपृष्ठ (Homepage) - डायनॅमिक माहितीसह"""
    trust = TrustDetails.query.first()
    chairperson = ChairpersonMessage.query.first()
    trustees = TrustMember.query.filter_by(is_active=True).order_by(TrustMember.display_order.asc()).limit(4).all()
    aartis = AartiSchedule.query.filter_by(is_active=True).order_by(AartiSchedule.display_order.asc()).all()
    updates = TrustUpdate.query.filter_by(is_published=True).order_by(TrustUpdate.published_at.desc()).limit(3).all()
    gallery_images = GalleryImage.query.order_by(GalleryImage.display_order.asc()).limit(4).all()
    stream_setting = LiveStreamSettings.query.first()

    return render_template(
        'index.html',
        trust=trust,
        chairperson=chairperson,
        trustees=trustees,
        aartis=aartis,
        updates=updates,
        gallery_images=gallery_images,
        stream_setting=stream_setting
    )

@public_bp.route('/about-temple')
def about_temple():
    """मंदिराची माहिती व इतिहास (About Temple & History)"""
    trust = TrustDetails.query.first()
    return render_template('about_temple.html', trust=trust)

@public_bp.route('/trust')
def trust():
    """संस्थेविषयी (About Trust, Chairperson & Board of Trustees)"""
    trust = TrustDetails.query.first()
    chairperson = ChairpersonMessage.query.first()
    members = TrustMember.query.filter_by(is_active=True).order_by(TrustMember.display_order.asc()).all()
    documents = PublicDocument.query.filter_by(is_public=True).all()

    return render_template(
        'trust.html',
        trust=trust,
        chairperson=chairperson,
        members=members,
        documents=documents
    )

@public_bp.route('/live-aarti')
def live_aarti():
    """थेट आरती दर्शन (Live Aarti Streaming Page via StreamingService)"""
    context = StreamingService.get_live_aarti_context()
    return render_template('live_aarti.html', **context)

@public_bp.route('/donate')
def donate():
    """ऑनलाइन देणगी पृष्ठ (Online Donation Page)"""
    return render_template('donate.html')

@public_bp.route('/donation-success')
def donation_success():
    """देणगी यशस्वी पृष्ठ (Donation Success & Receipt Download)"""
    donor_name = request.args.get('donor_name', 'श्री. भाविक')
    amount = request.args.get('amount', '५०१')
    receipt_number = request.args.get('receipt_number', 'STT-2026-0001')
    payment_id = request.args.get('payment_id', 'pay_live_sample')
    return render_template(
        'donation_success.html',
        donor_name=donor_name,
        amount=amount,
        receipt_number=receipt_number,
        payment_id=payment_id
    )

@public_bp.route('/donation-failed')
def donation_failed():
    """देणगी अयशस्वी पृष्ठ (Donation Failed Page)"""
    error_message = request.args.get('error', 'देणगी प्रक्रिया पूर्ण होऊ शकली नाही. कृपया पुन्हा प्रयत्न करा.')
    return render_template('donation_failed.html', error_message=error_message)

@public_bp.route('/gallery')
def gallery():
    """छायाचित्र संग्रह (Photo Gallery)"""
    all_images = GalleryImage.query.order_by(GalleryImage.display_order.asc()).all()
    aarti_images = [img for img in all_images if img.category == 'aarti']
    festival_images = [img for img in all_images if img.category == 'festival']
    campus_images = [img for img in all_images if img.category == 'campus']
    social_images = [img for img in all_images if img.category == 'social']

    return render_template(
        'gallery.html',
        all_images=all_images,
        aarti_images=aarti_images,
        festival_images=festival_images,
        campus_images=campus_images,
        social_images=social_images
    )

@public_bp.route('/updates')
def updates():
    """बातम्या व उपक्रम (News & Trust Announcements)"""
    updates_list = TrustUpdate.query.filter_by(is_published=True).order_by(TrustUpdate.published_at.desc()).all()
    return render_template('updates.html', updates_list=updates_list)

@public_bp.route('/contact')
def contact():
    """संपर्क (Contact & Location)"""
    trust = TrustDetails.query.first()
    return render_template('contact.html', trust=trust)
