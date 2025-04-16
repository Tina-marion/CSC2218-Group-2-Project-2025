# presentation/main.py

from domain.entities import CheckingAccount, SavingsAccount # type: ignore
from application.services import AccountCreationService, TransactionService
from infrastructure.repositories import InMemoryAccountRepository, InMemoryTransactionRepository
from infrastructure.notification import LoggingNotificationSender # type: ignore

def main():
    
    account_repo = InMemoryAccountRepository()
    transaction_repo = InMemoryTransactionRepository()
    notification_sender = LoggingNotificationSender()


    account_service = AccountCreationService(account_repo)
    txn_service = TransactionService(account_repo, transaction_repo, notification_sender)

    
    print("=== Creating Accounts ===")
    checking_id = account_service.create_account("CHECKING", owner_id="User123", initial_deposit=100)
    savings_id = account_service.create_account("SAVINGS", owner_id="User123", initial_deposit=500)
    
    print("\nAccounts Created:")
    print(account_repo.get_account_by_id(checking_id))
    print(account_repo.get_account_by_id(savings_id))

    print("\n=== Depositing Funds ===")
    txn_service.deposit(checking_id, 200)
    txn_service.deposit(savings_id, 300)
    print(account_repo.get_account_by_id(checking_id).view_balance())
    print(account_repo.get_account_by_id(savings_id).view_balance())

    print("\n=== Withdrawal Operation (Savings Account) ===")
    try:
        txn_service.withdraw(savings_id, 900)  # May violate minimum balance.
    except Exception as e:
        print("Withdrawal error:", e)

    print("\n=== Fund Transfer Operation ===")
    try:
        txn_service.transfer(checking_id, savings_id, 150)
    except Exception as e:
        print("Transfer error:", e)

    print("\n=== Final Balances ===")
    print(account_repo.get_account_by_id(checking_id).view_balance())
    print(account_repo.get_account_by_id(savings_id).view_balance())

    print("\n=== Transaction Histories ===")
    print("Checking Account Transactions:")
    print(account_repo.get_account_by_id(checking_id).view_transaction_history())
    print("\nSavings Account Transactions:")
    print(account_repo.get_account_by_id(savings_id).view_transaction_history())

if __name__ == "__main__":
    main()
