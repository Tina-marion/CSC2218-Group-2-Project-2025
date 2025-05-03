# Notification interfaces
from abc import ABC, abstractmethod
from ast import Dict
from typing import List


class Notification(ABC):
    @abstractmethod
    def send(self, message: str, recipient: str) -> bool:
        pass

class EmailNotification(Notification):
    def send(self, message: str, recipient: str) -> bool:
        # In a real implementation, this would send an actual email
        print(f"Email to {recipient}: {message}")
        return True

class SMSNotification(Notification):
    def send(self, message: str, recipient: str) -> bool:
        # In a real implementation, this would send an actual SMS
        print(f"SMS to {recipient}: {message}")
        return True

# Notification service using Observer pattern
class NotificationService:
    def __init__(self):
        self._subscribers: Dict[str, List[Notification]] = {}

    def subscribe(self, account_id: str, notification: Notification) -> None:
        if account_id not in self._subscribers:
            self._subscribers[account_id] = []
        self._subscribers[account_id].append(notification)

    def unsubscribe(self, account_id: str, notification: Notification) -> None:
        if account_id in self._subscribers:
            self._subscribers[account_id] = [
                n for n in self._subscribers[account_id] if n != notification
            ]

    def notify(self, account_id: str, message: str) -> None:
        if account_id in self._subscribers:
            for notification in self._subscribers[account_id]:
                notification.send(message, account_id)