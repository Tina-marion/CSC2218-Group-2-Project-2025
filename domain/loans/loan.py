from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

class LoanStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    PAID = "paid"
    DEFAULTED = "defaulted"

class LoanType(Enum):
    PERSONAL = "personal"
    MORTGAGE = "mortgage"
    AUTO = "auto"

@dataclass
class LoanRepayment:
    due_date: date
    amount_due: Decimal
    principal: Decimal
    interest: Decimal
    paid_amount: Decimal = Decimal("0")
    paid_date: Optional[date] = None

class Loan(ABC):
    def __init__(
        self,
        loan_id: str,
        account_id: str,
        principal: Decimal,
        annual_interest_rate: Decimal,
        term_months: int,
        loan_type: LoanType,
        start_date: date = date.today()
    ):
        self._loan_id = loan_id
        self._account_id = account_id
        self._principal = principal
        self._annual_interest_rate = annual_interest_rate
        self._term_months = term_months
        self._loan_type = loan_type
        self._start_date = start_date
        self._status = LoanStatus.PENDING
        self._repayment_schedule: List[LoanRepayment] = []
        self._generate_repayment_schedule()

    @property
    def loan_id(self) -> str:
        return self._loan_id

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def principal(self) -> Decimal:
        return self._principal

    @property
    def balance(self) -> Decimal:
        return sum(
            repayment.amount_due - repayment.paid_amount
            for repayment in self._repayment_schedule
            if not repayment.paid_date or repayment.due_date > date.today()
        )

    @property
    def status(self) -> LoanStatus:
        return self._status

    def approve(self) -> None:
        if self._status != LoanStatus.PENDING:
            raise ValueError("Only pending loans can be approved")
        self._status = LoanStatus.APPROVED

    def reject(self) -> None:
        if self._status != LoanStatus.PENDING:
            raise ValueError("Only pending loans can be rejected")
        self._status = LoanStatus.REJECTED

    def disburse(self) -> None:
        if self._status != LoanStatus.APPROVED:
            raise ValueError("Only approved loans can be disbursed")
        self._status = LoanStatus.ACTIVE

    def make_payment(self, amount: Decimal, payment_date: date = date.today()) -> None:
        if self._status != LoanStatus.ACTIVE:
            raise ValueError("Only active loans can receive payments")

        remaining_payment = amount
        for repayment in self._repayment_schedule:
            if repayment.paid_date is None and repayment.due_date <= payment_date:
                payment_amount = min(repayment.amount_due - repayment.paid_amount, remaining_payment)
                repayment.paid_amount += payment_amount
                repayment.paid_date = payment_date
                remaining_payment -= payment_amount

                if remaining_payment <= 0:
                    break

        if self._check_fully_paid():
            self._status = LoanStatus.PAID

    def get_repayment_schedule(self) -> List[LoanRepayment]:
        return self._repayment_schedule.copy()

    def _check_fully_paid(self) -> bool:
        return all(
            repayment.paid_amount >= repayment.amount_due
            for repayment in self._repayment_schedule
        )

    @abstractmethod
    def _generate_repayment_schedule(self) -> None:
        pass

class FixedRateLoan(Loan):
    def _generate_repayment_schedule(self) -> None:
        monthly_rate = self._annual_interest_rate / Decimal("12")
        monthly_payment = (self._principal * monthly_rate) / (
            Decimal("1") - (Decimal("1") + monthly_rate) ** -self._term_months
        )

        balance = self._principal
        for month in range(1, self._term_months + 1):
            interest = balance * monthly_rate
            principal = monthly_payment - interest
            balance -= principal

            self._repayment_schedule.append(
                LoanRepayment(
                    due_date=self._start_date + timedelta(days=30 * month),
                    amount_due=monthly_payment,
                    principal=principal,
                    interest=interest
                )
            )

class LoanService:
    def __init__(self):
        self._loans: Dict[str, Loan] = {}

    def apply_for_loan(
        self,
        account_id: str,
        principal: Decimal,
        annual_interest_rate: Decimal,
        term_months: int,
        loan_type: LoanType
    ) -> Loan:
        loan_id = f"LOAN-{len(self._loans) + 1}"
        loan = FixedRateLoan(
            loan_id=loan_id,
            account_id=account_id,
            principal=principal,
            annual_interest_rate=annual_interest_rate,
            term_months=term_months,
            loan_type=loan_type
        )
        self._loans[loan_id] = loan
        return loan

    def get_loan(self, loan_id: str) -> Optional[Loan]:
        return self._loans.get(loan_id)

    def get_account_loans(self, account_id: str) -> List[Loan]:
        return [loan for loan in self._loans.values() if loan.account_id == account_id]