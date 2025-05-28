from domain.models.account import Account
from domain.services.account_service import BankAccountService
from datetime import datetime
import json
import os

class LimitEnforcementService:
    def __init__(self, account_service: BankAccountService):
        self.account_service = account_service
        self.limits_file = "transaction_limits.json"
        self.daily_limit = 10000.0  # $10,000 daily limit per account
        self.monthly_limit = 30000.0  # $30,000 monthly limit per account
        self._initialize_limits()

    def _initialize_limits(self):
        """Initialize or load transaction limits from file."""
        if os.path.exists(self.limits_file):
            with open(self.limits_file, 'r') as f:
                self.limits = json.load(f)
        else:
            self.limits = {}
            self._save_limits()

    def _save_limits(self):
        """Save transaction limits to file."""
        with open(self.limits_file, 'w') as f:
            json.dump(self.limits, f, indent=4)

    def check_limit(self, account_id: str, transaction_amount: float) -> bool:
        """Check if the transaction is within daily and monthly limits."""
        account = self.account_service.get_account(account_id)
        if not account:
            return False

        today = datetime.now().date()
        first_of_month = today.replace(day=1)

        # Initialize limits for new accounts
        if account_id not in self.limits:
            self.limits[account_id] = {
                "daily_limit_used": 0.0,
                "daily_reset": today.isoformat(),
                "monthly_limit_used": 0.0,
                "monthly_reset": first_of_month.isoformat()
            }

        limits = self.limits[account_id]
        daily_reset = datetime.fromisoformat(limits["daily_reset"]).date()
        monthly_reset = datetime.fromisoformat(limits["monthly_reset"]).date()

        # Reset daily limit if a new day
        if daily_reset < today:
            limits["daily_limit_used"] = 0.0
            limits["daily_reset"] = today.isoformat()

        # Reset monthly limit if a new month
        if monthly_reset < first_of_month:
            limits["monthly_limit_used"] = 0.0
            limits["monthly_reset"] = first_of_month.isoformat()

        daily_remaining = self.daily_limit - limits["daily_limit_used"]
        monthly_remaining = self.monthly_limit - limits["monthly_limit_used"]

        if transaction_amount <= 0 or transaction_amount > daily_remaining or transaction_amount > monthly_remaining:
            return False

        limits["daily_limit_used"] += transaction_amount
        limits["monthly_limit_used"] += transaction_amount
        self._save_limits()
        return True

    def reset_limits_daily(self):
        """Reset daily limits for all accounts."""
        today = datetime.now().date()
        for account_id in self.limits:
            if datetime.fromisoformat(self.limits[account_id]["daily_reset"]).date() < today:
                self.limits[account_id]["daily_limit_used"] = 0.0
                self.limits[account_id]["daily_reset"] = today.isoformat()
        self._save_limits()

    def reset_monthly_limits(self):
        """Reset monthly limits for all accounts."""
        first_of_month = datetime.now().date().replace(day=1)
        for account_id in self.limits:
            if datetime.fromisoformat(self.limits[account_id]["monthly_reset"]).date() < first_of_month:
                self.limits[account_id]["monthly_limit_used"] = 0.0
                self.limits[account_id]["monthly_reset"] = first_of_month.isoformat()
        self._save_limits()