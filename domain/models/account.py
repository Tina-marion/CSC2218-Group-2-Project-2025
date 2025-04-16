from datetime import datetime
from enum import Enum, auto
from abc import ABC, abstractmethod
import uuid

# -------------------------------
# Enum for Account Status & Transaction Type
# -------------------------------

class AccountStatus(Enum):
<<<<<<< HEAD
=======
    """Representing account statuses"""
>>>>>>> dd78142bee6b66306136b4ffb9b3d24045d68fb1
    ACTIVE = auto()
    CLOSED = auto()
    FROZEN = auto()

class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

# -------------------------------
# Transaction Entity
# -------------------------------

class Transaction:
    def __init__(self, transaction_type: TransactionType, amount: float, account_id: str):
        self.transaction_id = str(uuid.uuid4())
        self.transaction_type = transaction_type
        self.amount = amount
        self.timestamp = datetime.now()
        self.account_id = account_id

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {self.transaction_type.name} | ${self.amount:.2f}"

# -------------------------------
# Abstract Account Entity
# -------------------------------

class Account(ABC):
    def __init__(self, account_type: str):
        self.account_id = str(uuid.uuid4())
        self.account_type = account_type
        self.balance = 0.0
        self.status = AccountStatus.ACTIVE
        self.creation_date = datetime.now()
        self.transactions = []

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        self.transactions.append(Transaction(TransactionType.DEPOSIT, amount, self.account_id))

    def withdraw(self, amount: float):
        if not self.can_withdraw(amount):
            raise ValueError("Withdrawal denied by account rules or insufficient funds.")
        self.balance -= amount
        self.transactions.append(Transaction(TransactionType.WITHDRAW, amount, self.account_id))

    def view_balance(self):
        return f"Current balance: ${self.balance:.2f}"

    def view_transaction_history(self):
        return "\n".join(str(txn) for txn in self.transactions) if self.transactions else "No transactions yet."

    @abstractmethod
    def can_withdraw(self, amount: float) -> bool:
        pass

# -------------------------------
# Specific Account Types
# -------------------------------

class CheckingAccount(Account):
    def __init__(self):
        super().__init__("CHECKING")

    def can_withdraw(self, amount: float) -> bool:
        return self.status == AccountStatus.ACTIVE and self.balance >= amount

class SavingsAccount(Account):
    def __init__(self):
        super().__init__("SAVINGS")

    def can_withdraw(self, amount: float) -> bool:
        # Must maintain at least $100 after withdrawal
        return self.status == AccountStatus.ACTIVE and (self.balance - amount) >= 100

# -------------------------------
# Example Usage
# -------------------------------

if __name__ == "__main__":
    acct1 = CheckingAccount()
    acct1.deposit(500)
    acct1.withdraw(200)

    acct2 = SavingsAccount()
    acct2.deposit(1000)
    try:
        acct2.withdraw(950)  # Should fail due to $100 minimum balance rule
    except ValueError as e:
        print(f"Error: {e}")

    print("\n--- Checking Account ---")
    print(acct1.view_balance())
    print(acct1.view_transaction_history())

    print("\n--- Savings Account ---")
    print(acct2.view_balance())
    print(acct2.view_transaction_history())
