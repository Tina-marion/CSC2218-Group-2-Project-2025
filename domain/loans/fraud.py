from abc import ABC, abstractmethod
from datetime import timedelta
from decimal import Decimal
from typing import Optional
from domain.entities.account import Account
from domain.entities.transaction import Transaction


class FraudDetectionResult:
    def __init__(self, is_fraud: bool, message: str = ""):
        self.is_fraud = is_fraud
        self.message = message

class FraudDetectionHandler(ABC):
    def __init__(self, next_handler: Optional['FraudDetectionHandler'] = None):
        self._next_handler = next_handler

    @abstractmethod
    def handle(self, transaction: Transaction, account: Account) -> FraudDetectionResult:
        pass

    def _next(self, transaction: Transaction, account: Account) -> FraudDetectionResult:
        if self._next_handler:
            return self._next_handler.handle(transaction, account)
        return FraudDetectionResult(False)

class HighAmountCheck(FraudDetectionHandler):
    def __init__(self, threshold: Decimal, next_handler: Optional[FraudDetectionHandler] = None):
        super().__init__(next_handler)
        self._threshold = threshold

    def handle(self, transaction: Transaction, account: Account) -> FraudDetectionResult:
        if Decimal(str(transaction.amount)) > self._threshold:
            return FraudDetectionResult(
                True,
                f"Transaction amount {transaction.amount} exceeds threshold {self._threshold}"
            )
        return self._next(transaction, account)

class UnusualFrequencyCheck(FraudDetectionHandler):
    def __init__(self, max_transactions: int, time_window_hours: int, 
                 next_handler: Optional[FraudDetectionHandler] = None):
        super().__init__(next_handler)
        self._max_transactions = max_transactions
        self._time_window = timedelta(hours=time_window_hours)

    def handle(self, transaction: Transaction, account: Account) -> FraudDetectionResult:
        recent_transactions = [
            tx for tx in account.get_transaction_history()
            if transaction.timestamp - tx.timestamp <= self._time_window
        ]
        if len(recent_transactions) >= self._max_transactions:
            return FraudDetectionResult(
                True,
                f"Too many transactions ({len(recent_transactions)}) in last {self._time_window}"
            )
        return self._next(transaction, account)

class LocationAnomalyCheck(FraudDetectionHandler):
    def handle(self, transaction: Transaction, account: Account) -> FraudDetectionResult:
        # In a real implementation, we'd check transaction location against account patterns
        return self._next(transaction, account)

class FraudDetectionService:
    def __init__(self):
        self._handler = self._build_chain()

    def _build_chain(self) -> FraudDetectionHandler:
        return HighAmountCheck(
            Decimal("10000"),  # $10,000 threshold
            UnusualFrequencyCheck(
                10,  # max 10 transactions
                24,  # in 24 hours
                LocationAnomalyCheck()
            )
        )

    def check_transaction(self, transaction: Transaction, account: Account) -> FraudDetectionResult:
        return self._handler.handle(transaction, account)