import unittest
from unittest.mock import patch, mock_open
from datetime import datetime, timedelta
import os
import csv
import json
from domain.models.account import Account, SavingsAccount, CheckingAccount, AccountType
from domain.models.transaction import TransactionType, DepositTransaction, WithdrawalTransaction, TransferTransaction
from domain.services.account_service import BankAccountService
from domain.services.interest_service import InterestService
from domain.services.limit_enforcement_service import LimitEnforcementService
from domain.services.statement_service import StatementService

class TestBankServices(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        self.account_service = BankAccountService()
        self.interest_service = InterestService(self.account_service)
        self.limit_service = LimitEnforcementService(self.account_service)
        self.statement_service = StatementService(self.account_service)

        # Create test accounts
        self.savings_account = self.account_service.create_account("savings", initial_balance=1000.0, owner_id="user1")
        self.checking_account = self.account_service.create_account("checking", initial_balance=500.0, owner_id="user2")

        # Mock transactions.csv for statement tests
        self.transactions_data = [
            {"Transaction ID": "trans1", "Account ID": self.savings_account.account_id, "Type": "deposit", "Amount": "1000.00", "Date": "2025-04-01 10:00:00", "Related Account": "", "Balance After": "1000.00"},
            {"Transaction ID": "trans2", "Account ID": self.savings_account.account_id, "Type": "withdraw", "Amount": "200.00", "Date": "2025-04-02 12:00:00", "Related Account": "", "Balance After": "800.00"},
            {"Transaction ID": "trans3", "Account ID": self.savings_account.account_id, "Type": "transfer", "Amount": "100.00", "Date": "2025-04-03 14:00:00", "Related Account": self.checking_account.account_id, "Balance After": "700.00"},
        ]

    def test_interest_calculation_accuracy(self):
        """Test that interest is correctly calculated and applied to savings accounts."""
        # Interest rate: 2% annual, compounded monthly -> 0.02 / 12 = 0.00166667 per month
        # Balance: $1000 -> Expected interest: $1000 * 0.00166667 = $1.66667
        self.assertTrue(self.interest_service.apply_interest_to_account(self.savings_account.account_id))
        expected_interest = 1000.0 * (0.02 / 12)
        self.assertAlmostEqual(self.savings_account.interest_accrued, expected_interest, places=5)
        self.assertAlmostEqual(self.savings_account.balance, 1000.0 + expected_interest, places=5)

        # Interest should not be applied to checking accounts
        self.assertFalse(self.interest_service.apply_interest_to_account(self.checking_account.account_id))
        self.assertEqual(self.checking_account.interest_accrued, 0.0)
        self.assertEqual(self.checking_account.balance, 500.0)

    def test_interest_batch_application(self):
        """Test batch interest application across multiple accounts."""
        # Add another savings account
        savings_account2 = self.account_service.create_account("savings", initial_balance=2000.0, owner_id="user3")
        account_ids = [self.savings_account.account_id, savings_account2.account_id, self.checking_account.account_id]

        # Apply interest to all accounts (should only affect savings accounts)
        success_count = self.interest_service.apply_interest_batch(account_ids)
        self.assertEqual(success_count, 2)  # Only the two savings accounts should succeed

        # Verify interest for savings_account
        expected_interest1 = 1000.0 * (0.02 / 12)
        self.assertAlmostEqual(self.savings_account.interest_accrued, expected_interest1, places=5)
        self.assertAlmostEqual(self.savings_account.balance, 1000.0 + expected_interest1, places=5)

        # Verify interest for savings_account2
        expected_interest2 = 2000.0 * (0.02 / 12)
        self.assertAlmostEqual(savings_account2.interest_accrued, expected_interest2, places=5)
        self.assertAlmostEqual(savings_account2.balance, 2000.0 + expected_interest2, places=5)

        # Verify no interest for checking_account
        self.assertEqual(self.checking_account.interest_accrued, 0.0)
        self.assertEqual(self.checking_account.balance, 500.0)

    def test_daily_limit_enforcement(self):
        """Test that daily transaction limits are enforced."""
        # Daily limit is $10,000
        # Deposit $9,000 (within limit)
        self.assertTrue(self.limit_service.check_limit(self.savings_account.account_id, 9000.0))
        # Try to deposit another $2,000 (total $11,000, exceeds limit)
        self.assertFalse(self.limit_service.check_limit(self.savings_account.account_id, 2000.0))

        # Verify the limits file
        with open("transaction_limits.json", "r") as f:
            limits = json.load(f)
            self.assertAlmostEqual(limits[self.savings_account.account_id]["daily_limit_used"], 9000.0, places=2)

    def test_monthly_limit_enforcement(self):
        """Test that monthly transaction limits are enforced."""
        # Monthly limit is $30,000
        # Deposit $29,000 (within limit)
        self.assertTrue(self.limit_service.check_limit(self.savings_account.account_id, 29000.0))
        # Try to deposit another $2,000 (total $31,000, exceeds limit)
        self.assertFalse(self.limit_service.check_limit(self.savings_account.account_id, 2000.0))

        # Verify the limits file
        with open("transaction_limits.json", "r") as f:
            limits = json.load(f)
            self.assertAlmostEqual(limits[self.savings_account.account_id]["monthly_limit_used"], 29000.0, places=2)

    def test_daily_limit_reset(self):
        """Test that daily limits reset correctly."""
        # Set a transaction and update the daily limit
        self.limit_service.check_limit(self.savings_account.account_id, 5000.0)

        # Mock the date to simulate a new day
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 5, 5, 10, 0, 0)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            self.limit_service.reset_limits_daily()

        # Verify the daily limit is reset
        with open("transaction_limits.json", "r") as f:
            limits = json.load(f)
            self.assertEqual(limits[self.savings_account.account_id]["daily_limit_used"], 0.0)
            self.assertEqual(limits[self.savings_account.account_id]["daily_reset"], "2025-05-05")

        # Check that we can now make a new transaction
        self.assertTrue(self.limit_service.check_limit(self.savings_account.account_id, 5000.0))

    def test_monthly_limit_reset(self):
        """Test that monthly limits reset correctly."""
        # Set a transaction and update the monthly limit
        self.limit_service.check_limit(self.savings_account.account_id, 15000.0)

        # Mock the date to simulate a new month
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 6, 1, 10, 0, 0)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            self.limit_service.reset_limits_monthly()

        # Verify the monthly limit is reset
        with open("transaction_limits.json", "r") as f:
            limits = json.load(f)
            self.assertEqual(limits[self.savings_account.account_id]["monthly_limit_used"], 0.0)
            self.assertEqual(limits[self.savings_account.account_id]["monthly_reset"], "2025-06-01")

        # Check that we can now make a new transaction
        self.assertTrue(self.limit_service.check_limit(self.savings_account.account_id, 15000.0))

    @patch("builtins.open", new_callable=mock_open)
    def test_statement_data_correctness(self, mock_file):
        """Test that the statement CSV contains correct transaction data and summaries."""
        # Mock the transactions.csv file
        mock_csv_data = "\n".join([",".join(row.values()) for row in self.transactions_data])
        mock_file.side_effect = [
            mock_open(read_data="Transaction ID,Account ID,Type,Amount,Date,Related Account,Balance After\n" + mock_csv_data).return_value,
            mock_open().return_value  # For writing the statement CSV
        ]

        # Generate the statement
        start_date = datetime(2025, 4, 1)
        end_date = datetime(2025, 4, 30)
        filename = self.statement_service.generate_statement(self.savings_account.account_id, start_date, end_date)

        # Verify the written CSV data
        handle = mock_file()
        written_calls = handle.write.call_args_list

        # Construct the expected CSV content
        expected_lines = [
            "Date,Type,Amount ($),Related Account,Balance ($),Interest Accrued ($)",
            "2025-04-01,deposit,1000.00,-,1000.00,0.00",
            "2025-04-02,withdraw,200.00,-,800.00,0.00",
            "2025-04-03,transfer,100.00," + self.checking_account.account_id + ",700.00,0.00",
            "",
            "Summary,,,,,",
            "Total Deposits,1000.00,,,,",
            "Total Withdrawals/Transfers,300.00,,,,",
            "Ending Balance,700.00,,,,",
            "Total Interest Accrued,0.00,,,,",
        ]

        # Check each line written to the CSV
        written_content = "".join(call[0][0] for call in written_calls).strip()
        written_lines = written_content.split("\n")
        self.assertEqual(len(written_lines), len(expected_lines))
        for written_line, expected_line in zip(written_lines, expected_lines):
            self.assertEqual(written_line, expected_line)

    def test_statement_with_interest(self):
        """Test that the statement correctly includes interest accrued."""
        # Apply interest to the savings account
        self.interest_service.apply_interest_to_account(self.savings_account.account_id)
        expected_interest = 1000.0 * (0.02 / 12)

        # Add a transaction after interest application
        transaction = DepositTransaction(amount=expected_interest, account_id=self.savings_account.account_id)
        self.account_service.execute_transaction(transaction)

        # Mock transactions.csv with updated data
        updated_transactions = self.transactions_data + [
            {"Transaction ID": "trans4", "Account ID": self.savings_account.account_id, "Type": "deposit", "Amount": f"{expected_interest:.2f}", "Date": "2025-04-04 16:00:00", "Related Account": "", "Balance After": f"{1000.0 + expected_interest:.2f}"},
        ]

        mock_csv_data = "\n".join([",".join(row.values()) for row in updated_transactions])
        with patch("builtins.open", mock_open(read_data="Transaction ID,Account ID,Type,Amount,Date,Related Account,Balance After\n" + mock_csv_data)) as mock_file:
            # Generate the statement
            start_date = datetime(2025, 4, 1)
            end_date = datetime(2025, 4, 30)
            filename = self.statement_service.generate_statement(self.savings_account.account_id, start_date, end_date)

            # Verify the written CSV data
            handle = mock_file()
            written_calls = handle.write.call_args_list
            written_content = "".join(call[0][0] for call in written_calls).strip()
            written_lines = written_content.split("\n")

            # Check that interest is reflected in the last transaction and summary
            self.assertIn(f"2025-04-04,deposit,{expected_interest:.2f},-,{1000.0 + expected_interest:.2f},{expected_interest:.2f}", written_lines)
            self.assertIn(f"Total Interest Accrued,{expected_interest:.2f},,,,", written_lines)

    def tearDown(self):
        """Clean up after each test."""
        # Remove temporary files created during tests
        for filename in ["transaction_limits.json", "statement_" + self.savings_account.account_id + "_20250504.csv"]:
            if os.path.exists(filename):
                os.remove(filename)

if __name__ == "__main__":
    unittest.main()