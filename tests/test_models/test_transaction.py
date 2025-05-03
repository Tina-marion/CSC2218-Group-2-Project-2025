from datetime import datetime
from fastapi.testclient import TestClient
from main import app  # Assuming your FastAPI app is in the main.py file
from domain.entities.transaction import Transaction, TransactionType

client = TestClient(app)

def test_transaction_initialization():
    """Test transaction initialization with correct values"""
    transaction_id = "TXN789012"
    account_id = "ACC123456"
    test_timestamp = datetime.now()
    
    # Create a test deposit
    test_deposit = Transaction(
        transaction_id=transaction_id,
        transaction_type=TransactionType.DEPOSIT,
        amount=500.00,
        account_id=account_id,
        timestamp=test_timestamp,
        description="Test deposit"
    )
    
    assert test_deposit.transaction_id == transaction_id
    assert test_deposit.transaction_type == TransactionType.DEPOSIT
    assert test_deposit.amount == 500.00
    assert test_deposit.account_id == account_id
    assert test_deposit.timestamp == test_timestamp
    assert test_deposit.description == "Test deposit"


def test_invalid_amount():
    """Test transaction with invalid amount"""
    with pytest.raises(ValueError):
        Transaction(
            transaction_id="TXN111111",
            transaction_type=TransactionType.DEPOSIT,
            amount=-100.00,
            account_id="ACC123456"
        )


def test_is_debit():
    """Test debit transaction detection"""
    test_withdrawal = Transaction(
        transaction_id="TXN345678",
        transaction_type=TransactionType.WITHDRAWAL,
        amount=200.00,
        account_id="ACC123456"
    )
    
    assert not test_withdrawal.is_debit()  # Adjust this based on logic
    assert test_withdrawal.is_credit()  # Adjust based on logic


def test_auto_timestamp():
    """Test automatic timestamp generation"""
    before_create = datetime.now()
    
    tx = Transaction(
        transaction_id="TXN999999",
        transaction_type=TransactionType.DEPOSIT,
        amount=100.00,
        account_id="ACC123456"
    )
    
    after_create = datetime.now()
    
    assert tx.timestamp >= before_create
    assert tx.timestamp <= after_create


def test_to_from_dict():
    """Test dictionary serialization/deserialization"""
    tx_dict = self.test_deposit.to_dict()  # Assuming this method is implemented
    reconstructed = Transaction.from_dict(tx_dict)  # Assuming this method is implemented
    
    assert reconstructed.transaction_id == self.test_deposit.transaction_id
    assert reconstructed.transaction_type == self.test_deposit.transaction_type
    assert reconstructed.amount == self.test_deposit.amount # type: ignore
    assert reconstructed.timestamp == self.test_deposit.timestamp


def test_string_representation():
    """Test the string representation of transactions"""
    repr_str = str(self.test_deposit)
    assert self.transaction_id in repr_str
    assert "DEPOSIT" in repr_str
    assert "500.00" in repr_str
    assert self.account_id in repr_str # type: ignore
    assert self.test_timestamp.strftime('%Y-%m-%d') in repr_str # type: ignore


if __name__ == '__main__':
    pytest.main() # type: ignore
