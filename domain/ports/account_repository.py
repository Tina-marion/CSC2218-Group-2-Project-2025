
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.account import Account

class AccountRepository(ABC):
    """Interface for account persistence"""
    @abstractmethod
    def create(self, account: Account) -> Account:
        pass
    
    @abstractmethod
    def find_by_id(self, account_id: int) -> Optional[Account]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Account]:
        pass
    
    @abstractmethod
    def delete(self, account_id: int) -> bool:
        pass
    
    @abstractmethod
    def update(self, account: Account) -> Account:
        pass