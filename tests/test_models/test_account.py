import unittest
from datetime import datetime
from domain.models.account import Account, AccountStatus

class TestAccount(unittest.TestCase):
    def setUp(self):
        """Create test account before each test"""
        self.account_id = "ACC123456"
        self.test_account = Account(
            account_id=self.account_id,
            account_type="checking",
            initial_balance=1000.00
        )

    def test_account_initialization(self):
        """Test account initialization with correct values"""
        self.assertEqual(self.test_account.account_id, self.account_id)
        self.assertEqual(self.test_account.account_type, "checking")
        self.assertEqual(self.test_account.balance, 1000.00)
        self.assertEqual(self.test_account.status, AccountStatus.ACTIVE)
        self.assertIsInstance(self.test_account.creation_date, datetime)

    def test_deposit_positive_amount(self):
        """Test depositing a valid positive amount"""
        self.assertTrue(self.test_account.deposit(500.00))
        self.assertEqual(self.test_account.balance, 1500.00)

    def test_deposit_invalid_amount(self):
        """Test depositing invalid amounts"""
        with self.assertRaises(ValueError):
            self.test_account.deposit(-100.00)  # Negative amount
        with self.assertRaises(ValueError):
            self.test_account.deposit(0.00)  # Zero amount

    def test_withdraw_sufficient_balance(self):
        """Test successful withdrawal with sufficient balance"""
        self.assertTrue(self.test_account.withdraw(500.00))
        self.assertEqual(self.test_account.balance, 500.00)

    def test_withdraw_insufficient_balance(self):
        """Test withdrawal with insufficient balance"""
        self.assertFalse(self.test_account.withdraw(1500.00))
        self.assertEqual(self.test_account.balance, 1000.00)  # Balance unchanged

    def test_withdraw_invalid_amount(self):
        """Test withdrawing invalid amounts"""
        with self.assertRaises(ValueError):
            self.test_account.withdraw(-100.00)  # Negative amount
        with self.assertRaises(ValueError):
            self.test_account.withdraw(0.00)  # Zero amount

    def test_close_account(self):
        """Test account closure"""
        self.assertTrue(self.test_account.close_account())
        self.assertEqual(self.test_account.status, AccountStatus.CLOSED)
        
        # Verify no transactions allowed on closed account
        with self.assertRaises(ValueError):
            self.test_account.deposit(100.00)
        with self.assertRaises(ValueError):
            self.test_account.withdraw(100.00)

    def test_reopen_account(self):
        """Test that accounts cannot be reopened (implementation-dependent)"""
        self.test_account.close_account()
        with self.assertRaises(AttributeError):
            self.test_account.status = AccountStatus.ACTIVE  # Should not allow direct status change

    def test_account_string_representation(self):
        """Test the string representation of the account"""
        repr_str = str(self.test_account)
        self.assertIn(self.account_id, repr_str)
        self.assertIn("checking", repr_str)
        self.assertIn("1000.00", repr_str)
        self.assertIn("active", repr_str.lower())

if __name__ == '__main__':
    unittest.main()