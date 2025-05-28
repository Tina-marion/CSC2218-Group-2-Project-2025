from abc import ABC, abstractmethod
from datetime import datetime
from domain.models.account import Account, CheckingAccount, SavingsAccount
from domain.models.transaction import Transaction, TransferTransaction, WithdrawalTransaction, DepositTransaction
from domain.services.fund_transfer_service import FundTransferService
from domain.services.interest_service import InterestService
from domain.services.limit_enforcement_service import LimitEnforcementService
from domain.services.statement_service import StatementService
from domain.services.notification_service import NotificationService # type: ignore
from typing import Dict, Optional
import uuid

class AccountService(ABC):
    @abstractmethod
    def create_account(self, account_type: str, initial_balance: float = 0.0, 
                      owner_id: Optional[str] = None) -> Account:
        pass

    @abstractmethod
    def get_account(self, account_id: str) -> Optional[Account]:
        pass

    @abstractmethod
    def deposit(self, account_id: str, amount: float) -> bool:
        pass

    @abstractmethod
    def withdraw(self, account_id: str, amount: float) -> bool:
        pass

    @abstractmethod
    def transfer(self, source_account_id: str, target_account_id: str, amount: float) -> bool:
        pass

    @abstractmethod
    def get_account_balance(self, account_id: str) -> Optional[float]:
        pass

    @abstractmethod
    def execute_transaction(self, transaction: Transaction) -> bool:
        pass

class BankAccountService(AccountService):
    """Concrete implementation of AccountService"""
    
    def __init__(self):
        self._accounts: Dict[str, Account] = {}
        self.transfer_service = FundTransferService(self)
        self.interest_service = InterestService(self)
        self.limit_service = LimitEnforcementService(self)
        self.statement_service = StatementService(self)
        self.notification_service = NotificationService()
        
    def create_account(self, account_type: str, initial_balance: float = 0.0, 
                       owner_id: Optional[str] = None) -> Account:
        account_id = str(uuid.uuid4())
        if account_type.lower() == "checking":
            account = CheckingAccount(account_id, initial_balance, owner_id)
        else:
            account = SavingsAccount(account_id, initial_balance, owner_id)
        self._accounts[account_id] = account
        return account

    def get_account(self, account_id: str) -> Optional[Account]:
        return self._accounts.get(account_id)

    def deposit(self, account_id: str, amount: float) -> bool:
        if self.limit_service.check_limit(account_id, amount):
            account = self.get_account(account_id)
            if account:
                success = account.deposit(amount)
                if success:
                    self.notification_service.notify(DepositTransaction(amount, account_id))
                return success
        return False

    def withdraw(self, account_id: str, amount: float) -> bool:
        if self.limit_service.check_limit(account_id, amount):
            account = self.get_account(account_id)
            if account:
                success = account.withdraw(amount)
                if success:
                    self.notification_service.notify(WithdrawalTransaction(amount, account_id))
                return success
        return False

    def transfer(self, source_account_id: str, target_account_id: str, amount: float) -> bool:
        if self.limit_service.check_limit(source_account_id, amount):
            success = self.transfer_service.transfer_funds(source_account_id, target_account_id, amount)
            if success:
                transaction = TransferTransaction(amount, source_account_id, target_account_id)
                self.notification_service.notify(transaction)
            return success
        return False

    def get_account_balance(self, account_id: str) -> Optional[float]:
        account = self.get_account(account_id)
        return account.balance if account else None

    def execute_transaction(self, transaction: Transaction) -> bool:
        """Unified transaction execution with limit check"""
        if self.limit_service.check_limit(transaction.account_id, transaction.amount):
            success = transaction.execute(self)
            if success:
                self.notification_service.notify(transaction)
            return success
        return False

    def apply_interest_to_account(self, account_id: str) -> bool:
        """Apply interest to a single account."""
        return self.interest_service.apply_interest_to_account(account_id)

    def apply_interest_batch(self, account_ids: list[str]) -> int:
        """Apply interest to multiple accounts."""
        return self.interest_service.apply_interest_batch(account_ids)

    def generate_statement(self, account_id: str, start_date: datetime, end_date: datetime) -> str:
        """Generate CSV statement for an account."""
        return self.statement_service.generate_statement(account_id, start_date, end_date)

    def reset_daily_limits(self):
        """Reset daily limits for all accounts."""
        self.limit_service.reset_limits_daily()

    def reset_monthly_limits(self):
        """Reset monthly limits for all accounts."""
        self.limit_service.reset_monthly_limits()