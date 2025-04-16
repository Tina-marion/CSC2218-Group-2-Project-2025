from pydantic import BaseModel

class AccountCreate(BaseModel):
    name: str
    initial_balance: float

class TransactionCreate(BaseModel):
    account_id: int
    amount: float
    transaction_type: str  # "deposit" or "withdrawal"