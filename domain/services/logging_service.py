from datetime import datetime
import logging
from domain.services.account_service import BankAccountService, AccountService
from domain.models.transaction import Transaction
from domain.models.account import Account
from typing import Dict, Optional

logging.basicConfig(
    filename='bank_operations.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LoggingService(AccountService):
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

    def apply_interest_to_account(self, account_id: str) -> bool:
        self.logger.info(f"Applying interest to account {account_id}")
        return self.account_service.apply_interest_to_account(account_id)

    def apply_interest_batch(self, account_ids: list[str]) -> int:
        self.logger.info(f"Applying interest batch to accounts {account_ids}")
        return self.account_service.apply_interest_batch(account_ids)

    def generate_statement(self, account_id: str, start_date: datetime, end_date: datetime) -> str:
        self.logger.info(f"Generating statement for account {account_id} from {start_date} to {end_date}")
        return self.account_service.generate_statement(account_id, start_date, end_date)

    def reset_daily_limits(self):
        self.logger.info("Resetting daily limits for all accounts")
        self.account_service.reset_daily_limits()

    def reset_monthly_limits(self):
        self.logger.info("Resetting monthly limits for all accounts")
        self.account_service.reset_monthly_limits()