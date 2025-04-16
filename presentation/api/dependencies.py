# api/dependencies.py
from typing import Annotated
from fastapi import Depends
from domain.ports.account_repository import AccountRepository
from domain.ports.transaction_repository import TransactionRepository
from domain.services.account_service import AccountService
from domain.services.transaction_service import TransactionService
from infrastructure.dependencies import (
    get_account_repository,
    get_transaction_repository
)

def get_account_service(
    repo: Annotated[AccountRepository, Depends(get_account_repository)]
) -> AccountService:
    return AccountService(repo)

def get_transaction_service(
    transaction_repo: Annotated[TransactionRepository, Depends(get_transaction_repository)],
    account_repo: Annotated[AccountRepository, Depends(get_account_repository)]
) -> TransactionService:
    return TransactionService(transaction_repo, account_repo)