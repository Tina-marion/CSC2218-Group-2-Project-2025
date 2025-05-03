from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import Dict, Optional

from domain.entities.account import AccountType
from domain.models.transaction_limits import TransactionLimit

class InterestStrategy(ABC):
    @abstractmethod
    def calculate_interest(self, balance: Decimal, days: int) -> Decimal:
        pass

class NoInterestStrategy(InterestStrategy):
    def calculate_interest(self, balance: Decimal, days: int) -> Decimal:
        return Decimal('0')

class SavingsInterestStrategy(InterestStrategy):
    def __init__(self, annual_rate: Decimal = Decimal('0.02')):
        self._annual_rate = annual_rate

    def calculate_interest(self, balance: Decimal, days: int) -> Decimal:
        if balance <= 0:
            return Decimal('0')
        daily_rate = self._annual_rate / Decimal('365')
        return (balance * daily_rate * Decimal(days)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

class CheckingInterestStrategy(InterestStrategy):
    def __init__(self, annual_rate: Decimal = Decimal('0.001')):
        self._annual_rate = annual_rate

    def calculate_interest(self, balance: Decimal, days: int) -> Decimal:
        if balance <= 0:
            return Decimal('0')
        daily_rate = self._annual_rate / Decimal('365')
        return (balance * daily_rate * Decimal(days)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

class Account(ABC):
    def __init__(self, account_id: str, account_type: AccountType, initial_balance: float = 0.0):
        # ... (existing initialization)
        self._interest_strategy: InterestStrategy = NoInterestStrategy()
        self._last_interest_calculation_date: Optional[date] = None
        self._interest_earned: Decimal = Decimal('0')
        self._transaction_limits: Dict[str, 'TransactionLimit'] = {}

    def set_interest_strategy(self, strategy: InterestStrategy) -> None:
        self._interest_strategy = strategy

    def calculate_interest(self, as_of_date: date = date.today()) -> Decimal:
        if self._last_interest_calculation_date is None:
            self._last_interest_calculation_date = as_of_date
            return Decimal('0')

        days = (as_of_date - self._last_interest_calculation_date).days
        if days <= 0:
            return Decimal('0')

        interest = self._interest_strategy.calculate_interest(
            Decimal(str(self._balance)), 
            days
        )
        self._interest_earned += interest
        self._last_interest_calculation_date = as_of_date
        return interest

    def get_interest_earned(self) -> Decimal:
        return self._interest_earned

    # ... (rest of Account class)