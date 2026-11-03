import os
import sys
import unittest

def run_complete_test_suite():
    """
    संपूर्ण मंदिर ट्रस्ट वेबसाइट चाचणी संच (Master Test Runner)
    """
    sys.stdout.buffer.write(b"============================================================\n")
    sys.stdout.buffer.write(b"SHREE TEMPLE TRUST - COMPLETE AUTOMATED SYSTEM TEST SUITE\n")
    sys.stdout.buffer.write(b"============================================================\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # सर्व चाचण्या जोडा
    from tests.test_donations import DonationSystemTests
    from tests.test_security import SecurityAuditTests

    suite.addTests(loader.loadTestsFromTestCase(DonationSystemTests))
    suite.addTests(loader.loadTestsFromTestCase(SecurityAuditTests))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        sys.stdout.buffer.write(b"\n============================================================\n")
        sys.stdout.buffer.write(b"ALL TESTS PASSED! 100% PRODUCTION READY AND VERIFIED.\n")
        sys.stdout.buffer.write(b"============================================================\n")
        return 0
    else:
        sys.stdout.buffer.write(b"\n[ERROR] SOME TESTS FAILED!\n")
        return 1

if __name__ == '__main__':
    exit_code = run_complete_test_suite()
    sys.exit(exit_code)
