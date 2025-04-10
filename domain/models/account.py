from datetime import datetime
from enum import Enum

class AccountStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"

class Account:
    """Represents a bank account with basic functionality"""
    
    def __init__(self, account_id: str, account_type: str, initial_balance: float = 0.0):
        """
        Initialize a new account
        
        Args:
            account_id: Unique identifier for the account
            account_type: Type of account (e.g., "checking", "savings")
            initial_balance: Starting balance (default 0.0)
        """
        self.account_id = account_id
        self.account_type = account_type
        self.balance = initial_balance
        self.status = AccountStatus.ACTIVE
        self.creation_date = datetime.now()
        
    def deposit(self, amount: float) -> bool:
        """Deposit money into the account"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        if self.status != AccountStatus.ACTIVE:
            raise ValueError("Cannot deposit to a closed account")
            
        self.balance += amount
        return True
        
    def withdraw(self, amount: float) -> bool:
        """Withdraw money from the account"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self.status != AccountStatus.ACTIVE:
            raise ValueError("Cannot withdraw from a closed account")
        if self.balance < amount:
            return False
            
        self.balance -= amount
        return True
        
    def close_account(self) -> bool:
        """Close the account"""
        if self.status == AccountStatus.CLOSED:
            return False
            
        self.status = AccountStatus.CLOSED
        return True
        
    def __str__(self) -> str:
        return (f"Account(ID: {self.account_id}, Type: {self.account_type}, "
                f"Balance: {self.balance:.2f}, Status: {self.status.value}, "
                f"Created: {self.creation_date.strftime('%Y-%m-%d %H:%M:%S')}")
