from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Optional, List
import uuid
from threading import Lock
from decimal import Decimal

# Enums
class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CLOSED = "CLOSED"
    FROZEN = "FROZEN"

class AccountType(Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"    

class TransactionType(Enum):
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    TRANSFER_OUT = auto()
    TRANSFER_IN = auto()
    INTEREST = auto()
    FEE = auto()

# Data class for transaction record
@dataclass
class Transaction:
    transaction_type: TransactionType
    amount: float
    account_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    source_account_id: Optional[str] = None
    destination_account_id: Optional[str] = None

# Abstract transaction template
class AbstractTransaction(ABC):
    def __init__(self, amount: Decimal, account_id: str, description: Optional[str] = None):
        self.transaction_id: str = str(uuid.uuid4())
        self.amount: Decimal = Decimal(amount)
        self.account_id: str = account_id
        self.timestamp: datetime = datetime.now()
        self.description: str = description or self._default_description()
        self._validate()
    
    def execute(self, account: Account) -> bool:
        if not self._pre_execute_checks(account):
            return False
        self._apply_balance_change(account)
        account.add_transaction(self.to_concrete_transaction())
        self._post_execute_actions(account)
        return True
    
    @abstractmethod
    def _validate(self) -> None:
        pass
    
    @abstractmethod
    def _pre_execute_checks(self, account: Account) -> bool:
        pass
    
    @abstractmethod
    def _apply_balance_change(self, account: Account) -> None:
        pass
    
    @abstractmethod
    def _default_description(self) -> str:
        pass
    
    @abstractmethod
    def to_concrete_transaction(self) -> Transaction:
        pass
    
    def _post_execute_actions(self, account: Account) -> None:
        pass

# Concrete transactions
class DepositTransaction(AbstractTransaction):
    def _validate(self) -> None:
        if self.amount <= Decimal('0'):
            raise ValueError("Deposit amount must be positive")
    
    def _pre_execute_checks(self, account: Account) -> bool:
        return account.status == AccountStatus.ACTIVE
    
    def _apply_balance_change(self, account: Account) -> None:
        account._increase_balance(float(self.amount))
        
    def _default_description(self) -> str:
        return "Deposit transaction"
        
    def to_concrete_transaction(self) -> Transaction:
        return Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=float(self.amount),
            account_id=self.account_id,
            description=self.description
        )

class WithdrawalTransaction(AbstractTransaction):
    def _validate(self) -> None:
        if self.amount <= Decimal('0'):
            raise ValueError("Withdrawal amount must be positive")
    
    def _pre_execute_checks(self, account: Account) -> bool:
        return account.status == AccountStatus.ACTIVE and account.can_withdraw(float(self.amount))
    
    def _apply_balance_change(self, account: Account) -> None:
        account._decrease_balance(float(self.amount))
        
    def _default_description(self) -> str:
        return "Withdrawal transaction"
        
    def to_concrete_transaction(self) -> Transaction:
        return Transaction(
            transaction_type=TransactionType.WITHDRAWAL,
            amount=float(self.amount),
            account_id=self.account_id,
            description=self.description
        )

class TransferOutTransaction(AbstractTransaction):
    def __init__(self, amount: Decimal, account_id: str, 
                 destination_account_id: str, description: Optional[str] = None):
        self.destination_account_id = destination_account_id
        super().__init__(amount, account_id, description)
    
    def _validate(self) -> None:
        if self.amount <= Decimal('0'):
            raise ValueError("Transfer amount must be positive")
    
    def _pre_execute_checks(self, account: Account) -> bool:
        return account.status == AccountStatus.ACTIVE and account.can_withdraw(float(self.amount))
    
    def _apply_balance_change(self, account: Account) -> None:
        account._decrease_balance(float(self.amount))
        
    def _default_description(self) -> str:
        return f"Transfer to account {self.destination_account_id}"
        
    def to_concrete_transaction(self) -> Transaction:
        return Transaction(
            transaction_type=TransactionType.TRANSFER_OUT,
            amount=float(self.amount),
            account_id=self.account_id,
            source_account_id=self.account_id,
            destination_account_id=self.destination_account_id,
            description=self.description
        )

# Account entities
class Account(ABC):
    def __init__(self, account_type: str, owner_id: Optional[str] = None):
        self.account_id: str = str(uuid.uuid4())
        self.account_type: str = account_type
        self.balance: float = 0.0
        self.name: str = ""
        self.status: AccountStatus = AccountStatus.ACTIVE
        self.creation_date: datetime = datetime.now()
        self.transactions: List[Transaction] = []
        self.owner_id: Optional[str] = owner_id
        self._lock = Lock()

    def add_transaction(self, txn: Transaction) -> None:
        with self._lock:
            self.transactions.append(txn)

    def process_transaction(self, transaction: AbstractTransaction) -> bool:
        with self._lock:
            return transaction.execute(self)

    def get_balance(self) -> float:
        with self._lock:
            return self.balance

    def get_transaction_history(self) -> List[Transaction]:
        with self._lock:
            return list(self.transactions)

    def _increase_balance(self, amount: float) -> None:
        with self._lock:
            self.balance += amount

    def _decrease_balance(self, amount: float) -> None:
        with self._lock:
            self.balance -= amount

    @abstractmethod
    def can_withdraw(self, amount: float) -> bool:
        pass

    def __str__(self) -> str:
        return (f"Account ID: {self.account_id}\n"
                f"Type: {self.account_type}\n"
                f"Status: {self.status.value}\n"
                f"Balance: ${self.get_balance():.2f}\n"
                f"Created on: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')}")

class CheckingAccount(Account):
    def __init__(self, owner_id: Optional[str] = None):
        super().__init__("CHECKING", owner_id)

    def can_withdraw(self, amount: float) -> bool:
        return self.status == AccountStatus.ACTIVE and self.get_balance() >= amount

class SavingsAccount(Account):
    MIN_BALANCE: float = 100.0

    def __init__(self, owner_id: Optional[str] = None):
        super().__init__("SAVINGS", owner_id)

    def can_withdraw(self, amount: float) -> bool:
        return (self.status == AccountStatus.ACTIVE and 
                (self.get_balance() - amount) >= self.MIN_BALANCE)

# Service to perform transfer
class TransferService:
    def __init__(self, account_repository):
        self._repo = account_repository
        self._transfer_lock = Lock()

    def transfer(self, source_id: str, dest_id: str, amount: Decimal, description: str = "") -> bool:
        with self._transfer_lock:
            source = self._repo.find_account_by_id(source_id)
            dest = self._repo.find_account_by_id(dest_id)
            
            if not source or not dest:
                return False
            
            transfer_out = TransferOutTransaction(
                amount=amount,
                account_id=source_id,
                destination_account_id=dest_id,
                description=description
            )
            
            transfer_in = DepositTransaction(
                amount=amount,
                account_id=dest_id,
                description=description
            )
            
            success = transfer_out.execute(source)
            if success:
                success = transfer_in.execute(dest)
                if not success:
                    # Rollback
                    DepositTransaction(amount, source_id, "Transfer rollback").execute(source)
                    return False
                
                self._repo.update_account(source)
                self._repo.update_account(dest)
                return True
            return False
