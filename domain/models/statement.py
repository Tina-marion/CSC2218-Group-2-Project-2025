import csv
from dataclasses import dataclass
from decimal import Decimal
from typing import List
from datetime import date, datetime, timedelta

from domain.entities.account import Account
from domain.entities.transaction import TransactionType

@dataclass
class StatementLineItem:
    date: datetime
    description: str
    amount: Decimal
    balance: Decimal

@dataclass
class MonthlyStatement:
    account_id: str
    account_type: str
    start_date: date
    end_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    interest_earned: Decimal
    transactions: List[StatementLineItem]

class StatementGenerator:
    def generate_statement(self, account: Account, month: int, year: int) -> MonthlyStatement:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        # Calculate interest up to statement date
        account.calculate_interest(end_date)

        # Filter transactions for the statement period
        statement_transactions = [
            tx for tx in account.get_transaction_history()
            if start_date <= tx.timestamp.date() <= end_date
        ]

        # Sort transactions by date
        statement_transactions.sort(key=lambda tx: tx.timestamp)

        # Calculate opening balance (balance before first transaction of the month)
        opening_balance = Decimal(str(account.balance))
        for tx in reversed(statement_transactions):
            if tx.transaction_type == TransactionType.DEPOSIT:
                opening_balance -= Decimal(str(tx.amount))
            elif tx.transaction_type == TransactionType.WITHDRAW:
                opening_balance += Decimal(str(tx.amount))
            elif tx.transaction_type == TransactionType.TRANSFER:
                if tx.account_id == account.account_id:
                    opening_balance += Decimal(str(tx.amount))

        # Generate line items
        line_items = []
        running_balance = opening_balance
        for tx in statement_transactions:
            if tx.transaction_type == TransactionType.DEPOSIT:
                running_balance += Decimal(str(tx.amount))
                desc = "Deposit"
            elif tx.transaction_type == TransactionType.WITHDRAW:
                running_balance -= Decimal(str(tx.amount))
                desc = "Withdrawal"
            elif tx.transaction_type == TransactionType.TRANSFER:
                if tx.account_id == account.account_id:
                    running_balance -= Decimal(str(tx.amount))
                    desc = f"Transfer to {tx.related_account_id}"
                else:
                    running_balance += Decimal(str(tx.amount))
                    desc = f"Transfer from {tx.related_account_id}"

            line_items.append(StatementLineItem(
                date=tx.timestamp,
                description=desc,
                amount=Decimal(str(tx.amount)),
                balance=running_balance
            ))

        return MonthlyStatement(
            account_id=account.account_id,
            account_type=account.account_type.value,
            start_date=start_date,
            end_date=end_date,
            opening_balance=opening_balance,
            closing_balance=Decimal(str(account.balance)),
            interest_earned=account.get_interest_earned(),
            transactions=line_items
        )


class CSVStatementExporter:
       def export(self, statement: MonthlyStatement, filename: str) -> None:
        """Generate a detailed CSV statement"""
        with open(filename, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                "Account ID", "Account Type", 
                "Statement Start Date", "Statement End Date",
                "Opening Balance", "Closing Balance",
                "Interest Earned"
            ])
            
            # Write account summary
            writer.writerow([
                statement.account_id,
                statement.account_type,
                statement.start_date,
                statement.end_date,
                f"{statement.opening_balance:.2f}",
                f"{statement.closing_balance:.2f}",
                f"{statement.interest_earned:.2f}"
            ])
            
            # Write transactions header
            writer.writerow([])
            writer.writerow(["Date", "Description", "Amount", "Balance"])
            
            # Write transactions
            for tx in statement.transactions:
                writer.writerow([
                    tx.date.strftime("%Y-%m-%d"),
                    tx.description,
                    f"{tx.amount:.2f}",
                    f"{tx.balance:.2f}"
                ])
                
            # Add summary footer
            writer.writerow([])
            writer.writerow(["End of Statement"])