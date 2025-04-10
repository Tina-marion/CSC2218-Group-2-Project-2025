import unittest
from datetime import datetime, timedelta
from models.transaction import Transaction, TransactionType

class TestTransaction(unittest.TestCase):
    def setUp(self):
        """Create test transactions before each test"""
        self.transaction_id = "TXN789012"
        self.account_id = "ACC123456"
        self.test_timestamp = datetime.now()
        self.test_deposit = Transaction(
            transaction_id=self.transaction_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=500.00,
            account_id=self.account_id,
            timestamp=self.test_timestamp,
            description="Test deposit"
        )
        
        self.test_withdrawal = Transaction(
            transaction_id="TXN345678",
            transaction_type=TransactionType.WITHDRAWAL,
            amount=200.00,
            account_id=self.account_id
        )

    def test_transaction_initialization(self):
        """Test transaction initialization with correct values"""
        self.assertEqual(self.test_deposit.transaction_id, self.transaction_id)
        self.assertEqual(self.test_deposit.transaction_type, TransactionType.DEPOSIT)
        self.assertEqual(self.test_deposit.amount, 500.00)
        self.assertEqual(self.test_deposit.account_id, self.account_id)
        self.assertEqual(self.test_deposit.timestamp, self.test_timestamp)
        self.assertEqual(self.test_deposit.description, "Test deposit")

    def test_invalid_amount(self):
        """Test transaction with invalid amount"""
        with self.assertRaises(ValueError):
            Transaction(
                transaction_id="TXN111111",
                transaction_type=TransactionType.DEPOSIT,
                amount=-100.00,
                account_id=self.account_id
            )

    def test_is_debit(self):
        """Test debit transaction detection"""
        self.assertFalse(self.test_deposit.is_debit())
        self.assertTrue(self.test_withdrawal.is_debit())

    def test_is_credit(self):
        """Test credit transaction detection"""
        self.assertTrue(self.test_deposit.is_credit())
        self.assertFalse(self.test_withdrawal.is_credit())

    def test_get_signed_amount(self):
        """Test correct signing of amounts"""
        self.assertEqual(self.test_deposit.get_signed_amount(), 500.00)
        self.assertEqual(self.test_withdrawal.get_signed_amount(), -200.00)

    def test_auto_timestamp(self):
        """Test automatic timestamp generation"""
        before_create = datetime.now()
        tx = Transaction(
            transaction_id="TXN999999",
            transaction_type=TransactionType.DEPOSIT,
            amount=100.00,
            account_id=self.account_id
        )
        after_create = datetime.now()
        
        self.assertGreaterEqual(tx.timestamp, before_create)
        self.assertLessEqual(tx.timestamp, after_create)

    def test_to_from_dict(self):
        """Test dictionary serialization/deserialization"""
        tx_dict = self.test_deposit.to_dict()
        reconstructed = Transaction.from_dict(tx_dict)
        
        self.assertEqual(reconstructed.transaction_id, self.test_deposit.transaction_id)
        self.assertEqual(reconstructed.transaction_type, self.test_deposit.transaction_type)
        self.assertEqual(reconstructed.amount, self.test_deposit.amount)
        self.assertEqual(reconstructed.timestamp, self.test_deposit.timestamp)

    def test_string_representation(self):
        """Test the string representation of transactions"""
        repr_str = str(self.test_deposit)
        self.assertIn(self.transaction_id, repr_str)
        self.assertIn("DEPOSIT", repr_str)
        self.assertIn("500.00", repr_str)
        self.assertIn(self.account_id, repr_str)
        self.assertIn(self.test_timestamp.strftime('%Y-%m-%d'), repr_str)

if __name__ == '__main__':
    unittest.main()