# application/statement_service.py
from datetime import datetime
import csv
from typing import List
from domain.models import  Transaction
from domain.account_service import AccountService # type: ignore

class StatementService:
    def __init__(self, account_service: AccountService, transaction_source: str):
        self.account_service = account_service
        self.transaction_source = transaction_source  # filepath or datasource

    def _load_transactions(self, account_id: str, start_date: datetime, end_date: datetime) -> List[Transaction]:
        transactions = []
        try:
            with open(self.transaction_source, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Account ID'] == account_id:
                        trans_date = datetime.strptime(row['Date'], "%Y-%m-%d %H:%M:%S")
                        if start_date <= trans_date <= end_date:
                            transactions.append(Transaction(
                                date=trans_date,
                                type=row['Type'],
                                amount=float(row['Amount']),
                                related_account=row['Related Account'] if row['Related Account'] else "-",
                                balance_after=float(row['Balance After'])
                            ))
        except FileNotFoundError:
            pass
        return transactions

    def generate_statement(self, account_id: str, start_date: datetime, end_date: datetime) -> str:
        account = self.account_service.get_account(account_id)
        if not account:
            raise ValueError("Account not found")

        transactions = self._load_transactions(account_id, start_date, end_date)

        filename = f"statement_{account_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Type', 'Amount ($)', 'Related Account', 'Balance ($)', 'Interest Accrued ($)'])

            total_deposits = 0.0
            total_withdrawals = 0.0
            for idx, trans in enumerate(transactions):
                if trans.type.lower() == "deposit":
                    total_deposits += trans.amount
                elif trans.type.lower() in ("withdraw", "transfer"):
                    total_withdrawals += trans.amount

                interest = f"{account.interest_accrued:.2f}" if idx == len(transactions) - 1 else "0.00"

                writer.writerow([
                    trans.date.strftime("%Y-%m-%d"),
                    trans.type,
                    f"{trans.amount:.2f}",
                    trans.related_account,
                    f"{trans.balance_after:.2f}",
                    interest
                ])

            writer.writerow([])
            writer.writerow(['Summary', '', '', '', '', ''])
            writer.writerow(['Total Deposits', f"{total_deposits:.2f}", '', '', '', ''])
            writer.writerow(['Total Withdrawals/Transfers', f"{total_withdrawals:.2f}", '', '', '', ''])
            writer.writerow(['Ending Balance', f"{account.balance:.2f}", '', '', '', ''])
            writer.writerow(['Total Interest Accrued', f"{account.interest_accrued:.2f}", '', '', '', ''])

        return filename
