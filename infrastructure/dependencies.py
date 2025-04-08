# infrastructure/dependencies.py
from typing import Annotated
from fastapi import Depends
from domain.ports.account_repository import AccountRepository
from domain.ports.transaction_repository import TransactionRepository
from infrastructure.repositories.memory.account_repository import MemoryAccountRepository
from infrastructure.repositories.memory.transaction_repository import MemoryTransactionRepository
from infrastructure.config import settings

# Singleton instances
_memory_account_repo = MemoryAccountRepository()
_memory_transaction_repo = MemoryTransactionRepository()

def get_account_repository() -> AccountRepository:
    """Returns the appropriate account repository implementation"""
    if settings.use_memory_repositories:
        return _memory_account_repo
    # Future: Add database repository option
    # elif settings.use_database:
    #     return DatabaseAccountRepository()
    raise NotImplementedError("No repository implementation configured")

def get_transaction_repository() -> TransactionRepository:
    """Returns the appropriate transaction repository implementation"""
    if settings.use_memory_repositories:
        return _memory_transaction_repo
    # Future: Add database repository option
    raise NotImplementedError("No repository implementation configured")