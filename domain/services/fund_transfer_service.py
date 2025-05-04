from domain.models.transaction import TransferTransaction
from domain.models.account import Account
from domain.services.account_service import BankAccountService
from datetime import datetime

class FundTransferService:
    def __init__(self, account_service: BankAccountService):
        self.account_service = account_service

    def transfer_funds(self, source_account_id: str, destination_account_id: str, amount: float) -> bool:
        """Transfer funds from source to destination account with balance check."""
        source = self.account_service.get_account(source_account_id)
        destination = self.account_service.get_account(destination_account_id)

        if not source or not destination:
            return False

        if not source.can_withdraw(amount):
            return False

        if source.withdraw(amount):
            if destination.deposit(amount):
                # Record the transfer transaction
                transaction = TransferTransaction(
                    amount=amount,
                    source_account_id=source_account_id,
                    destination_account_id=destination_account_id
                )
                self.account_service.execute_transaction(transaction)
                return True
            else:
                # Rollback withdrawal if deposit fails
                source.deposit(amount)
        return False