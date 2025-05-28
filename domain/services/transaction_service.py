
class Account:
    def __init__(self, account_id: int, balance: float):
        self.id = account_id
        self.balance = balance

    def deposit(self, amount: float):
        self.balance += amount

    def withdraw(self, amount: float):
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount


class Transaction:
    def __init__(self, account_id: int, amount: float, type: TransactionType):
        self.account_id = account_id
        self.amount = amount
        self.type = type



from domain.models.transaction import Transaction, TransactionType

class TransactionUseCase:
    def __init__(self, account_repo, transaction_repo):
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo

    def execute_transaction(self, account_id: int, amount: float, transaction_type: TransactionType) -> Transaction:
        account = self.account_repo.find_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        transaction = Transaction(account_id, amount, transaction_type)

        if transaction_type == TransactionType.DEPOSIT:
            account.deposit(amount)
        elif transaction_type == TransactionType.WITHDRAWAL:
            account.withdraw(amount)
        else:
            raise ValueError("Invalid transaction type")

        self.account_repo.update(account)
        self.transaction_repo.create(transaction)
        return transaction

    def get_account_transactions(self, account_id: int):
        account = self.account_repo.find_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        return self.transaction_repo.find_by_account_id(account_id)


class InMemoryAccountRepository:
    def __init__(self):
        self.accounts = {}

    def find_by_id(self, account_id: int):
        return self.accounts.get(account_id)

    def update(self, account):
        self.accounts[account.id] = account


# interface_adapters/repositories/transaction_repository.py
class InMemoryTransactionRepository:
    def __init__(self):
        self.transactions = []

    def create(self, transaction):
        self.transactions.append(transaction)

    def find_by_account_id(self, account_id):
        return [t for t in self.transactions if t.account_id == account_id]
