import os
import sys
import unittest
from app import create_app
from app.extensions import db
from app.models.admin import AdminUser
from app.models.trust import TrustDetails

class SecurityAuditTests(unittest.TestCase):
    """
    वेबसाइट सुरक्षा आणि प्रवेश नियंत्रण चाचणी (Security Audit Test Suite)
    """

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # १. सक्रिय ॲडमिन
        admin = AdminUser(username='active_admin', full_name='सक्रिय व्यवस्थापक', role='superadmin')
        admin.set_password('SecurePass@123')
        db.session.add(admin)

        # २. निष्क्रिय ॲडमिन (Disabled account)
        inactive = AdminUser(username='inactive_admin', full_name='निलंबित व्यवस्थापक', role='editor', is_active=False)
        inactive.set_password('SecurePass@123')
        db.session.add(inactive)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_01_unauthorized_admin_access_redirect(self):
        """अनधिकृत वापरकर्त्याला ॲडमिन राऊट्सवर थेट प्रवेश नाकारला जातो (Redirect to Login)"""
        protected_routes = [
            '/admin/dashboard',
            '/admin/donations',
            '/admin/reports',
            '/admin/live-stream',
            '/admin/aarti-schedule',
            '/admin/trust',
            '/admin/chairperson',
            '/admin/members',
            '/admin/gallery',
            '/admin/updates',
            '/admin/admins'
        ]

        for route in protected_routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 302, f"Route {route} allowed unauthorized access!")
            self.assertIn('/admin/login', res.headers['Location'])

        sys.stdout.buffer.write(b'[PASSED] 1. All protected admin routes require authentication\n')

    def test_02_password_hashing_security(self):
        """पासवर्ड कधीही प्लेनटेक्स्टमध्ये साठवला जात नाही व हॅश सुरक्षित आहे"""
        admin = AdminUser.query.filter_by(username='active_admin').first()
        self.assertNotEqual(admin.password_hash, 'SecurePass@123')
        self.assertTrue(admin.password_hash.startswith('scrypt:') or admin.password_hash.startswith('pbkdf2:'))
        self.assertTrue(admin.check_password('SecurePass@123'))
        self.assertFalse(admin.check_password('WrongPass@123'))
        sys.stdout.buffer.write(b'[PASSED] 2. Password hashing & verification validated\n')

    def test_03_inactive_admin_login_rejected(self):
        """निष्क्रिय (Disabled) प्रशासक खात्याला लॉगिन नकार"""
        res = self.client.post('/admin/login', data={
            'username': 'inactive_admin',
            'password': 'SecurePass@123'
        }, follow_redirects=True)
        self.assertIn('अवैध वापरकर्ता नाव', res.data.decode('utf-8'))
        sys.stdout.buffer.write(b'[PASSED] 3. Disabled admin account login blocked\n')

    def test_04_tampered_webhook_security(self):
        """बनावट/खोट्या Razorpay Webhook स्वाक्षरीचा तात्काळ नकार"""
        self.app.config['RAZORPAY_WEBHOOK_SECRET'] = 'webhook_secret_key_prod'
        fake_payload = b'{"event": "payment.captured", "id": "evt_fake_999"}'
        headers = {
            'X-Razorpay-Signature': 'invalid_signature_hash_here',
            'Content-Type': 'application/json'
        }

        res = self.client.post('/api/donations/razorpay-webhook', data=fake_payload, headers=headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn('अवैध वेबहुक स्वाक्षरी', res.get_json().get('message', ''))
        sys.stdout.buffer.write(b'[PASSED] 4. Tampered webhook signature blocked with 400 Bad Request\n')

if __name__ == '__main__':
    unittest.main()
