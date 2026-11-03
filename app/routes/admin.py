import csv
import io
from datetime import datetime, timezone, date
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.admin import AdminUser, AuditLog
from app.models.stream import LiveStreamSettings, AartiSchedule
from app.models.trust import TrustDetails, TrustMember, ChairpersonMessage, PublicDocument
from app.models.donation import Donation, Donor, Payment, Receipt
from app.models.content import GalleryImage, TrustUpdate
from app.services.streaming_service import StreamingService
from app.services.email_service import EmailService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def log_admin_action(action: str, record_type: str, record_id: int, details: str):
    """प्रशासकीय कृती सुरक्षा नोंद साठवणे"""
    try:
        admin_id = current_user.id if current_user.is_authenticated else None
        log = AuditLog(
            admin_id=admin_id,
            action=action,
            record_type=record_type,
            record_id=record_id,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()

# -------------------------------------------------------------
# ऑथेंटिकेशन (Login / Logout)
# -------------------------------------------------------------

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """प्रशासक लॉगिन"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = AdminUser.query.filter_by(username=username).first()
        if admin and admin.check_password(password) and admin.is_active:
            login_user(admin)
            admin.last_login = datetime.now(timezone.utc)
            db.session.commit()
            log_admin_action('LOGIN', 'ADMIN_USER', admin.id, f"प्रशासक {admin.username} ने लॉगिन केले.")
            flash(f'स्वागत आहे, {admin.full_name}! आपण यशस्वीरित्या प्रवेश केला.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('अवैध वापरकर्ता नाव किंवा गुप्तशब्द. कृपया पुन्हा तपासा.', 'danger')
            return redirect(url_for('admin.login'))
            
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    """प्रशासक बाहेर पडा"""
    log_admin_action('LOGOUT', 'ADMIN_USER', current_user.id, f"प्रशासक {current_user.username} बाहेर पडले.")
    logout_user()
    flash('आपण सुरक्षितपणे बाहेर पडला आहात.', 'info')
    return redirect(url_for('admin.login'))

# -------------------------------------------------------------
# १. डॅशबोर्ड विहंगावलोकन (Dashboard Overview)
# -------------------------------------------------------------

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """प्रशासक मुख्य नियंत्रण फलक (Dashboard)"""
    today = date.today()
    start_of_month = date(today.year, today.month, 1)

    # सर्व देणग्यांची आकडेवारी
    all_donations = Donation.query.all()
    paid_donations = [d for d in all_donations if d.status == 'PAID']
    pending_donations = [d for d in all_donations if d.status == 'PENDING']

    total_amount = sum(d.amount for d in paid_donations)
    
    # आजची देणगी
    today_paid = [d for d in paid_donations if d.created_at and d.created_at.date() == today]
    today_amount = sum(d.amount for d in today_paid)
    today_count = len(today_paid)

    # चालू महिन्याची देणगी
    month_paid = [d for d in paid_donations if d.created_at and d.created_at.date() >= start_of_month]
    month_amount = sum(d.amount for d in month_paid)

    # ताजे व्यवहार व घोषणा
    recent = Donation.query.order_by(Donation.created_at.desc()).limit(8).all()
    stream_setting = LiveStreamSettings.query.first()
    latest_updates = TrustUpdate.query.order_by(TrustUpdate.published_at.desc()).limit(4).all()

    return render_template(
        'admin/dashboard.html',
        total_amount=total_amount,
        today_amount=today_amount,
        today_count=today_count,
        month_amount=month_amount,
        paid_count=len(paid_donations),
        pending_count=len(pending_donations),
        recent_donations=recent,
        stream_setting=stream_setting,
        latest_updates=latest_updates
    )

# -------------------------------------------------------------
# २. देणगी व्यवस्थापन व CSV एक्सपोर्ट (Donations Management)
# -------------------------------------------------------------

@admin_bp.route('/donations')
@login_required
def donations_list():
    """सर्व देणग्यांची शोध व फिल्टर यादी"""
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('search', '').strip()

    query = Donation.query.join(Donor)

    if status_filter:
        query = query.filter(Donation.status == status_filter)

    if search_query:
        query = query.filter(
            db.or_(
                Donor.full_name.ilike(f"%{search_query}%"),
                Donor.email.ilike(f"%{search_query}%"),
                Donor.phone.ilike(f"%{search_query}%"),
                Donation.receipt_number.ilike(f"%{search_query}%")
            )
        )

    donations = query.order_by(Donation.created_at.desc()).all()

    return render_template(
        'admin/donations_list.html',
        donations=donations,
        current_status=status_filter,
        current_search=search_query
    )

@admin_bp.route('/donations/export-csv')
@login_required
def export_donations_csv():
    """देणगी डेटा CSV स्वरूपात सुरक्षित डाऊनलोड"""
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('search', '').strip()

    query = Donation.query.join(Donor)
    if status_filter:
        query = query.filter(Donation.status == status_filter)
    if search_query:
        query = query.filter(
            db.or_(
                Donor.full_name.ilike(f"%{search_query}%"),
                Donor.email.ilike(f"%{search_query}%"),
                Donation.receipt_number.ilike(f"%{search_query}%")
            )
        )

    donations = query.order_by(Donation.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    # CSV हेडर
    writer.writerow([
        'Receipt Number', 'Donor Name', 'Email', 'Phone', 
        'Amount (INR)', 'Status', 'Razorpay Order ID', 'Razorpay Payment ID', 
        'Date Created', 'Paid At'
    ])

    for d in donations:
        order_id = d.payment.razorpay_order_id if d.payment else ''
        payment_id = d.payment.razorpay_payment_id if d.payment else ''
        writer.writerow([
            d.receipt_number or 'PENDING',
            d.donor.full_name,
            d.donor.email,
            d.donor.phone,
            f"{d.amount:.2f}",
            d.status,
            order_id,
            payment_id,
            d.created_at.strftime('%Y-%m-%d %H:%M:%S') if d.created_at else '',
            d.paid_at.strftime('%Y-%m-%d %H:%M:%S') if d.paid_at else ''
        ])

    csv_data = output.getvalue()
    filename = f"Temple_Donations_{date.today().strftime('%Y%m%d')}.csv"

    log_admin_action('EXPORT', 'DONATIONS', 0, f"देणगी डेटा CSV एक्सपोर्ट केला ({len(donations)} नोंदी).")

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@admin_bp.route('/donations/resend-email/<int:donation_id>', methods=['POST'])
@login_required
def resend_receipt_email(donation_id):
    """देणगी पावती ईमेल पुन्हा पाठवणे"""
    donation = db.session.get(Donation, donation_id)
    if not donation or donation.status != 'PAID':
        flash('केवळ यशस्वी देणगीची पावती पुन्हा पाठवता येते.', 'warning')
        return redirect(url_for('admin.donations_list'))

    receipt = donation.receipt
    donor = donation.donor

    if not receipt:
        flash('या देणगीची पावती संचिका उपलब्ध नाही.', 'danger')
        return redirect(url_for('admin.donations_list'))

    success = EmailService.send_donation_receipt_email(
        recipient_email=donor.email,
        donor_name=donor.full_name,
        receipt_number=donation.receipt_number,
        amount=float(donation.amount),
        pdf_path=receipt.pdf_path,
        receipt_record=receipt
    )

    if success:
        log_admin_action('RESEND_EMAIL', 'RECEIPT', receipt.id, f"पावती {donation.receipt_number} ईमेलवर पुन्हा पाठवली.")
        flash(f"पावती {donation.receipt_number} यशस्वीरित्या {donor.email} वर पाठवली गेली.", 'success')
    else:
        flash("ईमेल सर्व्हरशी संपर्क होऊ शकला नाही. कृपया SMTP सेटिंग्ज तपासा.", 'danger')

    return redirect(url_for('admin.donations_list'))

# -------------------------------------------------------------
# ३. आर्थिक अहवाल (Reports)
# -------------------------------------------------------------

@admin_bp.route('/reports')
@login_required
def reports():
    """आर्थिक अहवाल व विश्लेषण"""
    paid_donations = Donation.query.filter_by(status='PAID').all()
    total_paid_amount = sum(d.amount for d in paid_donations)
    total_paid_count = len(paid_donations)
    avg_amount = (total_paid_amount / total_paid_count) if total_paid_count > 0 else Decimal('0.00')

    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    month_paid = [d for d in paid_donations if d.created_at and d.created_at.date() >= start_of_month]
    month_amount = sum(d.amount for d in month_paid)

    # चालू महिन्याची आकडेवारी
    monthly_stats = [{
        'month_str': today.strftime('%B %Y'),
        'total_trans': total_paid_count,
        'paid_trans': total_paid_count,
        'total_sum': total_paid_amount
    }]

    return render_template(
        'admin/reports.html',
        total_paid_amount=total_paid_amount,
        total_paid_count=total_paid_count,
        month_amount=month_amount,
        avg_amount=avg_amount,
        monthly_stats=monthly_stats
    )

# -------------------------------------------------------------
# ४. थेट आरती व वेळापत्रक (Live Stream & Aarti Schedule)
# -------------------------------------------------------------

@admin_bp.route('/live-stream', methods=['GET', 'POST'])
@login_required
def manage_stream():
    """थेट आरती प्रक्षेपण सेटिंग्ज संपादन"""
    settings = StreamingService.get_stream_settings()

    if request.method == 'POST':
        provider = request.form.get('provider', 'youtube')
        video_id = request.form.get('video_id', '').strip()
        is_enabled = bool(request.form.get('is_enabled'))
        unavailable_message = request.form.get('unavailable_message', '').strip()
        notice = request.form.get('notice', '').strip()

        if not video_id and is_enabled:
            flash('कृपया थेट प्रक्षेपणासाठी व्हिडिओ आयडी किंवा लिंक प्रविष्ट करा.', 'danger')
            return redirect(url_for('admin.manage_stream'))

        StreamingService.update_settings(
            provider=provider,
            video_id=video_id,
            is_enabled=is_enabled,
            unavailable_message=unavailable_message,
            notice=notice
        )

        log_admin_action('UPDATE', 'LIVE_STREAM', settings.id, f"थेट आरती सेटिंग्ज बदलली: Enabled={is_enabled}, VideoID={video_id}")
        flash('थेट आरती प्रक्षेपण सेटिंग्ज यशस्वीरित्या अद्ययावत झाल्या आहेत!', 'success')
        return redirect(url_for('admin.manage_stream'))

    return render_template('admin/stream_manage.html', settings=settings)

@admin_bp.route('/aarti-schedule')
@login_required
def aarti_schedule():
    """आरती वेळापत्रक सूची"""
    aartis = AartiSchedule.query.order_by(AartiSchedule.display_order.asc()).all()
    return render_template('admin/aarti_manage.html', aartis=aartis)

@admin_bp.route('/aarti-schedule/add', methods=['POST'])
@login_required
def add_aarti():
    """नवीन आरती वेळापत्रक जोडणे"""
    name = request.form.get('aarti_name', '').strip()
    start_time = request.form.get('start_time', '').strip()
    end_time = request.form.get('end_time', '').strip()
    marathi_time = request.form.get('marathi_time', '').strip()
    description = request.form.get('description', '').strip()
    order = int(request.form.get('display_order', 1))

    if not name or not start_time or not marathi_time:
        flash('कृपया आरतीचे नाव आणि वेळा अचूक भरा.', 'danger')
        return redirect(url_for('admin.aarti_schedule'))

    new_aarti = AartiSchedule(
        aarti_name=name,
        start_time=start_time,
        end_time=end_time,
        marathi_time=marathi_time,
        description=description,
        display_order=order,
        is_active=True
    )
    db.session.add(new_aarti)
    db.session.commit()

    log_admin_action('CREATE', 'AARTI_SCHEDULE', new_aarti.id, f"नवीन आरती '{name}' जोडली.")
    flash(f"नवीन आरती '{name}' वेळापत्रकात जोडली गेली आहे.", 'success')
    return redirect(url_for('admin.aarti_schedule'))

@admin_bp.route('/aarti-schedule/edit/<int:aarti_id>', methods=['POST'])
@login_required
def edit_aarti(aarti_id):
    """विद्यमान आरती संपादन"""
    aarti = db.session.get(AartiSchedule, aarti_id)
    if not aarti:
        flash('आरती नोंद सापडली नाही.', 'danger')
        return redirect(url_for('admin.aarti_schedule'))

    aarti.aarti_name = request.form.get('aarti_name', '').strip()
    aarti.start_time = request.form.get('start_time', '').strip()
    aarti.end_time = request.form.get('end_time', '').strip()
    aarti.marathi_time = request.form.get('marathi_time', '').strip()
    aarti.description = request.form.get('description', '').strip()
    aarti.display_order = int(request.form.get('display_order', aarti.display_order))
    aarti.is_active = bool(request.form.get('is_active'))

    db.session.commit()
    log_admin_action('UPDATE', 'AARTI_SCHEDULE', aarti.id, f"आरती '{aarti.aarti_name}' संपादन केली.")
    flash(f"आरती '{aarti.aarti_name}' चे बदल जतन करण्यात आले.", 'success')
    return redirect(url_for('admin.aarti_schedule'))

@admin_bp.route('/aarti-schedule/delete/<int:aarti_id>', methods=['POST'])
@login_required
def delete_aarti(aarti_id):
    """आरती वेळापत्रकातून काढणे"""
    aarti = db.session.get(AartiSchedule, aarti_id)
    if aarti:
        name = aarti.aarti_name
        db.session.delete(aarti)
        db.session.commit()
        log_admin_action('DELETE', 'AARTI_SCHEDULE', aarti_id, f"आरती '{name}' काढली.")
        flash(f"आरती '{name}' वेळापत्रकातून काढली गेली.", 'warning')
    return redirect(url_for('admin.aarti_schedule'))

# -------------------------------------------------------------
# ५. मंदिर संस्थानाची माहिती व कागदपत्रे व्यवस्थापन (Trust Details)
# -------------------------------------------------------------

@admin_bp.route('/trust', methods=['GET', 'POST'])
@login_required
def manage_trust():
    """संस्थान माहिती संपादन"""
    trust = TrustDetails.query.first()
    documents = PublicDocument.query.all()

    if request.method == 'POST':
        if not trust:
            trust = TrustDetails()
            db.session.add(trust)

        trust.trust_name = request.form.get('trust_name', '').strip()
        trust.establishment_year = request.form.get('establishment_year', '').strip()
        trust.registration_number = request.form.get('registration_number', '').strip()
        trust.introduction = request.form.get('introduction', '').strip()
        trust.history = request.form.get('history', '').strip()
        trust.address = request.form.get('address', '').strip()
        trust.helpline_phone = request.form.get('helpline_phone', '').strip()
        trust.contact_email = request.form.get('contact_email', '').strip()
        trust.visiting_hours = request.form.get('visiting_hours', '').strip()

        db.session.commit()
        log_admin_action('UPDATE', 'TRUST_DETAILS', trust.id, "संस्थान माहिती अद्ययावत केली.")
        flash('संस्थान माहिती यशस्वीरित्या जतन करण्यात आली!', 'success')
        return redirect(url_for('admin.manage_trust'))

    return render_template('admin/trust_manage.html', trust=trust, documents=documents)

@admin_bp.route('/trust/documents/add', methods=['POST'])
@login_required
def add_document():
    """पारदर्शकता कागदपत्र जोडणे"""
    title = request.form.get('title', '').strip()
    doc_type = request.form.get('document_type', '').strip()
    pub_year = request.form.get('published_year', '').strip()

    if title and doc_type:
        doc = PublicDocument(
            title=title,
            document_type=doc_type,
            published_year=pub_year,
            file_path="docs/sample_report.pdf",
            is_public=True
        )
        db.session.add(doc)
        db.session.commit()
        log_admin_action('CREATE', 'PUBLIC_DOCUMENT', doc.id, f"कागदपत्र '{title}' जोडले.")
        flash(f"कागदपत्र '{title}' जोडले गेले.", 'success')
    return redirect(url_for('admin.manage_trust'))

@admin_bp.route('/trust/documents/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    """कागदपत्र काढणे"""
    doc = db.session.get(PublicDocument, doc_id)
    if doc:
        db.session.delete(doc)
        db.session.commit()
        flash('कागदपत्र काढण्यात आले.', 'warning')
    return redirect(url_for('admin.manage_trust'))

# -------------------------------------------------------------
# ६. अध्यक्षांचा संदेश व्यवस्थापन (Chairperson Message)
# -------------------------------------------------------------

@admin_bp.route('/chairperson', methods=['GET', 'POST'])
@login_required
def manage_chairperson():
    """अध्यक्षांचा संदेश व्यवस्थापन"""
    chairperson = ChairpersonMessage.query.first()

    if request.method == 'POST':
        if not chairperson:
            chairperson = ChairpersonMessage()
            db.session.add(chairperson)

        chairperson.chairperson_name = request.form.get('chairperson_name', '').strip()
        chairperson.designation = request.form.get('designation', 'अध्यक्ष').strip()
        chairperson.photograph = request.form.get('photograph', 'images/default-trustee.svg').strip()
        chairperson.message = request.form.get('message', '').strip()
        chairperson.vision = request.form.get('vision', '').strip()

        db.session.commit()
        log_admin_action('UPDATE', 'CHAIRPERSON_MESSAGE', chairperson.id, "अध्यक्षांचा संदेश अद्ययावत केला.")
        flash('अध्यक्षांचा संदेश यशस्वीरित्या जतन करण्यात आला!', 'success')
        return redirect(url_for('admin.manage_chairperson'))

    return render_template('admin/chairperson_manage.html', chairperson=chairperson)

# -------------------------------------------------------------
# ७. विश्वस्त मंडळ व्यवस्थापन (Trust Members CMS)
# -------------------------------------------------------------

@admin_bp.route('/members')
@login_required
def manage_members():
    """विश्वस्त मंडळ यादी"""
    members = TrustMember.query.order_by(TrustMember.display_order.asc()).all()
    return render_template('admin/members_manage.html', members=members)

@admin_bp.route('/members/add', methods=['POST'])
@login_required
def add_member():
    """नवीन विश्वस्त जोडणे"""
    name = request.form.get('full_name', '').strip()
    desig = request.form.get('designation', 'विश्वस्त').strip()
    photo = request.form.get('photograph', 'images/default-trustee.svg').strip()
    desc = request.form.get('description', '').strip()
    order = int(request.form.get('display_order', 9))

    if name and desig:
        member = TrustMember(
            full_name=name,
            designation=desig,
            photograph=photo,
            description=desc,
            display_order=order,
            is_active=True
        )
        db.session.add(member)
        db.session.commit()
        log_admin_action('CREATE', 'TRUST_MEMBER', member.id, f"नवीन विश्वस्त '{name}' जोडले.")
        flash(f"विश्वस्त '{name}' यांची नोंद यशस्वीरित्या जोडली.", 'success')

    return redirect(url_for('admin.manage_members'))

@admin_bp.route('/members/edit/<int:member_id>', methods=['POST'])
@login_required
def edit_member(member_id):
    """विश्वस्त संपादन"""
    member = db.session.get(TrustMember, member_id)
    if not member:
        flash('विश्वस्त नोंद सापडली नाही.', 'danger')
        return redirect(url_for('admin.manage_members'))

    member.full_name = request.form.get('full_name', '').strip()
    member.designation = request.form.get('designation', '').strip()
    member.photograph = request.form.get('photograph', '').strip()
    member.description = request.form.get('description', '').strip()
    member.display_order = int(request.form.get('display_order', member.display_order))
    member.is_active = bool(request.form.get('is_active'))

    db.session.commit()
    log_admin_action('UPDATE', 'TRUST_MEMBER', member.id, f"विश्वस्त '{member.full_name}' संपादन केले.")
    flash(f"विश्वस्त '{member.full_name}' चे बदल जतन करण्यात आले.", 'success')
    return redirect(url_for('admin.manage_members'))

@admin_bp.route('/members/delete/<int:member_id>', methods=['POST'])
@login_required
def delete_member(member_id):
    """विश्वस्त काढणे"""
    member = db.session.get(TrustMember, member_id)
    if member:
        name = member.full_name
        db.session.delete(member)
        db.session.commit()
        log_admin_action('DELETE', 'TRUST_MEMBER', member_id, f"विश्वस्त '{name}' काढले.")
        flash(f"विश्वस्त '{name}' काढण्यात आले.", 'warning')
    return redirect(url_for('admin.manage_members'))

# -------------------------------------------------------------
# ८. छायाचित्र संग्रह व्यवस्थापन (Gallery CMS)
# -------------------------------------------------------------

@admin_bp.route('/gallery')
@login_required
def manage_gallery():
    """छायाचित्र संग्रह यादी"""
    images = GalleryImage.query.order_by(GalleryImage.uploaded_at.desc()).all()
    return render_template('admin/gallery_manage.html', images=images)

@admin_bp.route('/gallery/add', methods=['POST'])
@login_required
def add_gallery_image():
    """नवीन छायाचित्र जोडणे"""
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'aarti').strip()
    path = request.form.get('image_path', 'images/sample-gallery.svg').strip()
    desc = request.form.get('description', '').strip()

    if title and category and path:
        img = GalleryImage(
            title=title,
            category=category,
            image_path=path,
            description=desc
        )
        db.session.add(img)
        db.session.commit()
        log_admin_action('CREATE', 'GALLERY_IMAGE', img.id, f"छायाचित्र '{title}' जोडले.")
        flash(f"छायाचित्र '{title}' संग्रहात जोडले गेले.", 'success')

    return redirect(url_for('admin.manage_gallery'))

@admin_bp.route('/gallery/delete/<int:image_id>', methods=['POST'])
@login_required
def delete_gallery_image(image_id):
    """छायाचित्र काढणे"""
    img = db.session.get(GalleryImage, image_id)
    if img:
        db.session.delete(img)
        db.session.commit()
        flash('छायाचित्र संग्रहातून काढले गेले.', 'warning')
    return redirect(url_for('admin.manage_gallery'))

# -------------------------------------------------------------
# ९. बातम्या व उपक्रम व्यवस्थापन (Updates CMS)
# -------------------------------------------------------------

@admin_bp.route('/updates')
@login_required
def manage_updates():
    """बातम्या व उपक्रम यादी"""
    updates = TrustUpdate.query.order_by(TrustUpdate.published_at.desc()).all()
    return render_template('admin/updates_manage.html', updates=updates)

@admin_bp.route('/updates/add', methods=['POST'])
@login_required
def add_update():
    """नवीन बातमी किंवा परिपत्रक जोडणे"""
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'धार्मिक उत्सव').strip()
    desc = request.form.get('description', '').strip()

    if title and desc:
        upd = TrustUpdate(
            title=title,
            category=category,
            description=desc,
            is_published=True
        )
        db.session.add(upd)
        db.session.commit()
        log_admin_action('CREATE', 'TRUST_UPDATE', upd.id, f"बातमी '{title}' प्रसिद्ध केली.")
        flash(f"बातमी '{title}' प्रसिद्ध केली गेली.", 'success')

    return redirect(url_for('admin.manage_updates'))

@admin_bp.route('/updates/edit/<int:update_id>', methods=['POST'])
@login_required
def edit_update(update_id):
    """बातमी संपादन"""
    upd = db.session.get(TrustUpdate, update_id)
    if upd:
        upd.title = request.form.get('title', '').strip()
        upd.category = request.form.get('category', '').strip()
        upd.description = request.form.get('description', '').strip()
        upd.is_published = bool(request.form.get('is_published'))
        db.session.commit()
        flash('बातमी यशस्वीरित्या अद्ययावत केली गेली.', 'success')
    return redirect(url_for('admin.manage_updates'))

@admin_bp.route('/updates/delete/<int:update_id>', methods=['POST'])
@login_required
def delete_update(update_id):
    """बातमी काढणे"""
    upd = db.session.get(TrustUpdate, update_id)
    if upd:
        db.session.delete(upd)
        db.session.commit()
        flash('बातमी काढण्यात आली.', 'warning')
    return redirect(url_for('admin.manage_updates'))

# -------------------------------------------------------------
# १०. प्रशासक खाती व सुरक्षा (Admin Users & Password Management)
# -------------------------------------------------------------

@admin_bp.route('/admins')
@login_required
def manage_admins():
    """प्रशासक खाती यादी"""
    admins = AdminUser.query.all()
    audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(15).all()
    return render_template('admin/admins_manage.html', admins=admins, audit_logs=audit_logs)

@admin_bp.route('/admins/add', methods=['POST'])
@login_required
def add_admin():
    """नवीन प्रशासक जोडणे"""
    username = request.form.get('username', '').strip()
    full_name = request.form.get('full_name', '').strip()
    role = request.form.get('role', 'trustee').strip()
    password = request.form.get('password', '')

    if username and password:
        existing = AdminUser.query.filter_by(username=username).first()
        if existing:
            flash(f"वापरकर्ता नाव '{username}' आधीच वापरात आहे.", 'danger')
            return redirect(url_for('admin.manage_admins'))

        new_admin = AdminUser(
            username=username,
            full_name=full_name,
            role=role
        )
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()
        log_admin_action('CREATE', 'ADMIN_USER', new_admin.id, f"नवीन प्रशासक खाते '{username}' तयार केले.")
        flash(f"प्रशासक '{username}' चे खाते यशस्वीरित्या तयार झाले.", 'success')

    return redirect(url_for('admin.manage_admins'))

@admin_bp.route('/admins/change-password/<int:admin_id>', methods=['POST'])
@login_required
def change_password(admin_id):
    """पासवर्ड बदलणे"""
    admin = db.session.get(AdminUser, admin_id)
    new_pwd = request.form.get('new_password', '')
    if admin and new_pwd and len(new_pwd) >= 6:
        admin.set_password(new_pwd)
        db.session.commit()
        log_admin_action('UPDATE', 'ADMIN_PASSWORD', admin.id, f"प्रशासक {admin.username} चा पासवर्ड बदलला.")
        flash(f"प्रशासक {admin.username} चा पासवर्ड अद्ययावत झाला.", 'success')
    else:
        flash('पासवर्ड किमान ६ अक्षरांचा असणे आवश्यक आहे.', 'danger')
    return redirect(url_for('admin.manage_admins'))
