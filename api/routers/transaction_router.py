from fastapi import APIRouter, Depends, HTTPException
from api.controllers.transaction_controller import TransactionController
from api.models.request_models import TransactionCreate
from api.models.response_models import TransactionResponse
from api.dependencies.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, username: str = Depends(get_current_user)):
    try:
        return TransactionController.create_transaction(transaction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/account/{account_id}", response_model=list[TransactionResponse])
def get_account_transactions(account_id: int, username: str = Depends(get_current_user)):
    try:
        return TransactionController.get_account_transactions(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))