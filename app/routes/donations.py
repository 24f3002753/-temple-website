import os
from flask import Blueprint, request, jsonify, send_file, current_app, url_for
from app.extensions import csrf
from app.services.payment_service import PaymentService
from app.models.donation import Donation, Receipt

donations_bp = Blueprint('donations', __name__)

@donations_bp.route('/api/donations/create-order', methods=['POST'])
def create_order():
    """
    देणगी ऑर्डर निर्मिती API (Razorpay Order Creation Endpoint)
    """
    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    amount = data.get('amount')

    if not full_name or not email or not phone or not amount:
        return jsonify({
            'success': False,
            'message': 'कृपया सर्व आवश्यक माहिती अचूक भरा.'
        }), 400

    try:
        amount_val = float(amount)
        if amount_val < 10:
            return jsonify({
                'success': False,
                'message': 'किमान देणगी रक्कम ₹१० असणे आवश्यक आहे.'
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'message': 'अवैध देणगी रक्कम. कृपया योग्य रक्कम प्रविष्ट करा.'
        }), 400

    try:
        order_info = PaymentService.create_donation_order(
            full_name=full_name,
            email=email,
            phone=phone,
            amount=amount_val
        )
        return jsonify({
            'success': True,
            **order_info,
            'currency': 'INR'
        }), 200

    except Exception as e:
        current_app.logger.error(f"ऑर्डर निर्मिती त्रुटी: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"ऑर्डर तयार करताना त्रुटी आली: {str(e)}"
        }), 500


@donations_bp.route('/api/donations/verify-payment', methods=['POST'])
def verify_payment():
    """
    Razorpay पेमेंट पडताळणी API (Payment Signature Verification & Receipt Gen)
    """
    data = request.get_json() or {}
    order_id = data.get('razorpay_order_id')
    payment_id = data.get('razorpay_payment_id')
    signature = data.get('razorpay_signature')
    donation_id = data.get('donation_id')

    if not payment_id or (not order_id and not donation_id):
        return jsonify({
            'success': False,
            'message': 'अपूर्ण पेमेंट माहिती प्राप्त झाली.'
        }), 400

    try:
        donation, receipt = PaymentService.complete_donation_payment(
            order_id=order_id,
            payment_id=payment_id,
            signature=signature,
            donation_id=donation_id
        )

        redirect_url = url_for(
            'public.donation_success',
            donor_name=donation.donor.full_name,
            amount=f"{int(donation.amount):,}",
            receipt_number=donation.receipt_number,
            payment_id=payment_id
        )

        return jsonify({
            'success': True,
            'message': 'देणगी यशस्वीरित्या पडताळली गेली आहे आणि अधिकृत पावती तयार झाली आहे.',
            'receipt_number': donation.receipt_number,
            'redirect_url': redirect_url
        }), 200

    except ValueError as ve:
        return jsonify({
            'success': False,
            'message': str(ve)
        }), 400
    except Exception as e:
        current_app.logger.error(f"पेमेंट पडताळणी दरम्यान त्रुटी: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'पेमेंट पडताळणी दरम्यान तांत्रिक अडचण आली. कृपया ग्राहक सेवेशी संपर्क साधा.'
        }), 500


@donations_bp.route('/api/donations/razorpay-webhook', methods=['POST'])
@csrf.exempt
def razorpay_webhook():
    """
    Razorpay Webhook Endpoint (इडेम्पोटन्सी संरक्षण व स्वयंचलित पुष्टीकरण)
    """
    raw_payload = request.get_data()
    signature_header = request.headers.get('X-Razorpay-Signature', '')
    event_data = request.get_json() or {}

    response_data, status_code = PaymentService.handle_webhook(
        event_data=event_data,
        raw_payload=raw_payload,
        signature_header=signature_header
    )
    return jsonify(response_data), status_code


@donations_bp.route('/api/donations/status/<int:donation_id>')
def get_donation_status(donation_id):
    """
    सुरक्षित देणगी स्थिती तपासणी (Read-only status check)
    """
    donation = Donation.query.get_or_404(donation_id)
    return jsonify({
        'donation_id': donation.id,
        'status': donation.status,
        'amount': float(donation.amount),
        'receipt_number': donation.receipt_number,
        'is_paid': donation.status == 'PAID'
    })


@donations_bp.route('/receipts/download/<receipt_number>')
def download_receipt(receipt_number):
    """
    अधिकृत देणगी पावती PDF डाऊनलोड (Download Receipt Endpoint)
    """
    receipt = Receipt.query.filter_by(receipt_number=receipt_number).first()
    if receipt and os.path.exists(receipt.pdf_path):
        return send_file(
            receipt.pdf_path,
            as_attachment=True,
            download_name=f"ShreeTemple_Receipt_{receipt_number}.pdf",
            mimetype='application/pdf'
        )

    # पावती फाईल तपासणी
    receipt_dir = current_app.config.get('RECEIPT_FOLDER')
    pdf_path = os.path.join(receipt_dir, f"{receipt_number}.pdf")
    if os.path.exists(pdf_path):
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"ShreeTemple_Receipt_{receipt_number}.pdf",
            mimetype='application/pdf'
        )

    return f"""
    <html>
        <head><meta charset="utf-8"><title>पावती आढळली नाही</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
            <h2 style="color: #7A0000;">श्री देवस्थान विश्वस्त व्यवस्था</h2>
            <p style="color: #C62828; font-size: 1.2em;">पावती क्रमांक <strong>{receipt_number}</strong> ची PDF फाईल आढळली नाही.</p>
            <p>कृपया आपल्या नोंदणीकृत ईमेलवर आलेली पावती तपासा अथवा प्रशासनाशी संपर्क साधा.</p>
            <br>
            <a href="/" style="padding: 10px 20px; background: #E65100; color: #FFF; text-decoration: none; border-radius: 5px;">मुख्यपृष्ठावर परत जा</a>
        </body>
    </html>
    """, 404
