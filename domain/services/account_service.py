# domain/services/account_service.py
from typing import List, Optional
from domain.models.account import Account
from domain.ports.account_repository import AccountRepository

class AccountService:
    """Handles account-related business logic"""
    def __init__(self, account_repository: AccountRepository):
        self._repo = account_repository

    def create_account(self, name: str, initial_balance: float = 0.0) -> Account:
        """Creates a new account with validation"""
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        
        account = Account(name=name, balance=initial_balance)
        return self._repo.create(account)

    def get_account(self, account_id: int) -> Optional[Account]:
        """Retrieves an account by ID"""
        return self._repo.find_by_id(account_id)

    def get_all_accounts(self) -> List[Account]:
        """Retrieves all accounts"""
        return self._repo.find_all()

    def delete_account(self, account_id: int) -> bool:
        """Deletes an account if balance is zero"""
        account = self._repo.find_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        if account.balance != 0:
            raise ValueError("Account balance must be zero before deletion")
        return self._repo.delete(account_id)