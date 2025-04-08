from pydantic import BaseModel
from datetime import datetime

class AccountResponse(BaseModel):
    id: int
    name: str
    balance: float
    created_at: datetime

class TransactionResponse(BaseModel):
    id: int
    account_id: int
    amount: float
    transaction_type: str
    timestamp: datetime