import os
import sys
import json
import hmac
import hashlib
import unittest
from app import create_app
from app.extensions import db
from app.models.donation import Donor, Donation, Payment, Receipt, WebhookEvent
from app.models.trust import TrustDetails
from app.services.marathi_num_to_words import number_to_marathi_words
from app.services.payment_service import PaymentService

class DonationSystemTests(unittest.TestCase):
    """
    ऑनलाइन देणगी प्रणालीची सर्वसमावेशक चाचणी
    (Razorpay, स्वाक्षरी पडताळणी, इडेम्पोटन्सी, ReportLab PDF, Webhook)
    """

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # आवश्यक विश्वस्त संस्था माहिती
        trust = TrustDetails(
            trust_name="श्री देवस्थान विश्वस्त व्यवस्था",
            registration_number="महा./१२३४/ट्रस्ट",
            address="तीर्थक्षेत्र देवस्थान, महाराष्ट्र"
        )
        db.session.add(trust)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_marathi_number_to_words(self):
        """मराठी संख्या-ते-शब्द अचूकता चाचणी"""
        self.assertEqual(number_to_marathi_words(101), "एकशे एक रुपये फक्त")
        self.assertEqual(number_to_marathi_words(501), "पाचशे एक रुपये फक्त")
        self.assertEqual(number_to_marathi_words(1001), "एक हजार एक रुपये फक्त")
        self.assertEqual(number_to_marathi_words(5001), "पाच हजार एक रुपये फक्त")
        self.assertEqual(number_to_marathi_words(50000), "पन्नास हजार रुपये फक्त")
        sys.stdout.buffer.write(b'[PASSED] 1. Marathi Number-To-Words tested\n')

    def test_02_create_order_validation(self):
        """देणगी ऑर्डर निर्मिती व सर्व्हर प्रमाणीकरण चाचणी"""
        # किमान रक्कम प्रमाणीकरण (< ₹१०)
        res = self.client.post('/api/donations/create-order', json={
            'full_name': 'समीर पाटील',
            'email': 'sameer@example.com',
            'phone': '9876543210',
            'amount': 5
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn('किमान देणगी रक्कम', res.get_json()['message'])

        # वैध देणगी ऑर्डर
        res_valid = self.client.post('/api/donations/create-order', json={
            'full_name': 'समीर पाटील',
            'email': 'sameer@example.com',
            'phone': '9876543210',
            'amount': 501
        })
        self.assertEqual(res_valid.status_code, 200)
        data = res_valid.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['amount_paise'], 50100)
        self.assertTrue(data['order_id'].startswith('order_'))
        self.assertTrue(data['receipt_number'].startswith('STT-'))
        sys.stdout.buffer.write(b'[PASSED] 2. Order creation and validation tested\n')

    def test_03_successful_payment_and_receipt(self):
        """यशस्वी पेमेंट स्वाक्षरी, PAID स्थिती व ReportLab PDF निर्मिती"""
        order_res = self.client.post('/api/donations/create-order', json={
            'full_name': 'राजेश दत्तात्रय कुलकर्णी',
            'email': 'rajesh@example.com',
            'phone': '9822012345',
            'amount': 501
        })
        order_data = order_res.get_json()
        order_id = order_data['order_id']
        payment_id = 'pay_test_succ_123'

        secret = 'temple_secret_key'
        self.app.config['RAZORPAY_KEY_SECRET'] = secret
        msg = f"{order_id}|{payment_id}".encode('utf-8')
        valid_sig = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).hexdigest()

        verify_res = self.client.post('/api/donations/verify-payment', json={
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': valid_sig,
            'donation_id': order_data['donation_id']
        })
        self.assertEqual(verify_res.status_code, 200)
        v_data = verify_res.get_json()
        self.assertTrue(v_data['success'])
        receipt_no = v_data['receipt_number']

        # डेटाबेस तपासणी
        donation = Donation.query.filter_by(receipt_number=receipt_no).first()
        self.assertIsNotNone(donation)
        self.assertEqual(donation.status, 'PAID')
        self.assertTrue(donation.payment.signature_verified)
        self.assertIsNotNone(donation.receipt)
        self.assertTrue(os.path.exists(donation.receipt.pdf_path))

        # PDF डाऊनलोड तपासणी
        dl_res = self.client.get(f'/receipts/download/{receipt_no}')
        self.assertEqual(dl_res.status_code, 200)
        self.assertEqual(dl_res.content_type, 'application/pdf')
        self.assertGreater(len(dl_res.data), 1000)
        sys.stdout.buffer.write(b'[PASSED] 3. Successful payment & ReportLab PDF receipt tested\n')

    def test_04_tampered_signature_rejection(self):
        """बनावट/चुकीच्या स्वाक्षरीचा तात्काळ नकार चाचणी"""
        order_res = self.client.post('/api/donations/create-order', json={
            'full_name': 'अशोक पवार',
            'email': 'ashok@example.com',
            'phone': '9811122233',
            'amount': 1001
        })
        order_data = order_res.get_json()

        self.app.config['RAZORPAY_KEY_SECRET'] = 'secret_key_123'
        fake_sig = "fake_tampered_signature_hex_code_12345"

        verify_res = self.client.post('/api/donations/verify-payment', json={
            'razorpay_order_id': order_data['order_id'],
            'razorpay_payment_id': 'pay_fake_999',
            'razorpay_signature': fake_sig,
            'donation_id': order_data['donation_id']
        })
        self.assertEqual(verify_res.status_code, 400)
        self.assertIn('पडताळणी अयशस्वी', verify_res.get_json()['message'])

        donation = db.session.get(Donation, order_data['donation_id'])
        self.assertEqual(donation.status, 'FAILED')
        self.assertIsNone(donation.receipt)
        sys.stdout.buffer.write(b'[PASSED] 4. Tampered signature rejection tested\n')

    def test_05_idempotent_duplicate_protection(self):
        """इडेम्पोटन्सी चाचणी: एकाच पेमेंटवर दुहेरी पावती बनत नाही"""
        order_res = self.client.post('/api/donations/create-order', json={
            'full_name': 'गणेश शिंदे',
            'email': 'ganesh@example.com',
            'phone': '9844455566',
            'amount': 101
        })
        order_data = order_res.get_json()
        order_id = order_data['order_id']
        payment_id = 'pay_idem_001'

        secret = 'idem_secret'
        self.app.config['RAZORPAY_KEY_SECRET'] = secret
        msg = f"{order_id}|{payment_id}".encode('utf-8')
        sig = hmac.new(secret.encode('utf-8'), msg, hashlib.sha256).hexdigest()

        # पहिली यशस्वी पडताळणी
        self.client.post('/api/donations/verify-payment', json={
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': sig,
            'donation_id': order_data['donation_id']
        })

        # पुन्हा त्याच देणगीवर दुसरी पडताळणी कॉल करणे
        second_res = self.client.post('/api/donations/verify-payment', json={
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': sig,
            'donation_id': order_data['donation_id']
        })
        self.assertEqual(second_res.status_code, 200)

        # डेटाबेसमध्ये पावती १ च असायला हवी
        receipts_count = Receipt.query.filter_by(donation_id=order_data['donation_id']).count()
        self.assertEqual(receipts_count, 1)
        sys.stdout.buffer.write(b'[PASSED] 5. Idempotent duplicate verification tested\n')

    def test_06_razorpay_webhook_idempotency(self):
        """Razorpay Webhook व दुहेरी इव्हेंट संरक्षण चाचणी"""
        order_info = PaymentService.create_donation_order(
            full_name='प्रशांत देशपांडे',
            email='prashant@example.com',
            phone='9899988877',
            amount=5001
        )
        order_id = order_info['order_id']

        webhook_payload = {
            'id': 'evt_razorpay_webhook_123',
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_hook_captured_999',
                        'order_id': order_id,
                        'amount': 500100,
                        'status': 'captured'
                    }
                }
            }
        }

        # १. पहिला वेबहुक कॉल
        res1 = self.client.post('/api/donations/razorpay-webhook', json=webhook_payload)
        self.assertEqual(res1.status_code, 200)
        self.assertTrue(res1.get_json()['success'])

        # २. तोच वेबहुक इव्हेंट पुन्हा आला (Duplicate Webhook Delivery)
        res2 = self.client.post('/api/donations/razorpay-webhook', json=webhook_payload)
        self.assertEqual(res2.status_code, 200)
        self.assertIn('आधीच प्रक्रिया', res2.get_json()['message'])

        # ३. देणगी तपासणी
        donation = Donation.query.filter_by(receipt_number=order_info['receipt_number']).first()
        self.assertEqual(donation.status, 'PAID')
        event_count = WebhookEvent.query.filter_by(event_id='evt_razorpay_webhook_123').count()
        self.assertEqual(event_count, 1)
        sys.stdout.buffer.write(b'[PASSED] 6. Razorpay Webhook duplicate event idempotency tested\n')

if __name__ == '__main__':
    unittest.main()
