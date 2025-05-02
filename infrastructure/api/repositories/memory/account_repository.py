

from typing import Dict, List
from domain.entities import Account, Transaction # type: ignore
from application.services import AccountRepository, TransactionRepository

class InMemoryAccountRepository(AccountRepository):
    def __init__(self):
        self.accounts: Dict[str, Account] = {}

    def create_account(self, account: Account) -> None:
        self.accounts[account.account_id] = account

    def get_account_by_id(self, account_id: str) -> Account | None:
        return self.accounts.get(account_id)

    def update_account(self, account: Account) -> None:
        if account.account_id in self.accounts:
            self.accounts[account.account_id] = account

class InMemoryTransactionRepository(TransactionRepository):
    def __init__(self):
        self.transactions: List[Transaction] = []

    def save_transaction(self, txn: Transaction) -> None:
        self.transactions.append(txn)

    def get_transactions_for_account(self, account_id: str) -> List[Transaction]:
        return [txn for txn in self.transactions if (
            txn.account_id == account_id or
            txn.source_account_id == account_id or
            txn.destination_account_id == account_id
        )]
