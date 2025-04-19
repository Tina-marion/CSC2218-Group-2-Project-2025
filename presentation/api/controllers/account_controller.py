from typing import List, Dict
from datetime import datetime
from api.models.request_models import AccountCreate
from api.models.response_models import AccountResponse

# Simple in-memory database
accounts_db: Dict[int, dict] = {}
account_id_counter = 1

class AccountController:
    @staticmethod
    def create_account(account_data: AccountCreate) -> AccountResponse:
        global account_id_counter
        
        account = {
            "id": account_id_counter,
            "name": account_data.name,
            "balance": account_data.initial_balance,
            "created_at": datetime.now()
        }
        
        accounts_db[account_id_counter] = account
        account_id_counter += 1
        
        return AccountResponse(**account)
    
    @staticmethod
    def get_account(account_id: int) -> AccountResponse:
        if account_id not in accounts_db:
            raise ValueError("Account not found")
        return AccountResponse(**accounts_db[account_id])
    
    @staticmethod
    def get_all_accounts() -> List[AccountResponse]:
        return [AccountResponse(**account) for account in accounts_db.values()]
    
    @staticmethod
    def delete_account(account_id: int) -> bool:
        if account_id not in accounts_db:
            raise ValueError("Account not found")
    
    # Check if account has balance (optional safety check)
        if accounts_db[account_id]["balance"] != 0:
            raise ValueError("Account balance must be zero before deletion")
    
        del accounts_db[account_id]
        return True
    