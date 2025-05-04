from domain.models.transaction import Transaction, TransactionType
import logging

class NotificationService:
    def __init__(self):
        self.logger = logging.getLogger("NotificationService")

    def notify(self, transaction: Transaction) -> None:
        """Send notifications to account owner(s) based on transaction type."""
        source_account_id = transaction.account_id
        related_account = transaction.related_account if transaction.related_account else None

        if transaction.transaction_type == TransactionType.TRANSFER and related_account:
            message = (
                f"Transfer of ${transaction.amount:.2f} completed on {transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"From Account: {source_account_id}\n"
                f"To Account: {related_account}"
            )
            self.logger.info(f"Notification (Transfer): {message}")
            # Extend this to send email/SMS using an API (e.g., SMTP for email, Twilio for SMS)
            print(f"Notification (Transfer): {message}")  # Placeholder for actual notification
        else:
            message = (
                f"{transaction.transaction_type.value.capitalize()} of ${transaction.amount:.2f} completed on "
                f"{transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for Account: {source_account_id}"
            )
            self.logger.info(f"Notification ({transaction.transaction_type.value}): {message}")
            print(f"Notification ({transaction.transaction_type.value}): {message}")  # Placeholder

