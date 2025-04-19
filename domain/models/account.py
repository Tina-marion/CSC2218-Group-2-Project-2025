# domain/entities.py

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Optional, List
import uuid

class TransactionType(Enum):
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    TRANSFER = auto()
    INTEREST = auto()
    FEE = auto()

@dataclass
class Transaction:
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    transaction_type: TransactionType = TransactionType.DEPOSIT
    amount: float = 0.0
    # For deposit, withdrawal, fee, interest – this is the primary account.
    account_id: str = ""
    # For transfers record both accounts.
    source_account_id: Optional[str] = None
    destination_account_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        if self.transaction_type == TransactionType.TRANSFER:
            if not self.source_account_id or not self.destination_account_id:
                raise ValueError("Transfer transactions require source and destination account IDs.")

    def __str__(self) -> str:
        if self.transaction_type == TransactionType.TRANSFER:
            return (f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                    f"[{self.transaction_id[:8]}] {self.transaction_type.name} "
                    f"${self.amount:.2f} (From: {self.source_account_id} To: {self.destination_account_id})")
        else:
            return (f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                    f"[{self.transaction_id[:8]}] {self.transaction_type.name} "
                    f"${self.amount:.2f} (Account: {self.account_id})")

class Account(ABC):
    def __init__(self, account_type: str, owner_id: Optional[str] = None):
        self.account_id: str = str(uuid.uuid4())
        self.account_type: str = account_type
        self.balance: float = 0.0
        self.status: str = "ACTIVE"  # In a more robust implementation, use an Enum.
        self.creation_date: datetime = datetime.now()
        self.transactions: List[Transaction] = []
        self.owner_id: Optional[str] = owner_id

    def add_transaction(self, txn: Transaction) -> None:
        self.transactions.append(txn)

    def view_balance(self) -> str:
        return f"Account {self.account_id} Balance: ${self.balance:.2f}"

    def view_transaction_history(self) -> str:
        if not self.transactions:
            return "No transactions yet."
        return "\n".join(str(txn) for txn in self.transactions)

    @abstractmethod
    def can_withdraw(self, amount: float) -> bool:
        pass

    def __str__(self) -> str:
        return (f"Account ID: {self.account_id}\n"
                f"Type: {self.account_type}\n"
                f"Status: {self.status}\n"
                f"Balance: ${self.balance:.2f}\n"
                f"Created on: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')}")

class CheckingAccount(Account):
    def __init__(self, owner_id: Optional[str] = None):
        super().__init__("CHECKING", owner_id)

    def can_withdraw(self, amount: float) -> bool:
        return self.status == "ACTIVE" and self.balance >= amount

class SavingsAccount(Account):
    MIN_BALANCE: float = 100.0

    def __init__(self, owner_id: Optional[str] = None):
        super().__init__("SAVINGS", owner_id)

    def can_withdraw(self, amount: float) -> bool:
        return self.status == "ACTIVE" and (self.balance - amount) >= self.MIN_BALANCE
