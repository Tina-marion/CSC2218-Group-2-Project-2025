from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List, Optional

from domain.entities.transaction import Transaction, TransactionType

class AccountStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"

class AccountType(Enum):
    CHECKING = "checking"
    SAVINGS = "savings"

class Account(ABC):
    def __init__(
        self, 
        account_id: str, 
        account_type: AccountType, 
        initial_balance: float = 0.0
    ):
        self._account_id = account_id
        self._account_type = account_type
        self._balance = initial_balance
        self._status = AccountStatus.ACTIVE
        self._creation_date = datetime.now()
        self._transactions: List['Transaction'] = []

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def account_type(self) -> AccountType:
        return self._account_type

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def status(self) -> AccountStatus:
        return self._status

    @property
    def creation_date(self) -> datetime:
        return self._creation_date

    @property
    def transactions(self) -> List['Transaction']:
        return self._transactions.copy()

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount
        transaction = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            account_id=self._account_id
        )
        self._transactions.append(transaction)

    @abstractmethod
    def withdraw(self, amount: float) -> None:
        pass

    def close_account(self) -> None:
        self._status = AccountStatus.CLOSED

    def get_transaction_history(self) -> List['Transaction']:
        return self._transactions.copy()

class CheckingAccount(Account):
    def __init__(self, account_id: str, initial_balance: float = 0.0):
        super().__init__(account_id, AccountType.CHECKING, initial_balance)
        self._overdraft_limit = 100.0  # Example overdraft limit

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if self._balance - amount < -self._overdraft_limit:
            raise ValueError("Withdrawal amount exceeds available balance and overdraft limit")
        
        self._balance -= amount
        transaction = Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=amount,
            account_id=self._account_id
        )
        self._transactions.append(transaction)

class SavingsAccount(Account):
    def __init__(self, account_id: str, initial_balance: float = 0.0):
        super().__init__(account_id, AccountType.SAVINGS, initial_balance)
        self._minimum_balance = 50.0  # Example minimum balance requirement

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if self._balance - amount < self._minimum_balance:
            raise ValueError(f"Withdrawal would go below minimum balance requirement of {self._minimum_balance}")
        
        self._balance -= amount
        transaction = Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=amount,
            account_id=self._account_id
        )
        self._transactions.append(transaction)