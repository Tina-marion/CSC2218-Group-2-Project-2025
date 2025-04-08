# infrastructure/repositories/memory/transaction_repository.py
from typing import Dict, List
from domain.models.transaction import Transaction
from domain.ports.transaction_repository import TransactionRepository

class MemoryTransactionRepository(TransactionRepository):
    def __init__(self):
        self._storage: Dict[int, Transaction] = {}
        self._counter = 1

    def create(self, transaction: Transaction) -> Transaction:
        transaction.id = self._counter
        self._storage[transaction.id] = transaction
        self._counter += 1
        return transaction

    def find_by_account_id(self, account_id: int) -> List[Transaction]:
        return [t for t in self._storage.values() if t.account_id == account_id]