# application/services.py

from typing import Protocol
from domain.entities import Account, Transaction, TransactionType # type: ignore
from domain.exceptions import InsufficientFunds # type: ignore
import logging

from domain.ports import account_repository, transaction_repository


class NotificationSender(Protocol):
    def send(self, message: str) -> None:
        ...

class AccountCreationService:
    """
    Responsible for creating accounts. (In a complete solution, you might validate a minimum deposit.)
    """
    def __init__(self, account_repository: account_repository):
        self.account_repository = account_repository

    def create_account(self, account_type: str, owner_id: str, initial_deposit: float = 0.0) -> str:
        if account_type.upper() == "CHECKING":
            from domain.models import CheckingAccount  
            account = CheckingAccount(owner_id)
        elif account_type.upper() == "SAVINGS":
            from domain.models import SavingsAccount
            account = SavingsAccount(owner_id)
        else:
            raise ValueError("Unsupported account type.")
        
        if initial_deposit > 0:
            account.balance += initial_deposit
        
        self.account_repository.create_account(account)
        return account.account_id


class TransactionService:
    def __init__(self, account_repository: account_repository,
                 transaction_repository: transaction_repository,
                 notification_sender: NotificationSender):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.notification_sender = notification_sender

    def deposit(self, account_id: str, amount: float) -> Transaction:
        account = self.account_repository.get_account_by_id(account_id)
        if account is None:
            raise ValueError("Account not found.")
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        account.balance += amount
        txn = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            account_id=account.account_id,
            description="Deposit"
        )
        account.add_transaction(txn)
        self.transaction_repository.save_transaction(txn)
        self._notify(txn)
        logging.info("Deposit processed: %s", txn)
        self.account_repository.update_account(account)
        return txn

    def withdraw(self, account_id: str, amount: float) -> Transaction:
        account = self.account_repository.get_account_by_id(account_id)
        if account is None:
            raise ValueError("Account not found.")
        if not account.can_withdraw(amount):
            raise InsufficientFunds("Insufficient funds or withdrawal not permitted.")
        account.balance -= amount
        txn = Transaction(
            transaction_type=TransactionType.WITHDRAWAL,
            amount=amount,
            account_id=account.account_id,
            description="Withdrawal"
        )
        account.add_transaction(txn)
        self.transaction_repository.save_transaction(txn)
        self._notify(txn)
        logging.info("Withdrawal processed: %s", txn)
        self.account_repository.update_account(account)
        return txn

    def transfer(self, source_account_id: str, destination_account_id: str, amount: float) -> Transaction:
        source = self.account_repository.get_account_by_id(source_account_id)
        destination = self.account_repository.get_account_by_id(destination_account_id)
        if source is None or destination is None:
            raise ValueError("One or both accounts not found.")
        if not source.can_withdraw(amount):
            raise InsufficientFunds("Source account cannot withdraw the requested amount.")

        
        self.withdraw(source_account_id, amount)
        self.deposit(destination_account_id, amount)
        
        txn = Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=amount,
            account_id=source.account_id,  
            source_account_id=source.account_id,
            destination_account_id=destination.account_id,
            description=f"Transfer from {source.account_id} to {destination.account_id}"
        )
        source.add_transaction(txn)
        destination.add_transaction(txn)
        self.transaction_repository.save_transaction(txn)
        self._notify(txn)
        logging.info("Transfer processed: %s", txn)
        self.account_repository.update_account(source)
        self.account_repository.update_account(destination)
        return txn

    def _notify(self, txn: Transaction) -> None:
        message = f"Transaction Alert: {txn}"
        self.notification_sender.send(message)


class AccountRepository(Protocol):
    def create_account(self, account: Account) -> None:
        ...
    def get_account_by_id(self, account_id: str) -> Account | None:
        ...
    def update_account(self, account: Account) -> None:
        ...

class TransactionRepository(Protocol):
    def save_transaction(self, txn: Transaction) -> None:
        ...
    def get_transactions_for_account(self, account_id: str) -> list[Transaction]:
        ...
