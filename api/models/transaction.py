from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class Transaction:
    def __init__(self, transaction_id: str, transaction_type: TransactionType, amount: float, account_id: str):
        self.transaction_id = transaction_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.timestamp = datetime.now()
        self.account_id = account_id
