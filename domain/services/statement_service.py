from domain.models.account import Account
from domain.services.account_service import BankAccountService
from domain.models.transaction import Transaction
import csv
import os
from datetime import datetime

class StatementService:
    def __init__(self, account_service: BankAccountService):
        self.account_service = account_service

    def generate_statement(self, account_id: str, start_date: datetime, end_date: datetime) -> str:
        """Generate a CSV statement for a period and return the filename."""
        account = self.account_service.get_account(account_id)
        if not account:
            raise ValueError("Account not found")

        transactions = []
        try:
            with open("transactions.csv", mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Account ID'] == account_id:
                        trans_date = datetime.strptime(row['Date'], "%Y-%m-%d %H:%M:%S")
                        if start_date <= trans_date <= end_date:
                            transactions.append({
                                'date': trans_date.strftime("%Y-%m-%d"),
                                'type': row['Type'],
                                'amount': float(row['Amount']),
                                'related_account': row['Related Account'] if row['Related Account'] else "-",
                                'balance': float(row['Balance After'])
                            })
        except FileNotFoundError:
            transactions = []

        # Generate CSV filename
        filename = f"statement_{account_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Type', 'Amount ($)', 'Related Account', 'Balance ($)', 'Interest Accrued ($)'])
            total_deposits = 0.0
            total_withdrawals = 0.0
            for trans in transactions:
                if trans['type'].lower() == "deposit":
                    total_deposits += trans['amount']
                elif trans['type'].lower() in ("withdraw", "transfer"):
                    total_withdrawals += trans['amount']
                writer.writerow([
                    trans['date'],
                    trans['type'],
                    f"{trans['amount']:.2f}",
                    trans['related_account'],
                    f"{trans['balance']:.2f}",
                    f"{account.interest_accrued:.2f}" if trans['date'] == transactions[-1]['date'] else "0.00"
                ])
            # Add summary row
            writer.writerow([])
            writer.writerow(['Summary', '', '', '', '', ''])
            writer.writerow(['Total Deposits', f"{total_deposits:.2f}", '', '', '', ''])
            writer.writerow(['Total Withdrawals/Transfers', f"{total_withdrawals:.2f}", '', '', '', ''])
            writer.writerow(['Ending Balance', f"{account.balance:.2f}", '', '', '', ''])
            writer.writerow(['Total Interest Accrued', f"{account.interest_accrued:.2f}", '', '', '', ''])

        return filename