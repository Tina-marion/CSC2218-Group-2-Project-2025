# domain/ports/notification_service.py
from abc import ABC, abstractmethod
from domain.models.transaction import Transaction

class NotificationServicePort(ABC):
    @abstractmethod
    def notify(self, transaction: Transaction) -> None:
        """Send notification for a transaction"""
        pass
