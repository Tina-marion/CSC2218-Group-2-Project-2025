from domain.models.account import AccountType
from domain.models.transaction import DepositTransaction
from domain.services.account_service import BankAccountService

class InterestService:
    def __init__(self, account_service: BankAccountService):
        self.account_service = account_service
        self.interest_rate = 0.02  # 2% annual interest, compounded monthly

    def apply_interest_to_account(self, account_id: str) -> bool:
        """Apply monthly interest to a single account."""
        account = self.account_service.get_account(account_id)
        if not account or account._account_type != AccountType.SAVINGS:  # Apply only to savings
            return False

        interest_amount = account.balance * (self.interest_rate / 12)  # Monthly interest
        if interest_amount > 0:
            transaction = DepositTransaction(
                amount=interest_amount,
                account_id=account_id
            )
            if self.account_service.execute_transaction(transaction):
                account.add_interest(interest_amount)
                return True
        return False

    def apply_interest_batch(self, account_ids: list[str]) -> int:
        """Apply interest to multiple accounts and return the number of successful applications."""
        success_count = 0
        for account_id in account_ids:
            if self.apply_interest_to_account(account_id):
                success_count += 1
        return success_count