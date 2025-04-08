# infrastructure/repositories/memory/account_repository.py
from typing import Dict, List, Optional
from domain.models.account import Account
from domain.ports.account_repository import AccountRepository

class MemoryAccountRepository(AccountRepository):
    def __init__(self):
        self._storage: Dict[int, Account] = {}
        self._counter = 1

    def create(self, account: Account) -> Account:
        account.id = self._counter
        self._storage[account.id] = account
        self._counter += 1
        return account

    def find_by_id(self, account_id: int) -> Optional[Account]:
        return self._storage.get(account_id)

    def find_all(self) -> List[Account]:
        return list(self._storage.values())

    def delete(self, account_id: int) -> bool:
        if account_id not in self._storage:
            return False
        del self._storage[account_id]
        return True

    def update(self, account: Account) -> Account:
        if account.id not in self._storage:
            raise ValueError("Account not found")
        self._storage[account.id] = account
        return account