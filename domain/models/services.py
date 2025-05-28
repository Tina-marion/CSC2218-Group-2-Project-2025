from typing import List
import logging
from domain.models.account import Account, AccountType, CheckingAccount, SavingsAccount
from domain.models.notifications import NotificationService
from domain.models.transaction import Transaction, TransactionType


class AccountService:
    @staticmethod
    def create_account(account_type: AccountType, account_id: str, initial_balance: float = 0.0) -> Account:
        if account_type == AccountType.CHECKING:
            return CheckingAccount(account_id, initial_balance)
        elif account_type == AccountType.SAVINGS:
            return SavingsAccount(account_id, initial_balance)
        else:
            raise ValueError(f"Unsupported account type: {account_type}")

    @staticmethod
    def get_account_balance(account: Account) -> float:
        return account.balance

    @staticmethod
    def get_transaction_history(account: Account) -> List[Transaction]:
        return account.get_transaction_history()

class TransactionService:
    @staticmethod
    def deposit(account: Account, amount: float) -> None:
        account.deposit(amount)

    @staticmethod
    def withdraw(account: Account, amount: float) -> None:
        account.withdraw(amount)


# Transfer-specific domain service
class TransferService:
    def __init__(self, notification_service: NotificationService):
        self._notification_service = notification_service
        self._logger = logging.getLogger('banking.transfer')

    def transfer(
        self, 
        source_account: Account, 
        destination_account: Account, 
        amount: float
    ) -> None:
        # Validate accounts
        if source_account.account_id == destination_account.account_id:
            raise ValueError("Cannot transfer to the same account")

        # Log transfer initiation
        self._logger.info(
            f"Transfer initiated: {source_account.account_id} -> "
            f"{destination_account.account_id}, Amount: {amount}"
        )

        try:
            # Withdraw from source
            source_account.withdraw(amount)
            
            # Deposit to destination
            destination_account.deposit(amount)

            # Create transfer transactions
            source_tx = Transaction(
                transaction_type=TransactionType.TRANSFER,
                amount=amount,
                account_id=source_account.account_id,
                related_account_id=destination_account.account_id
            )
            destination_tx = Transaction(
                transaction_type=TransactionType.TRANSFER,
                amount=amount,
                account_id=destination_account.account_id,
                related_account_id=source_account.account_id
            )
            
            source_account._transactions.append(source_tx)
            destination_account._transactions.append(destination_tx)

            # Notify both accounts
            self._notification_service.notify(
                source_account.account_id,
                f"Transfer of ${amount:.2f} to account {destination_account.account_id}"
            )
            self._notification_service.notify(
                destination_account.account_id,
                f"Transfer of ${amount:.2f} received from account {source_account.account_id}"
            )

            self._logger.info("Transfer completed successfully")

        except Exception as e:
            self._logger.error(f"Transfer failed: {str(e)}")
            raise

# Transaction logging decorator
class LoggedTransactionService:
    def __init__(self, transaction_service: 'TransactionService'):
        self._transaction_service = transaction_service
        self._logger = logging.getLogger('banking.transactions')

    def deposit(self, account: Account, amount: float) -> None:
        self._logger.info(f"Deposit initiated: {account.account_id}, Amount: {amount}")
        try:
            self._transaction_service.deposit(account, amount)
            self._logger.info(f"Deposit successful: {account.account_id}, Amount: {amount}")
        except Exception as e:
            self._logger.error(f"Deposit failed: {str(e)}")
            raise

    def withdraw(self, account: Account, amount: float) -> None:
        self._logger.info(f"Withdrawal initiated: {account.account_id}, Amount: {amount}")
        try:
            self._transaction_service.withdraw(account, amount)
            self._logger.info(f"Withdrawal successful: {account.account_id}, Amount: {amount}")
        except Exception as e:
            self._logger.error(f"Withdrawal failed: {str(e)}")
            raise        