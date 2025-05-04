from abc import ABC, abstractmethod
from domain.models.account import Account, CheckingAccount, SavingsAccount
from domain.models.transaction import Transaction, TransferTransaction
from typing import Dict, Optional
import uuid
from domain.services.fund_transfer_service import FundTransferService

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
        account = self.get_account(account_id)
        if account:
            return account.deposit(amount)
        return False

    def withdraw(self, account_id: str, amount: float) -> bool:
        account = self.get_account(account_id)
        if account:
            return account.withdraw(amount)
        return False

    def transfer(self, source_account_id: str, target_account_id: str, amount: float) -> bool:
        """Delegate transfer to FundTransferService"""
        return self.transfer_service.transfer_funds(source_account_id, target_account_id, amount)

    def get_account_balance(self, account_id: str) -> Optional[float]:
        account = self.get_account(account_id)
        return account.balance if account else None

    def execute_transaction(self, transaction: Transaction) -> bool:
        """Unified transaction execution"""
        return transaction.execute(self)