import logging
from application.services import NotificationSender

class LoggingNotificationSender(NotificationSender):
    """
    Concrete implementation of NotificationSender that simulates sending notifications via console and logging.
    """
    def send(self, message: str) -> None:
        print(message)
        logging.info("Notification sent: %s", message)
