# domain/models/account.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator

class Account(BaseModel):
    """Core domain model for a bank account"""
    id: Optional[int] = None  # Will be set by repository
    name: str = Field(..., min_length=2, max_length=50)
    balance: float = Field(default=0.0, ge=0)
    created_at: datetime = Field(default_factory=datetime.now)

    def deposit(self, amount: float) -> None:
        """Business rule: Deposit must be positive"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        """Business rules: 
        - Withdrawal must be positive
        - Cannot overdraw account
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount