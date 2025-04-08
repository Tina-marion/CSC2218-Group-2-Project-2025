# domain/models/transaction.py
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, validator

class TransactionType(str, Enum):
    """Defines allowed transaction types"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

class Transaction(BaseModel):
    """Core domain model for financial transactions"""
    id: Optional[int] = None  # Will be set by repository
    account_id: int
    amount: float = Field(..., gt=0)
    type: TransactionType
    timestamp: datetime = Field(default_factory=datetime.now)

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v