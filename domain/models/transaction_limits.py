from abc import ABC, abstractmethod
from datetime import date
from domain.entities.transaction import TransactionType


class TransactionLimit(ABC):
    @abstractmethod
    def check_limit(self, account: 'Account', amount: float) -> None:
        pass

class DailyWithdrawalLimit(TransactionLimit):
    def __init__(self, max_amount: float):
        self._max_amount = max_amount
        self._current_amount: float = 0.0
        self._last_reset_date: date = date.today()

    def check_limit(self, account: 'Account', amount: float) -> None:
        today = date.today()
        if today != self._last_reset_date:
            self._current_amount = 0.0
            self._last_reset_date = today

        if amount + self._current_amount > self._max_amount:
            raise ValueError(
                f"Daily withdrawal limit exceeded. "
                f"Limit: ${self._max_amount:.2f}, "
                f"Used: ${self._current_amount:.2f}, "
                f"Attempted: ${amount:.2f}"
            )

    def record_transaction(self, amount: float) -> None:
        today = date.today()
        if today != self._last_reset_date:
            self._current_amount = 0.0
            self._last_reset_date = today
        self._current_amount += amount

class MonthlyDepositLimit(TransactionLimit):
    def __init__(self, max_amount: float):
        self._max_amount = max_amount
        self._current_amount: float = 0.0
        self._last_reset_month: tuple[int, int] = (date.today().year, date.today().month)

    def check_limit(self, account: 'Account', amount: float) -> None:
        current_month = (date.today().year, date.today().month)
        if current_month != self._last_reset_month:
            self._current_amount = 0.0
            self._last_reset_month = current_month

        if amount + self._current_amount > self._max_amount:
            raise ValueError(
                f"Monthly deposit limit exceeded. "
                f"Limit: ${self._max_amount:.2f}, "
                f"Used: ${self._current_amount:.2f}, "
                f"Attempted: ${amount:.2f}"
            )

    def record_transaction(self, amount: float) -> None:
        current_month = (date.today().year, date.today().month)
        if current_month != self._last_reset_month:
            self._current_amount = 0.0
            self._last_reset_month = current_month
        self._current_amount += amount

class Account(ABC):
    # ... (existing methods)
    
    def add_transaction_limit(self, limit_type: str, limit: TransactionLimit) -> None:
        self._transaction_limits[limit_type] = limit

    def remove_transaction_limit(self, limit_type: str) -> None:
        if limit_type in self._transaction_limits:
            del self._transaction_limits[limit_type]

    def _check_limits(self, transaction_type: TransactionType, amount: float) -> None:
        for limit in self._transaction_limits.values():
            limit.check_limit(self, amount)

    def withdraw(self, amount: float) -> None:
        self._check_limits(TransactionType.WITHDRAW, amount)
        # ... (existing withdrawal logic)
        for limit in self._transaction_limits.values():
            if isinstance(limit, DailyWithdrawalLimit):
                limit.record_transaction(amount)

    def deposit(self, amount: float) -> None:
        self._check_limits(TransactionType.DEPOSIT, amount)
        # ... (existing deposit logic)
        for limit in self._transaction_limits.values():
            if isinstance(limit, MonthlyDepositLimit):
                limit.record_transaction(amount)