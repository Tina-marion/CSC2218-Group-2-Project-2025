from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Optional

class AccountStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"

class AccountType(Enum):
<<<<<<< HEAD
    CHECKING = "checking"
    SAVINGS = "savings"
=======
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"    

class TransactionType(Enum):
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    TRANSFER_OUT = auto()
    TRANSFER_IN = auto()
    INTEREST = auto()
    FEE = auto()
>>>>>>> e7c253fdce9c0e15814b588fec9dfaa285d6272f

class Account(ABC):
    def __init__(self, account_id: str, account_type: AccountType, 
                 balance: float = 0.0, owner_id: Optional[str] = None):
        self._account_id = account_id
        self._account_type = account_type
        self._balance = balance
        self._status = AccountStatus.ACTIVE
        self._creation_date = datetime.now()
        self._owner_id = owner_id

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

    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        """ Abstract withdrawal method for account-specific behavior"""
        pass

    def can_withdraw(self, amount: float) -> bool:
        """Additional check for transfer operations"""
        return self._status == AccountStatus.ACTIVE and amount > 0

    def close_account(self) -> None:
        self._status = AccountStatus.CLOSED

    # Week 2: Transfer-specific method
    def prepare_for_transfer(self, amount: float) -> bool:
        """Reserve funds for transfer (could be extended for concurrency)"""
        return self.withdraw(amount)

    def complete_transfer(self, amount: float) -> bool:
        """Finalize transfer (currently same as deposit)"""
        return self.deposit(amount)

    def __str__(self) -> str:
        return f"{self._account_type.value.capitalize()} Account {self._account_id}: Balance ${self._balance:.2f}"

class CheckingAccount(Account):
    """ account type with overdraft protection"""
    def __init__(self, account_id: str, balance: float = 0.0, owner_id: Optional[str] = None):
        super().__init__(account_id, AccountType.CHECKING, balance, owner_id)
        self._overdraft_limit = 100.00

    def withdraw(self, amount: float) -> bool:
        if (self.can_withdraw(amount) and (self._balance - amount)) >= -self._overdraft_limit:
            self._balance -= amount
            return True
        return False

class SavingsAccount(Account):
    """ account type with no overdraft"""
    def __init__(self, account_id: str, balance: float = 0.0, owner_id: Optional[str] = None):
        super().__init__(account_id, AccountType.SAVINGS, balance, owner_id)
        self._minimum_balance = 10.00  # Week 1: Minimum balance requirement

    def withdraw(self, amount: float) -> bool:
        if self.can_withdraw(amount) and (self._balance - amount) >= self._minimum_balance:
            self._balance -= amount
            return True
        return False