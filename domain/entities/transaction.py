from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Callable
import logging

# Update TransactionType enum
class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"

# Enhanced Transaction entity
class Transaction:
    def __init__(
        self, 
        transaction_type: TransactionType, 
        amount: float, 
        account_id: str,
        related_account_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self._transaction_type = transaction_type
        self._amount = amount
        self._account_id = account_id
        self._related_account_id = related_account_id
        self._timestamp = timestamp if timestamp else datetime.now()

    @property
    def transaction_type(self) -> TransactionType:
        return self._transaction_type

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def related_account_id(self) -> Optional[str]:
        return self._related_account_id

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    def __repr__(self) -> str:
        return (f"Transaction(type={self._transaction_type.value}, "
                f"amount={self._amount}, "
                f"account_id={self._account_id}, "
                f"related_account={self._related_account_id}, "
                f"timestamp={self._timestamp})")