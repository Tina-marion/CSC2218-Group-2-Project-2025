from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime
from typing import Optional, Dict
import uuid
from threading import Lock
from decimal import Decimal
from dataclasses import dataclass, field


class AccountStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"


class AccountType(Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"


class TransactionType(Enum):
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    TRANSFER_OUT = auto()
    TRANSFER_IN = auto()
    INTEREST = auto()
    FEE = auto()


# Data class for transaction record
@dataclass
class Transaction:
    transaction_type: TransactionType
    amount: float
    account_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    source_account_id: Optional[str] = None
    destination_account_id: Optional[str] = None


# Abstract transaction template
class AbstractTransaction(ABC):
    def __init__(self, amount: Decimal, account_id: str, description: Optional[str] = None):
        self.transaction_id: str = str(uuid.uuid4())
        self.amount: Decimal = Decimal(amount)
        self.account_id: str = account_id
        self.timestamp: datetime = datetime.now()
        self.description: str = description or self._default_description()
        self._validate()

    def execute(self, account: 'Account') -> bool:
        if not self._pre_execute_checks(account):
            return False
        self._apply_balance_change(account)
        account.add_transaction(self.to_concrete_transaction())
        self._post_execute_actions(account)
        return True

    @abstractmethod
    def _validate(self) -> None:
        pass

    @abstractmethod
    def _pre_execute_checks(self, account: 'Account') -> bool:
        pass

    @abstractmethod
    def _apply_balance_change(self, account: 'Account') -> None:
        pass

    @abstractmethod
    def _default_description(self) -> str:
        pass

    @abstractmethod
    def to_concrete_transaction(self) -> Transaction:
        pass

    def _post_execute_actions(self, account: 'Account') -> None:
        pass


# Concrete transactions
class DepositTransaction(AbstractTransaction):
    def _validate(self) -> None:
        if self.amount <= Decimal('0'):
            raise ValueError("Deposit amount must be positive")

    def _pre_execute_checks(self, account: 'Account') -> bool:
        return account.status == AccountStatus.ACTIVE

    def _apply_balance_change(self, account: 'Account') -> None:
        account._increase_balance(float(self.amount))

    def _default_description(self) -> str:
        return "Deposit transaction"

    def to_concrete_transaction(self) -> Transaction:
        return Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=float(self.amount),
            account_id=self.account_id,
            description=self.description
        )


class WithdrawalTransaction(AbstractTransaction):
    def _validate(self) -> None:
        if self.amount <= Decimal('0'):
            raise ValueError("Withdrawal amount must be positive")

    def _pre_execute_checks(self, account: 'Account') -> bool:
        return account.status == AccountStatus.ACTIVE and account.can_withdraw(float(self.amount))

    def _apply_balance_change(self, account: 'Account') -> None:
        account._decrease_balance(float(self.amount))

    def _default_description(self) -> str:
        return "Withdrawal transaction"

    def to_concrete_transaction(self) -> Transaction:
        return Transaction(
            transaction_type=TransactionType.WITHDRAWAL,
            amount=float(self.amount),
            account_id=self.account_id,
            description=self.description
        )


class TransferOutTransaction(AbstractTransaction):
    def __init__(self, amount: Decimal, account_id: str,
                 destination_account_id: str, description: Optional[str] = None):
        self.destination_account_id = destination_account_id
        super().__init__(amount, account_id, description)

    def _validate(self) -> None:
        if self.amount <= Decimal('0'):
            raise ValueError("Transfer amount must be positive")

    def _pre_execute_checks(self, account: 'Account') -> bool:
        return account.status == AccountStatus.ACTIVE and account.can_withdraw(float(self.amount))

    def _apply_balance_change(self, account: 'Account') -> None:
        account._decrease_balance(float(self.amount))

    def _default_description(self) -> str:
        return f"Transfer to account {self.destination_account_id}"

    def to_concrete_transaction(self) -> Transaction:
        return Transaction(
            transaction_type=TransactionType.TRANSFER_OUT,
            amount=float(self.amount),
            account_id=self.account_id,
            source_account_id=self.account_id,
            destination_account_id=self.destination_account_id,
            description=self.description
        )


# Account entities
class Account(ABC):
    def __init__(self, account_id: str, account_type: AccountType, 
                 balance: float = 0.0, owner_id: Optional[str] = None):
        self._account_id = account_id
        self._account_type = account_type
        self._balance = balance
        self._status = AccountStatus.ACTIVE
        self._creation_date = datetime.now()
        self._owner_id = owner_id
        self._transactions = []

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def status(self) -> AccountStatus:
        return self._status

    def deposit(self, amount: float) -> bool:
        if amount > 0 and self._status == AccountStatus.ACTIVE:
            self._balance += amount
            return True
        return False

    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        """ Abstract withdrawal method for account-specific behavior"""
        pass

    def can_withdraw(self, amount: float) -> bool:
        """ Additional check for transfer operations """
        return self._status == AccountStatus.ACTIVE and amount > 0

    def close_account(self) -> None:
        self._status = AccountStatus.CLOSED

    def _increase_balance(self, amount: float) -> None:
        self._balance += amount

    def _decrease_balance(self, amount: float) -> None:
        if self._balance >= amount:
            self._balance -= amount

    def add_transaction(self, transaction: Transaction) -> None:
        self._transactions.append(transaction)

    def __str__(self) -> str:
        return f"{self._account_type.value.capitalize()} Account {self._account_id}: Balance ${self._balance:.2f}"


class CheckingAccount(Account):
    """ Account type with overdraft protection """
    def __init__(self, account_id: str, balance: float = 0.0, owner_id: Optional[str] = None):
        super().__init__(account_id, AccountType.CHECKING, balance, owner_id)
        self._overdraft_limit = 100.00

    def withdraw(self, amount: float) -> bool:
        if self.can_withdraw(amount) and (self._balance - amount) >= -self._overdraft_limit:
            self._balance -= amount
            return True
        return False


class SavingsAccount(Account):
    """ Account type with no overdraft """
    def __init__(self, account_id: str, balance: float = 0.0, owner_id: Optional[str] = None):
        super().__init__(account_id, AccountType.SAVINGS, balance, owner_id)
        self._minimum_balance = 10.00  # Minimum balance requirement

    def withdraw(self, amount: float) -> bool:
        if self.can_withdraw(amount) and (self.balance - amount) >= self._minimum_balance:
            self._balance -= amount
            return True
        return False


# Account repository interface
class AccountRepository(ABC):
    @abstractmethod
    def find_account_by_id(self, account_id: str) -> Optional[Account]:
        pass

    @abstractmethod
    def update_account(self, account: Account) -> None:
        pass


# In-memory account repository
class InMemoryAccountRepository(AccountRepository):
    def __init__(self):
        self.accounts: Dict[str, Account] = {}

    def add_account(self, account: Account) -> None:
        self.accounts[account.account_id] = account

    def find_account_by_id(self, account_id: str) -> Optional[Account]:
        return self.accounts.get(account_id)

    def update_account(self, account: Account) -> None:
        self.accounts[account.account_id] = account


# Transfer service
class TransferService:
    def __init__(self, account_repository: AccountRepository):
        self._repo = account_repository
        self._transfer_lock = Lock()

    def transfer(self, source_id: str, dest_id: str, amount: Decimal, description: str = "") -> bool:
        with self._transfer_lock:
            source = self._repo.find_account_by_id(source_id)
            dest = self._repo.find_account_by_id(dest_id)

            if not source or not dest:
                return False

            transfer_out = TransferOutTransaction(
                amount=amount,
                account_id=source_id,
                destination_account_id=dest_id,
                description=description
            )

            transfer_in = DepositTransaction(
                amount=amount,
                account_id=dest_id,
                description=description
            )

            success = transfer_out.execute(source)
            if success:
                success = transfer_in.execute(dest)
                if not success:
                    # Rollback
                    DepositTransaction(amount, source_id, "Transfer rollback").execute(source)
                    return False

                self._repo.update_account(source)
                self._repo.update_account(dest)
                return True
            return False
