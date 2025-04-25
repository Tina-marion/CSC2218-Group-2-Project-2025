from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.testclient import TestClient
from datetime import datetime
from enum import Enum

# Define the models for the API

class AccountStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"

class Account(BaseModel):
    account_id: str
    account_type: str
    balance: float = 0.0
    status: AccountStatus = AccountStatus.ACTIVE
    creation_date: datetime = datetime.now()

    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        return True

    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.balance >= amount:
            self.balance -= amount
            return True
        return False

    def close_account(self):
        self.status = AccountStatus.CLOSED
        return True

# Create FastAPI app
app = FastAPI()

# In-memory "database"
accounts = {}

@app.post("/create_account/")
def create_account(account: Account):
    if account.account_id in accounts:
        raise HTTPException(status_code=400, detail="Account already exists")
    accounts[account.account_id] = account
    return accounts[account.account_id]

@app.post("/deposit/{account_id}")
def deposit(account_id: str, amount: float):
    account = accounts.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.status == AccountStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Account is closed")
    account.deposit(amount)
    return account

@app.post("/withdraw/{account_id}")
def withdraw(account_id: str, amount: float):
    account = accounts.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.status == AccountStatus.CLOSED:
        raise HTTPException(status_code=400, detail="Account is closed")
    if not account.withdraw(amount):
        raise HTTPException(status_code=400, detail="Insufficient funds")
    return account

@app.post("/close_account/{account_id}")
def close_account(account_id: str):
    account = accounts.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account.close_account()
    return account

@app.get("/account/{account_id}")
def get_account(account_id: str):
    account = accounts.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# Test client
client = TestClient(app)

# Test suite
class TestAccount:
    def setup_method(self):
        """Create test account before each test"""
        self.account_id = "ACC123456"
        self.test_account = {
            "account_id": self.account_id,
            "account_type": "checking",
            "balance": 1000.00
        }
        # Create the account using FastAPI endpoint
        client.post("/create_account/", json=self.test_account)

    def test_account_initialization(self):
        """Test account initialization with correct values"""
        response = client.get(f"/account/{self.account_id}")
        assert response.status_code == 200
        account = response.json()
        assert account["account_id"] == self.account_id
        assert account["account_type"] == "checking"
        assert account["balance"] == 1000.00
        assert account["status"] == "active"

    def test_deposit_positive_amount(self):
        """Test depositing a valid positive amount"""
        response = client.post(f"/deposit/{self.account_id}", json={"amount": 500.00})
        assert response.status_code == 200
        account = response.json()
        assert account["balance"] == 1500.00

    def test_deposit_invalid_amount(self):
        """Test depositing invalid amounts"""
        response = client.post(f"/deposit/{self.account_id}", json={"amount": -100.00})
        assert response.status_code == 400
        assert response.json() == {"detail": "Deposit amount must be positive."}

        response = client.post(f"/deposit/{self.account_id}", json={"amount": 0.00})
        assert response.status_code == 400
        assert response.json() == {"detail": "Deposit amount must be positive."}

    def test_withdraw_sufficient_balance(self):
        """Test successful withdrawal with sufficient balance"""
        response = client.post(f"/withdraw/{self.account_id}", json={"amount": 500.00})
        assert response.status_code == 200
        account = response.json()
        assert account["balance"] == 500.00

    def test_withdraw_insufficient_balance(self):
        """Test withdrawal with insufficient balance"""
        response = client.post(f"/withdraw/{self.account_id}", json={"amount": 1500.00})
        assert response.status_code == 400
        assert response.json() == {"detail": "Insufficient funds"}

    def test_withdraw_invalid_amount(self):
        """Test withdrawing invalid amounts"""
        response = client.post(f"/withdraw/{self.account_id}", json={"amount": -100.00})
        assert response.status_code == 400
        assert response.json() == {"detail": "Withdrawal amount must be positive."}

        response = client.post(f"/withdraw/{self.account_id}", json={"amount": 0.00})
        assert response.status_code == 400
        assert response.json() == {"detail": "Withdrawal amount must be positive."}

    def test_close_account(self):
        """Test account closure"""
        response = client.post(f"/close_account/{self.account_id}")
        assert response.status_code == 200
        account = response.json()
        assert account["status"] == "closed"

        # Verify no transactions allowed on closed account
        response = client.post(f"/deposit/{self.account_id}", json={"amount": 100.00})
        assert response.status_code == 400
        assert response.json() == {"detail": "Account is closed"}

        response = client.post(f"/withdraw/{self.account_id}", json={"amount": 100.00})
        assert response.status_code == 400
        assert response.json() == {"detail": "Account is closed"}

    def test_account_string_representation(self):
        """Test the string representation of the account"""
        response = client.get(f"/account/{self.account_id}")
        account = response.json()
        repr_str = str(account)
        assert self.account_id in repr_str
        assert "checking" in repr_str
        assert "1000.00" in repr_str
        assert "active" in repr_str.lower()

# Run tests (could be run in pytest)
if __name__ == '__main__':
    import pytest # type: ignore
    pytest.main()
