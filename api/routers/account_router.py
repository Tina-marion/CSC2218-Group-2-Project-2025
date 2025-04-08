from fastapi import APIRouter, Depends, HTTPException
from api.controllers.account_controller import AccountController
from api.models.request_models import AccountCreate
from api.models.response_models import AccountResponse
from api.dependencies.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=AccountResponse)
def create_account(account: AccountCreate, username: str = Depends(get_current_user)):
    try:
        return AccountController.create_account(account)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, username: str = Depends(get_current_user)):
    try:
        return AccountController.get_account(account_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=list[AccountResponse])
def get_all_accounts(username: str = Depends(get_current_user)):
    return AccountController.get_all_accounts()