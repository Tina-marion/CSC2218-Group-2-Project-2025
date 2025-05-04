from dataclasses import dataclass
from enum import Enum
from typing import Optional
import uuid

class AccountType(Enum):
    CHECKING = "checking"
    SAVINGS = "savings"

class AccountStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"

@dataclass
class Account:
    account_id: str
    _balance: float = 0.0
    _account_type: AccountType = AccountType.CHECKING
    owner_id: Optional[str] = None
    status: AccountStatus = AccountStatus.ACTIVE
    minimum_balance: float = 0.0
    interest_accrued: float = 0.0  # Track total interest accrued

    def __post_init__(self):
        if not self.account_id:
            self.account_id = str(uuid.uuid4())
        self._balance = float(self._balance)

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> bool:
        if amount > 0:
            self._balance += amount
            return True
        return False

    def withdraw(self, amount: float) -> bool:
        if amount > 0 and self._balance - amount >= self.minimum_balance:
            self._balance -= amount
            return True
        return False

    def can_withdraw(self, amount: float) -> bool:
        return amount > 0 and self._balance - amount >= self.minimum_balance

    def prepare_for_transfer(self, amount: float) -> bool:
        return self.can_withdraw(amount)

    def complete_transfer(self, amount: float) -> bool:
        return self.deposit(amount)

    def add_interest(self, amount: float) -> None:
        """Add interest to the account and track it."""
        self.interest_accrued += amount
        self.deposit(amount)

@dataclass
class CheckingAccount(Account):
    minimum_balance: float = 0.0

@dataclass
class SavingsAccount(Account):
    minimum_balance: float = 100.0