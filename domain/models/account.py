from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime
from typing import Optional, Dict
import uuid
from threading import Lock
from decimal import Decimal
from dataclasses import dataclass, field
from domain.models.transaction import TransferTransaction

class AccountStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"

class AccountType(Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"

# Data class for transaction record
@dataclass
class TransactionRecord:
    transaction_type: str
    amount: float
    account_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    source_account_id: Optional[str] = None
    destination_account_id: Optional[str] = None

# Account entities
class Account:
    def __init__(self, account_id: str, account_type: AccountType, 
                 balance: float = 0.0, owner_id: Optional[str] = None):
        self._account_id = account_id
        self._account_type = account_type
        self._balance = balance
        self._status = AccountStatus.ACTIVE
        self._creation_date = datetime.now()
        self._owner_id = owner_id
        self._transactions = []

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def status(self) -> AccountStatus:
        return self._status

    def deposit(self, amount: float) -> bool:
        if amount > 0 and self._status == AccountStatus.ACTIVE:
            self._balance += amount
            return True
        return False

    def withdraw(self, amount: float) -> bool:
        if self.can_withdraw(amount):
            self._balance -= amount
            return True
        return False

    def can_withdraw(self, amount: float) -> bool:
        """Additional check for withdrawal operations"""
        return self._status == AccountStatus.ACTIVE and amount > 0 and self._balance >= amount

    def prepare_for_transfer(self, amount: float) -> bool:
        """Prepare for a transfer by checking if withdrawal is possible."""
        return self.can_withdraw(amount) and self.withdraw(amount)

    def complete_transfer(self, amount: float) -> bool:
        """Complete a transfer by depositing (for incoming) or rolling back (for outgoing)."""
        return self.deposit(amount)

    def close_account(self) -> None:
        self._status = AccountStatus.CLOSED

    def _increase_balance(self, amount: float) -> None:
        self._balance += amount

    def _decrease_balance(self, amount: float) -> None:
        if self._balance >= amount:
            self._balance -= amount

    def add_transaction(self, transaction: TransactionRecord) -> None:
        self._transactions.append(transaction)

    def __str__(self) -> str:
        return f"{self._account_type.value.capitalize()} Account {self._account_id}: Balance ${self._balance:.2f}"

class CheckingAccount(Account):
    """Account type with overdraft protection"""
    def __init__(self, account_id: str, balance: float = 0.0, owner_id: Optional[str] = None):
        super().__init__(account_id, AccountType.CHECKING, balance, owner_id)
        self._overdraft_limit = 100.00

    def withdraw(self, amount: float) -> bool:
        if self.can_withdraw(amount) and (self._balance - amount) >= -self._overdraft_limit:
            self._balance -= amount
            return True
        return False

class SavingsAccount(Account):
    """Account type with no overdraft"""
    def __init__(self, account_id: str, balance: float = 0.0, owner_id: Optional[str] = None):
        super().__init__(account_id, AccountType.SAVINGS, balance, owner_id)
        self._minimum_balance = 10.00

    def withdraw(self, amount: float) -> bool:
        if self.can_withdraw(amount) and (self.balance - amount) >= self._minimum_balance:
            self._balance -= amount
            return True
        return False

# Account repository interface
class AccountRepository(ABC):
    @abstractmethod
    def find_account_by_id(self, account_id: str) -> Optional[Account]:
        pass

    @abstractmethod
    def update_account(self, account: Account) -> None:
        pass

# In-memory account repository
class InMemoryAccountRepository(AccountRepository):
    def __init__(self):
        self.accounts: Dict[str, Account] = {}

    def add_account(self, account: Account) -> None:
        self.accounts[account.account_id] = account

    def find_account_by_id(self, account_id: str) -> Optional[Account]:
        return self.accounts.get(account_id)

    def update_account(self, account: Account) -> None:
        self.accounts[account.account_id] = account

# Transfer service
class TransferService:
    def __init__(self, account_repository: AccountRepository):
        self._repo = account_repository
        self._transfer_lock = Lock()

    def transfer(self, source_id: str, dest_id: str, amount: Decimal, description: str = "") -> bool:
        with self._transfer_lock:
            source = self._repo.find_account_by_id(source_id)
            dest = self._repo.find_account_by_id(dest_id)

            if not source or not dest:
                return False

            transfer = TransferTransaction(
                amount=float(amount),
                source_account_id=source_id,
                destination_account_id=dest_id,
                source_account=source,
                destination_account=dest
            )

            success = transfer.execute(None)  # Pass None since TransferTransaction uses account objects
            if success:
                self._repo.update_account(source)
                self._repo.update_account(dest)
                return True
            return False