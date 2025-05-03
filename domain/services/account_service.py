from abc import ABC, abstractmethod
from domain.entities.account import Account, CheckingAccount, SavingsAccount
from domain.entities.transaction import Transaction, TransferTransaction
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
        """ Atomic transfer implementation"""
        if source_account_id == target_account_id:
            return False
            
        source = self.get_account(source_account_id)
        target = self.get_account(target_account_id)
        
        if not source or not target:
            return False
            
        # Create and execute transfer transaction
        transaction = TransferTransaction(
            transaction_id=str(uuid.uuid4()),
            amount=amount,
            source_account_id=source_account_id,
            destination_account_id=target_account_id
        )
        
        return self.execute_transaction(transaction)

    def get_account_balance(self, account_id: str) -> Optional[float]:
        account = self.get_account(account_id)
        return account.balance if account else None

    def execute_transaction(self, transaction: Transaction) -> bool:
        """Unified transaction execution"""
        return transaction.execute(self)