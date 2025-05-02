from abc import ABC, abstractmethod


class NotificationSender(ABC):
    """Interface for sending notifications"""
    
    @abstractmethod
    def send_email(self, recipient: str, subject: str, body: str) -> None:
        """Send an email notification"""
        pass
    
    @abstractmethod
    def send_sms(self, phone_number: str, message: str) -> None:
        """Send an SMS notification"""
        pass
