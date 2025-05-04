from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass, field
import uuid
from threading import Lock
from domain.services.notification_service import NotificationService

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"

@dataclass
class Transaction(ABC):
    transaction_type: TransactionType
    amount: float
    account_id: str
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None
    related_account: Optional[str] = None
    tag: Optional[str] = None
    is_interest: bool = False
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def __post_init__(self):
        self._amount = self.amount
        self._transaction_id = self.transaction_id
        self._completed = False

    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def is_completed(self) -> bool:
        return self._completed

    def is_debit(self) -> bool:
        """Returns True if this transaction reduces the account balance"""
        return self.transaction_type in (TransactionType.WITHDRAW, TransactionType.TRANSFER)

    def is_credit(self) -> bool:
        """Returns True if this transaction increases the account balance"""
        return self.transaction_type == TransactionType.DEPOSIT

    def get_signed_amount(self) -> float:
        """Returns the amount with proper sign (+/-) based on transaction type"""
        return -self.amount if self.is_debit() else self.amount

    def to_dict(self) -> dict:
        """Converts transaction to dictionary for serialization"""
        return {
            'transaction_id': self.transaction_id,
            'type': self.transaction_type.name,
            'amount': self.amount,
            'account_id': self.account_id,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'related_account': self.related_account,
            'tag': self.tag,
            'is_interest': self.is_interest
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Creates Transaction from dictionary"""
        return cls(
            transaction_id=data.get('transaction_id', str(uuid.uuid4())),
            transaction_type=TransactionType[data['type']],
            amount=data['amount'],
            account_id=data['account_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            description=data.get('description'),
            related_account=data.get('related_account'),
            tag=data.get('tag'),
            is_interest=data.get('is_interest', False)
        )

    def __str__(self) -> str:
        """Human-readable representation"""
        direction = "Credit" if self.is_credit() else "Debit"
        related = f" -> {self.related_account}" if self.related_account else ""
        interest_flag = " [Interest]" if self.is_interest else ""
        return (f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                f"[{self.transaction_id[:8]}] {direction} ${self.amount:.2f} "
                f"on Account: {self.account_id}{related} - "
                f"{self.transaction_type.name}{interest_flag}")

    @abstractmethod
    def execute(self, account_service) -> bool:
        pass

    def execute(self, account_service) -> bool:  # Override abstract method with notification
        result = super().execute(account_service) if hasattr(super(), 'execute') else False
        if result:
            NotificationService().notify(self)  # Trigger notification on success
        return result

class DepositTransaction(Transaction):
    """Concrete deposit transaction"""
    def __init__(self, amount: float, account_id: str):
        super().__init__(TransactionType.DEPOSIT, amount, account_id)

    def execute(self, account_service) -> bool:
        account = account_service.get_account(self.account_id)
        if account and account.deposit(self.amount):
            self._completed = True
            return True
        return False

class WithdrawalTransaction(Transaction):
    """Concrete withdrawal transaction"""
    def __init__(self, amount: float, account_id: str):
        super().__init__(TransactionType.WITHDRAW, amount, account_id)

    def execute(self, account_service) -> bool:
        account = account_service.get_account(self.account_id)
        if account and account.withdraw(self.amount):
            self._completed = True
            return True
        return False

class TransferTransaction(Transaction):
    """Transfer transaction that handles both accounts atomically"""
    def __init__(self, amount: float, source_account_id: str, destination_account_id: str):
        super().__init__(TransactionType.TRANSFER, amount, source_account_id)
        self.destination_account_id = destination_account_id

    def execute(self, account_service) -> bool:
        source = account_service.get_account(self.account_id)
        destination = account_service.get_account(self.destination_account_id)

        if not source or not destination:
            return False

        if source.prepare_for_transfer(self.amount):
            if destination.complete_transfer(self.amount):
                self._completed = True
                return True
            else:
                source.complete_transfer(self.amount)
        return False