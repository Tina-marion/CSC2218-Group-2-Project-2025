from datetime import datetime
from enum import Enum, auto
from typing import List
from .transaction import Transaction, TransactionType

class AccountStatus(Enum):
    """Representing account statuses"""
    ACTIVE = auto()
    CLOSED = auto()
    FROZEN = auto()

class Account:
    """Represents a bank account with transaction capabilities"""
    
    def __init__(self, account_id: str, account_type: str, initial_balance: float = 0.0):
        """
        Initialize a new bank account
        
        Args:
            account_id: Unique account identifier
            account_type: Type of account ('checking' or 'savings')
            initial_balance: Starting balance (default 0.0)
        """
        self.account_id = account_id
        self.account_type = account_type
        self.balance = initial_balance
        self.status = AccountStatus.ACTIVE
        self.creation_date = datetime.now()
        self.transactions: List[Transaction] = []
        
    def deposit(self, amount: float) -> bool:
        """Deposit money into the account"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
            
        self.balance += amount
        self.transactions.append(
            Transaction(
                transaction_id=f"DEP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                transaction_type=TransactionType.DEPOSIT,
                amount=amount,
                account_id=self.account_id,
                description="Deposit"
            )
        )
        return True
        
    def withdraw(self, amount: float) -> bool:
        """Withdraw money from the account"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
            
        if self.balance >= amount:
            self.balance -= amount
            self.transactions.append(
                Transaction(
                    transaction_id=f"WTH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    transaction_type=TransactionType.WITHDRAWAL,
                    amount=amount,
                    account_id=self.account_id,
                    description="Withdrawal"
                )
            )
            return True
        return False
        
    def close_account(self) -> bool:
        """Close the account if balance is zero"""
        if self.balance == 0:
            self.status = AccountStatus.CLOSED
            return True
        return False
        
    def __str__(self) -> str:
        """String representation of the account"""
        return (f"Account(ID: {self.account_id}, Type: {self.account_type}, "
                f"Balance: {self.balance:.2f}, Status: {self.status.name}, "
                f"Created: {self.creation_date.strftime('%Y-%m-%d')})")