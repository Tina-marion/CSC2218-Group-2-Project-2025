from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class TransactionType(Enum):
    WITHDRAWAL = 1
    DEPOSIT = 2
    TRANSFER = 3
    FEE = 4
    INTEREST = 5

class TransactionTemplate(ABC):
    """Abstract base class defining the transaction template"""
    
    def __init__(self, transaction_id: str, amount: float, account_id: str,
                 timestamp: datetime = datetime.now(),
                 description: Optional[str] = None,
                 related_account: Optional[str] = None):
        self.transaction_id = transaction_id
        self.amount = amount
        self.account_id = account_id
        self.timestamp = timestamp
        self.description = description
        self.related_account = related_account
        
        self.validate()
    
    def validate(self):
        """Template method with common validation"""
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        self._validate_specific()
    
    @abstractmethod
    def _validate_specific(self):
        """Subclasses implement specific validation"""
        pass
    
    @abstractmethod
    def is_debit(self) -> bool:
        """Returns True if this transaction reduces the account balance"""
        pass
    
    def is_credit(self) -> bool:
        """Returns True if this transaction increases the account balance"""
        return not self.is_debit()
    
    def get_signed_amount(self) -> float:
        """Returns the amount with proper sign (+/-) based on transaction type"""
        return -self.amount if self.is_debit() else self.amount
    
    def to_dict(self) -> dict:
        """Converts transaction to dictionary for serialization"""
        return {
            'transaction_id': self.transaction_id,
            'type': self.__class__.__name__,
            'amount': self.amount,
            'account_id': self.account_id,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'related_account': self.related_account
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TransactionTemplate':
        """Factory method to create appropriate transaction from dictionary"""
        transaction_classes = {
            'WithdrawalTransaction': WithdrawalTransaction,
            'DepositTransaction': DepositTransaction,
            'TransferTransaction': TransferTransaction,
            'FeeTransaction': FeeTransaction,
            'InterestTransaction': InterestTransaction
        }
        
        transaction_class = transaction_classes.get(data['type'])
        if not transaction_class:
            raise ValueError(f"Unknown transaction type: {data['type']}")
            
        return transaction_class(
            transaction_id=data['transaction_id'],
            amount=data['amount'],
            account_id=data['account_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            description=data.get('description'),
            related_account=data.get('related_account')
        )

    def __str__(self) -> str:
        """Human-readable representation"""
        return (f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
                f"[{self.transaction_id}] {self.__class__.__name__} "
                f"${self.amount:.2f} (Account: {self.account_id})")

# Concrete Transaction Classes
@dataclass
class WithdrawalTransaction(TransactionTemplate):
    def is_debit(self) -> bool:
        return True
    
    def _validate_specific(self):
        if self.related_account is not None:
            raise ValueError("Withdrawal should not have a related account")

@dataclass
class DepositTransaction(TransactionTemplate):
    def is_debit(self) -> bool:
        return False
    
    def _validate_specific(self):
        if self.related_account is not None:
            raise ValueError("Deposit should not have a related account")

@dataclass
class TransferTransaction(TransactionTemplate):
    def is_debit(self) -> bool:
        return True
    
    def _validate_specific(self):
        if self.related_account is None:
            raise ValueError("Transfer must have a related account")

@dataclass
class FeeTransaction(TransactionTemplate):
    def is_debit(self) -> bool:
        return True
    
    def _validate_specific(self):
        if self.related_account is not None:
            raise ValueError("Fee should not have a related account")

@dataclass
class InterestTransaction(TransactionTemplate):
    def is_debit(self) -> bool:
        return False
    
    def _validate_specific(self):
        if self.related_account is not None:
            raise ValueError("Interest should not have a related account")