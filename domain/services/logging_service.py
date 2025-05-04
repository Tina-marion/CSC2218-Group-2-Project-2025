import logging
from typing import Optional
from domain.services.account_service import BankAccountService
from domain.models.transaction import Transaction
from domain.models.account import Account

logging.basicConfig(
    filename='bank_operations.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LoggingService:
    def __init__(self, account_service: BankAccountService):
        self.account_service = account_service
        self.logger = logging.getLogger("LoggingService")

    def create_account(self, account_type: str, initial_balance: float = 0.0, owner_id: Optional[str] = None) -> Account:
        self.logger.info(f"Creating {account_type} account with initial balance ${initial_balance} for owner {owner_id}")
        return self.account_service.create_account(account_type, initial_balance, owner_id)

    def get_account(self, account_id: str) -> Optional[Account]:
        self.logger.info(f"Retrieving account {account_id}")
        return self.account_service.get_account(account_id)

    def deposit(self, account_id: str, amount: float) -> bool:
        self.logger.info(f"Depositing ${amount} to account {account_id}")
        return self.account_service.deposit(account_id, amount)

    def withdraw(self, account_id: str, amount: float) -> bool:
        self.logger.info(f"Withdrawing ${amount} from account {account_id}")
        return self.account_service.withdraw(account_id, amount)

    def transfer(self, source_account_id: str, target_account_id: str, amount: float) -> bool:
        self.logger.info(f"Transferring ${amount} from {source_account_id} to {target_account_id}")
        return self.account_service.transfer(source_account_id, target_account_id, amount)

    def get_account_balance(self, account_id: str) -> Optional[float]:
        self.logger.info(f"Checking balance for account {account_id}")
        return self.account_service.get_account_balance(account_id)

    def execute_transaction(self, transaction: Transaction) -> bool:
        self.logger.info(f"Executing transaction {transaction.transaction_id} of type {transaction.transaction_type.value}")
        return self.account_service.execute_transaction(transaction)