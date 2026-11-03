import sys
import unittest
from tests.test_donations import (
    test_marathi_number_to_words,
    test_create_order_validation,
    test_successful_payment_and_receipt_generation,
    test_failed_signature_payment,
    test_idempotent_duplicate_processing,
    test_razorpay_webhook_idempotency,
    app_instance
)

class DonationTestCase(unittest.TestCase):
    def setUp(self):
        # Setup test app fixture
        self.app_gen = app_instance()
        self.app = next(self.app_gen)
        self.client = self.app.test_client()

    def tearDown(self):
        try:
            next(self.app_gen)
        except StopIteration:
            pass

    def test_words(self):
        test_marathi_number_to_words()
        sys.stdout.buffer.write(b'[PASSED] 1. Marathi Number-To-Words tested\n')

    def test_validation(self):
        test_create_order_validation(self.client)
        sys.stdout.buffer.write(b'[PASSED] 2. Order validation tested\n')

    def test_successful_flow(self):
        test_successful_payment_and_receipt_generation(self.client, self.app)
        sys.stdout.buffer.write(b'[PASSED] 3. Successful payment & ReportLab PDF receipt tested\n')

    def test_failed_signature(self):
        test_failed_signature_payment(self.client, self.app)
        sys.stdout.buffer.write(b'[PASSED] 4. Tampered signature rejection tested\n')

    def test_idempotency(self):
        test_idempotent_duplicate_processing(self.client, self.app)
        sys.stdout.buffer.write(b'[PASSED] 5. Idempotent duplicate verification tested\n')

    def test_webhook(self):
        test_razorpay_webhook_idempotency(self.client, self.app)
        sys.stdout.buffer.write(b'[PASSED] 6. Razorpay Webhook duplicate event idempotency tested\n')

if __name__ == '__main__':
    unittest.main()
