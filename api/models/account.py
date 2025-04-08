from datetime import datetime
from enum import Enum


class AccountStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"


class AccountType(str, Enum):
    SAVINGS = "savings"
    CHECKING = "checking"


class Account:
    def __init__(self, account_id: str, account_type: AccountType, balance: float = 0.0):
        self.account_id = account_id
        self.account_type = account_type
        self.balance = balance
        self.status = AccountStatus.ACTIVE
        self.creation_date = datetime.now()

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.balance - amount < 0:
            raise ValueError("Insufficient funds.")
        self.balance -= amount

    def close_account(self):
        self.status = AccountStatus.CLOSED
