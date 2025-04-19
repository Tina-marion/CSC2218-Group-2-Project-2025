from typing import List, Dict
from datetime import datetime
from api.models.request_models import TransactionCreate
from api.models.response_models import TransactionResponse
from api.controllers.account_controller import accounts_db

# Simple in-memory database
transactions_db: Dict[int, dict] = {}
transaction_id_counter = 1

class TransactionController:
    @staticmethod
    def create_transaction(transaction_data: TransactionCreate) -> TransactionResponse:
        global transaction_id_counter
        
        # Verify account exists
        if transaction_data.account_id not in accounts_db:
            raise ValueError("Account not found")
        
        # Update account balance
        account = accounts_db[transaction_data.account_id]
        if transaction_data.transaction_type == "deposit":
            account["balance"] += transaction_data.amount
        elif transaction_data.transaction_type == "withdrawal":
            if account["balance"] < transaction_data.amount:
                raise ValueError("Insufficient funds")
            account["balance"] -= transaction_data.amount
        else:
            raise ValueError("Invalid transaction type")
        
        # Create transaction record
        transaction = {
            "id": transaction_id_counter,
            "account_id": transaction_data.account_id,
            "amount": transaction_data.amount,
            "transaction_type": transaction_data.transaction_type,
            "timestamp": datetime.now()
        }
        
        transactions_db[transaction_id_counter] = transaction
        transaction_id_counter += 1
        
        return TransactionResponse(**transaction)
    
    @staticmethod
    def get_account_transactions(account_id: int) -> List[TransactionResponse]:
        if account_id not in accounts_db:
            raise ValueError("Account not found")
        
        return [
            TransactionResponse(**tx) 
            for tx in transactions_db.values() 
            if tx["account_id"] == account_id
        ]