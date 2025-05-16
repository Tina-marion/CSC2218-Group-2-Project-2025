from abc import ABC, abstractmethod
from domain.entities.account import Account

class AccountRepository(ABC):
    @abstractmethod
    def create_account(self, account: Account) -> str:
        pass
    
    @abstractmethod
    def get_account_by_id(self, account_id: str) -> Account:
        pass
    
    @abstractmethod
    def update_account(self, account: Account) -> None:
        pass