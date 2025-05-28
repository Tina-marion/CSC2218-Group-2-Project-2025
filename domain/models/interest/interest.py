from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP


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
