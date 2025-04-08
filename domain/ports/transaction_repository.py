# domain/ports/transaction_repository.py
from abc import ABC, abstractmethod
from typing import List
from domain.models.transaction import Transaction

class TransactionRepository(ABC):
    """Interface for transaction persistence"""
    @abstractmethod
    def create(self, transaction: Transaction) -> Transaction:
        pass
    
    @abstractmethod
    def find_by_account_id(self, account_id: int) -> List[Transaction]:
        pass