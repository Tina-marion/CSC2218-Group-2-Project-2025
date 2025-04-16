from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from models.service import AccountService
from models.transaction import TransactionType

app = FastAPI(title="Bank API")
service = AccountService()

# Request Models
class AccountCreateRequest(BaseModel):
    account_type: str

class TransactionRequest(BaseModel):
    amount: float
    type: str

# Response Models
class AccountResponse(BaseModel):
    id: str
    account_type: str
    balance: float
    status: str

class TransactionResponse(BaseModel):
    amount: float
    type: str
    timestamp: str

@app.get("/")
def home():
    return {"message": "FastAPI Bank Service Running 🚀"}

@app.post("/accounts", response_model=AccountResponse)
def create_account(data: AccountCreateRequest):
    account = service.create_account(data.account_type)
    return {
        "id": account.id,
        "account_type": account.account_type,
        "balance": account.balance,
        "status": account.status
    }

@app.get("/accounts", response_model=List[AccountResponse])
def get_all_accounts():
    return [{
        "id": acc.id,
        "account_type": acc.account_type,
        "balance": acc.balance,
        "status": acc.status
    } for acc in service.accounts.values()]

@app.post("/accounts/{account_id}/transactions", response_model=TransactionResponse)
def make_transaction(account_id: str, data: TransactionRequest):
    try:
        tx = service.perform_transaction(account_id, data.amount, data.type)
        return {
            "amount": tx.amount,
            "type": tx.transaction_type,
            "timestamp": tx.timestamp
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/accounts/{account_id}/transactions", response_model=List[TransactionResponse])
def get_transactions(account_id: str):
    account = service.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return [{
        "amount": tx.amount,
        "type": tx.transaction_type,
        "timestamp": tx.timestamp
    } for tx in account.transactions]
