from datetime import date
from domain.models.account import Account


class InterestService:
    def calculate_and_apply_interest(self, account: Account, as_of_date: date = date.today()) -> float:
        interest = account.calculate_interest(as_of_date)
        return float(interest)
