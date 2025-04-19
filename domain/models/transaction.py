from datetime import datetime
from enum import Enum, auto
from typing import Optional
from dataclasses import dataclass, field
from threading import Lock
import uuid


class TransactionType(Enum):
    """Enum representing different types of transactions"""
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    TRANSFER = auto()
    INTEREST = auto()
    FEE = auto()


@dataclass
class Transaction:
    transaction_type: TransactionType
    amount: float
    account_id: str
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None
    related_account: Optional[str] = None

    # Lock for any future thread-safe operations
    _lock: Lock = field(default_factory=Lock, init=False, repr=False)

    def __post_init__(self):
        """Validation after initialization"""
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")

    def is_debit(self) -> bool:
        """Returns True if this transaction reduces the account balance"""
        return self.transaction_type in (
            TransactionType.WITHDRAWAL,
            TransactionType.FEE,
            TransactionType.TRANSFER
        )

    def is_credit(self) -> bool:
        """Returns True if this transaction increases the account balance"""
        return self.transaction_type in (
            TransactionType.DEPOSIT,
            TransactionType.INTEREST
        )

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
            'related_account': self.related_account
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
            related_account=data.get('related_account')
        )

    def __str__(self) -> str:
        """Human-readable representation"""
        direction = "Credit" if self.is_credit() else "Debit"
        related = f" -> {self.related_account}" if self.related_account else ""
        return (f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                f"[{self.transaction_id[:8]}] {direction} "
                f"${self.amount:.2f} on Account: {self.account_id}{related} - {self.transaction_type.name}")
