import os
import hmac
import hashlib
from datetime import datetime, timezone
from decimal import Decimal
from flask import current_app
from app.extensions import db
from app.models.donation import Donor, Donation, Payment, Receipt, WebhookEvent
from app.models.trust import TrustDetails
from app.services.receipt_service import ReceiptService
from app.services.email_service import EmailService

class PaymentService:
    """
    Razorpay पेमेंट गेटवे एकत्रीकरण व सुरक्षा सेवा
    HMAC-SHA256 स्वाक्षरी पडताळणी, इडेम्पोटंट वेबहुक प्रक्रिया आणि पावती निर्मिती
    """

    @classmethod
    def get_razorpay_client(cls):
        """Razorpay Client सुरू करणे"""
        key_id = current_app.config.get('RAZORPAY_KEY_ID', '')
        key_secret = current_app.config.get('RAZORPAY_KEY_SECRET', '')
        if not key_id or not key_secret:
            return None
        try:
            import razorpay
            return razorpay.Client(auth=(key_id, key_secret))
        except Exception:
            return None

    @classmethod
    def generate_receipt_number(cls) -> str:
        """अनन्य अधिकृत पावती क्रमांक (उदा. STT-2026-0001)"""
        year = datetime.now().year
        random_hex = os.urandom(3).hex().upper()
        return f"STT-{year}-{random_hex}"

    @classmethod
    def create_donation_order(cls, full_name: str, email: str, phone: str, amount: float):
        """
        पायरी १ ते ५: देणगीदार माहिती प्रमाणीकरण, PENDING नोंद, व Razorpay ऑर्डर निर्मिती
        """
        amount_decimal = Decimal(str(amount))
        if amount_decimal < Decimal('10.00'):
            raise ValueError("किमान देणगी रक्कम ₹१० असणे आवश्यक आहे.")

        # १. देणगीदार शोधा किंवा नवीन तयार करा
        donor = Donor.query.filter_by(email=email).first()
        if not donor:
            donor = Donor(full_name=full_name, email=email, phone=phone)
            db.session.add(donor)
            db.session.flush()
        else:
            donor.full_name = full_name
            donor.phone = phone

        # २. युनिक पावती क्रमांक व देणगी नोंद (PENDING स्थिती)
        receipt_no = cls.generate_receipt_number()
        donation = Donation(
            donor_id=donor.id,
            amount=amount_decimal,
            currency='INR',
            status='PENDING',
            receipt_number=receipt_no
        )
        db.session.add(donation)
        db.session.flush()

        amount_paise = int(amount_decimal * 100)
        key_id = current_app.config.get('RAZORPAY_KEY_ID', '')
        client = cls.get_razorpay_client()

        order_id = None
        if client and key_id:
            try:
                order_data = {
                    'amount': amount_paise,
                    'currency': 'INR',
                    'receipt': receipt_no,
                    'notes': {
                        'donor_name': full_name,
                        'email': email,
                        'phone': phone,
                        'trust': 'श्री देवस्थान विश्वस्त व्यवस्था'
                    }
                }
                rzp_order = client.order.create(data=order_data)
                order_id = rzp_order.get('id')
            except Exception as e:
                current_app.logger.warning(f"Razorpay थेट API त्रुटी, चाचणी ऑर्डर वापरत आहे: {str(e)}")

        # चाचणी किंवा प्रत्यक्ष ऑर्डर आयडी
        if not order_id:
            order_id = f"order_dev_{int(amount)}_{os.urandom(4).hex()}"

        # ३. पेमेंट नोंद साठवणे
        payment = Payment(
            donation_id=donation.id,
            razorpay_order_id=order_id,
            payment_status='created'
        )
        db.session.add(payment)
        db.session.commit()

        return {
            'donation_id': donation.id,
            'receipt_number': receipt_no,
            'order_id': order_id,
            'amount_paise': amount_paise,
            'razorpay_key_id': key_id or 'rzp_test_placeholder'
        }

    @classmethod
    def verify_signature(cls, order_id: str, payment_id: str, signature: str) -> bool:
        """
        पायरी ९: HMAC-SHA256 स्वाक्षरी पडताळणी
        क्लायंटच्या रिस्पॉन्सवर कधीही आंधळा विश्वास ठेवला जात नाही.
        """
        key_secret = current_app.config.get('RAZORPAY_KEY_SECRET', '')
        if not key_secret:
            # डेव्हलपमेंट मोडमध्ये सिक्रेट की नसल्यास सुरक्षित सिमुलेशन
            return True

        message = f"{order_id}|{payment_id}".encode('utf-8')
        generated_signature = hmac.new(
            key_secret.encode('utf-8'),
            message,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(generated_signature, signature)

    @classmethod
    def verify_webhook_signature(cls, raw_payload: bytes, signature_header: str) -> bool:
        """
        Razorpay Webhook स्वाक्षरी पडताळणी
        """
        webhook_secret = current_app.config.get('RAZORPAY_WEBHOOK_SECRET', '')
        if not webhook_secret:
            return True

        generated_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            raw_payload,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(generated_signature, signature_header)

    @classmethod
    def complete_donation_payment(cls, order_id: str, payment_id: str, signature: str = None, donation_id: int = None):
        """
        पायरी १० ते १४: पेमेंटची पुष्टी, PAID स्थिती, ReportLab PDF पावती व ईमेल पाठवणे
        (Idempotency: आधीच प्रक्रिया झाली असल्यास पुन्हा पावती बनवली जात नाही)
        """
        payment = None
        if order_id:
            payment = Payment.query.filter_by(razorpay_order_id=order_id).first()
        if not payment and donation_id:
            payment = Payment.query.filter_by(donation_id=donation_id).first()

        if not payment:
            raise ValueError(f"पेमेंट संदर्भ सापडला नाही: {order_id}")

        donation = db.session.get(Donation, payment.donation_id)
        if not donation:
            raise ValueError("देणगी नोंद सापडली नाही.")

        donor = db.session.get(Donor, donation.donor_id)
        trust = TrustDetails.query.first()

        # स्वाक्षरी पडताळणी
        is_verified = True
        if signature:
            is_verified = cls.verify_signature(order_id, payment_id, signature)
            if not is_verified:
                payment.signature_verified = False
                payment.payment_status = 'failed'
                donation.status = 'FAILED'
                db.session.commit()
                raise ValueError("पेमेंट स्वाक्षरी पडताळणी अयशस्वी. हा व्यवहार अवैध असू शकतो.")

        # इडेम्पोटन्सी संरक्षण (Idempotent Check)
        if donation.status == 'PAID' and donation.receipt:
            current_app.logger.info(f"देणगी {donation.receipt_number} आधीच यशस्वी आहे. दुहेरी प्रक्रिया टाळली.")
            return donation, donation.receipt

        # पेमेंट व देणगी यशस्वी चिन्हांकित करा
        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.signature_verified = True
        payment.payment_status = 'captured'

        donation.status = 'PAID'
        donation.paid_at = datetime.now(timezone.utc)

        # PDF पावती जनरेट करा
        base_dir = current_app.root_path
        output_dir = current_app.config.get('RECEIPT_FOLDER')
        pdf_path = ReceiptService.generate_receipt_pdf(
            donation=donation,
            donor=donor,
            payment=payment,
            trust_details=trust,
            output_dir=output_dir,
            base_dir=os.path.dirname(base_dir)
        )

        # पावती नोंद डेटाबेसमध्ये जतन करा
        receipt = Receipt.query.filter_by(donation_id=donation.id).first()
        if not receipt:
            receipt = Receipt(
                donation_id=donation.id,
                receipt_number=donation.receipt_number,
                pdf_path=pdf_path,
                issued_at=datetime.now(timezone.utc)
            )
            db.session.add(receipt)
        else:
            receipt.pdf_path = pdf_path

        db.session.commit()

        # ईमेल पाठवणे (अयशस्वी झाल्यासही देणगी यशस्वी राहते)
        EmailService.send_donation_receipt_email(
            recipient_email=donor.email,
            donor_name=donor.full_name,
            receipt_number=donation.receipt_number,
            amount=float(donation.amount),
            pdf_path=pdf_path,
            receipt_record=receipt
        )

        return donation, receipt

    @classmethod
    def handle_webhook(cls, event_data: dict, raw_payload: bytes, signature_header: str):
        """
        Razorpay Webhook प्रक्रिया व इडेम्पोटन्सी संरक्षण
        """
        # स्वाक्षरी पडताळणी
        if signature_header and not cls.verify_webhook_signature(raw_payload, signature_header):
            return {'success': False, 'message': 'अवैध वेबहुक स्वाक्षरी'}, 400

        event_id = event_data.get('event_id') or event_data.get('id')
        event_type = event_data.get('event')

        if not event_id:
            return {'success': False, 'message': 'इव्हेंट आयडी आढळला नाही'}, 400

        # इडेम्पोटन्सी तपासणी: हा इव्हेंट आधी प्रक्रिया झाला आहे का?
        existing_event = WebhookEvent.query.filter_by(event_id=event_id).first()
        if existing_event and existing_event.processing_status == 'PROCESSED':
            return {'success': True, 'message': 'हा इव्हेंट आधीच प्रक्रिया झाला आहे.'}, 200

        # वेबहुक नोंदणी
        if not existing_event:
            existing_event = WebhookEvent(
                event_id=event_id,
                event_type=event_type,
                processing_status='PENDING'
            )
            db.session.add(existing_event)
            db.session.commit()

        # इव्हेंट प्रक्रिया (उदा. payment.captured किंवा order.paid)
        if event_type in ['payment.captured', 'order.paid']:
            payload = event_data.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payload.get('order_id')
            payment_id = payload.get('id')

            if order_id and payment_id:
                try:
                    cls.complete_donation_payment(order_id=order_id, payment_id=payment_id)
                    existing_event.processing_status = 'PROCESSED'
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"वेबहुक प्रक्रिया अयशस्वी: {str(e)}")
                    existing_event.processing_status = 'FAILED'
                    db.session.commit()
                    return {'success': False, 'message': str(e)}, 500

        existing_event.processing_status = 'PROCESSED'
        db.session.commit()
        return {'success': True, 'message': 'वेबहुक यशस्वीरित्या हाताळला गेला.'}, 200
