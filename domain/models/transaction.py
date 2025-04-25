from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional

class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TRANSFER = "transfer"

class Transaction(ABC):
    """Base transaction class"""
    def __init__(self, transaction_id: str, transaction_type: TransactionType, 
                 amount: float, account_id: str):
        self._transaction_id = transaction_id
        self._transaction_type = transaction_type
        self._amount = amount
        self._account_id = account_id
        self._timestamp = datetime.now()
        self._completed = False

    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def is_completed(self) -> bool:
        return self._completed

    @abstractmethod
    def execute(self, account_service) -> bool:
        pass

    def __str__(self) -> str:
        status = "completed" if self._completed else "pending"
        return f"{self._transaction_type.value.capitalize()} of ${self._amount:.2f} ({status}) on {self._timestamp}"

class DepositTransaction(Transaction):
    """ Concrete deposit transaction"""
    def __init__(self, transaction_id: str, amount: float, account_id: str):
        super().__init__(transaction_id, TransactionType.DEPOSIT, amount, account_id)

    def execute(self, account_service) -> bool:
        account = account_service.get_account(self._account_id)
        if account and account.deposit(self._amount):
            self._completed = True
            return True
        return False

class WithdrawalTransaction(Transaction):
    """ Concrete withdrawal transaction"""
    def __init__(self, transaction_id: str, amount: float, account_id: str):
        super().__init__(transaction_id, TransactionType.WITHDRAW, amount, account_id)

    def execute(self, account_service) -> bool:
        account = account_service.get_account(self._account_id)
        if account and account.withdraw(self._amount):
            self._completed = True
            return True
        return False

class TransferTransaction(Transaction):
    """ Transfer transaction that handles both accounts atomically"""
    def __init__(self, transaction_id: str, amount: float, 
                 source_account_id: str, destination_account_id: str):
        super().__init__(transaction_id, TransactionType.TRANSFER, amount, source_account_id)
        self._destination_account_id = destination_account_id

    def execute(self, account_service) -> bool:
        source = account_service.get_account(self._account_id)
        destination = account_service.get_account(self._destination_account_id)
        
        if not source or not destination:
            return False
        
        #  Atomic transfer logic
        if source.prepare_for_transfer(self._amount):
            if destination.complete_transfer(self._amount):
                self._completed = True
                return True
            else:
                # Rollback if deposit fails
                source.complete_transfer(self._amount)
        return False