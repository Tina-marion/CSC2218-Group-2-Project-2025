from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from .account import Account, AccountStatus
from .transaction import Transaction, TransactionType

class AccountService:
    """
    Service layer for banking operations with business rules and validation.
    Handles all core banking operations and maintains data integrity.
    """
    
    MINIMUM_BALANCE = Decimal('50.00')  # Minimum balance for checking accounts
    SAVINGS_INTEREST_RATE = Decimal('0.01')  # 1% interest for savings
    
    @staticmethod
    def create_account(account_type: str, initial_balance: Decimal = Decimal('0.00')) -> Tuple[Account, Transaction]:
        """
        Creates a new account with initial deposit transaction.
        
        Args:
            account_type: Type of account ('checking' or 'savings')
            initial_balance: Initial deposit amount
            
        Returns:
            Tuple of (created Account, initial Transaction)
            
        Raises:
            ValueError: If invalid account type or initial balance
        """
        if account_type.lower() not in ('checking', 'savings'):
            raise ValueError("Invalid account type. Must be 'checking' or 'savings'")
            
        if initial_balance < Decimal('0.00'):
            raise ValueError("Initial balance cannot be negative")
            
        account = Account(
            account_id=f"ACCT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            account_type=account_type,
            initial_balance=float(initial_balance)
        )
        
        transaction = Transaction(
            transaction_id=f"TX-INIT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            transaction_type=TransactionType.DEPOSIT,
            amount=float(initial_balance),
            account_id=account.account_id,
            description="Initial deposit"
        )
        
        return account, transaction

    @staticmethod
    def execute_transaction(account: Account, transaction: Transaction) -> bool:
        """
        Executes a transaction with full business rule validation.
        
        Args:
            account: Account to operate on
            transaction: Transaction to execute
            
        Returns:
            bool: True if successful, False if rejected
            
        Raises:
            ValueError: For invalid transactions
        """
        if account.status != AccountStatus.ACTIVE:
            raise ValueError("Cannot transact on closed account")
            
        if transaction.amount <= 0:
            raise ValueError("Transaction amount must be positive")
            
        if transaction.transaction_type == TransactionType.DEPOSIT:
            account.deposit(transaction.amount)
            return True
            
        elif transaction.transaction_type == TransactionType.WITHDRAWAL:
            # Additional business rule: minimum balance requirement
            if account.account_type == "checking" and \
               (account.balance - transaction.amount) < float(AccountService.MINIMUM_BALANCE):
                return False
                
            return account.withdraw(transaction.amount)
            
        else:
            raise ValueError(f"Unsupported transaction type: {transaction.transaction_type}")

    @staticmethod
    def calculate_interest(account: Account) -> Optional[Transaction]:
        """
        Calculates and applies monthly interest for savings accounts.
        
        Args:
            account: The savings account to process
            
        Returns:
            Transaction if interest applied, None otherwise
        """
        if account.account_type != "savings":
            return None
            
        interest_amount = Decimal(str(account.balance)) * AccountService.SAVINGS_INTEREST_RATE / Decimal('12')
        interest_amount = interest_amount.quantize(Decimal('.01'))
        
        if interest_amount > 0:
            transaction = Transaction(
                transaction_id=f"TX-INT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                transaction_type=TransactionType.INTEREST,
                amount=float(interest_amount),
                account_id=account.account_id,
                description="Monthly interest"
            )
            
            account.deposit(transaction.amount)
            return transaction
            
        return None

    @staticmethod
    def transfer_funds(source: Account, target: Account, amount: Decimal) -> Tuple[bool, List[Transaction]]:
        """
        Transfers funds between accounts with full transaction history.
        
        Args:
            source: Source account
            target: Target account
            amount: Amount to transfer
            
        Returns:
            Tuple of (success status, list of transactions created)
        """
        if source.status != AccountStatus.ACTIVE or target.status != AccountStatus.ACTIVE:
            return False, []
            
        if amount <= Decimal('0.00'):
            return False, []
            
        timestamp = datetime.now()
        transactions = []
        
        # Create withdrawal transaction
        withdrawal_tx = Transaction(
            transaction_id=f"TX-TF-OUT-{timestamp.strftime('%Y%m%d%H%M%S')}",
            transaction_type=TransactionType.WITHDRAWAL,
            amount=float(amount),
            account_id=source.account_id,
            description=f"Transfer to {target.account_id}"
        )
        
        # Create deposit transaction
        deposit_tx = Transaction(
            transaction_id=f"TX-TF-IN-{timestamp.strftime('%Y%m%d%H%M%S')}",
            transaction_type=TransactionType.DEPOSIT,
            amount=float(amount),
            account_id=target.account_id,
            description=f"Transfer from {source.account_id}"
        )
        
        # Execute as atomic operation
        success = source.withdraw(withdrawal_tx.amount)
        if success:
            target.deposit(deposit_tx.amount)
            transactions.extend([withdrawal_tx, deposit_tx])
            return True, transactions
            
        return False, transactions

    @staticmethod
    def close_account(account: Account) -> bool:
        """
        Closes an account with business rule validation.
        
        Args:
            account: Account to close
            
        Returns:
            bool: True if successfully closed
        """
        if account.status == AccountStatus.CLOSED:
            return False
            
        # Business rule: Cannot close account with positive balance
        if account.balance > 0:
            return False
            
        account.close_account()
        return True