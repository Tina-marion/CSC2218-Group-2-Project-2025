from domain.models.transaction import TransferTransaction
from domain.services.account_service import BankAccountService

class FundTransferService:
    def __init__(self, account_service: BankAccountService):
        self.account_service = account_service

    def transfer_funds(self, source_account_id: str, destination_account_id: str, amount: float) -> bool:
        # Validate accounts exist
        source = self.account_service.get_account(source_account_id)
        destination = self.account_service.get_account(destination_account_id)
        if not source or not destination:
            return False
        
        # Validate funds available using domain logic
        if not source.can_withdraw(amount):
            return False
        
        # Create transfer transaction (domain model)
        transaction = TransferTransaction(
            amount=amount,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id
        )
        
        # Delegate execution to domain service to handle atomic withdraw + deposit
        success = self.account_service.execute_transaction(transaction)
        return success
