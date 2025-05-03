# domain/services/transaction_service.py
from typing import List
from domain.entities.account import Account
from domain.entities.transaction import Transaction, TransactionType
from domain.ports.account_repository import AccountRepository
from domain.ports.transaction_repository import TransactionRepository

class TransactionService:
    """Handles transaction-related business logic"""
    def __init__(
        self, 
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository
    ):
        self._transaction_repo = transaction_repo
        self._account_repo = account_repo

    def execute_transaction(
        self,
        account_id: int,
        amount: float,
        transaction_type: TransactionType
    ) -> Transaction:
        """Executes and records a financial transaction"""
        account = self._account_repo.find_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        # Create transaction first to ensure we have all data
        transaction = Transaction(
            account_id=account_id,
            amount=amount,
            type=transaction_type
        )

        # Execute the transaction
        if transaction_type == TransactionType.DEPOSIT:
            account.deposit(amount)
        else:
            account.withdraw(amount)

        # Persist changes
        self._account_repo.update(account)
        return self._transaction_repo.create(transaction)

    def get_account_transactions(self, account_id: int) -> List[Transaction]:
        """Retrieves all transactions for an account"""
        if not self._account_repo.find_by_id(account_id):
            raise ValueError("Account not found")
        return self._transaction_repo.find_by_account_id(account_id)