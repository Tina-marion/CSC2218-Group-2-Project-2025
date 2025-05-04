import smtplib
from email.mime.text import MIMEText
from domain.models.transaction import Transaction, TransactionType
import logging

class NotificationService:
    def __init__(self):
        self.logger = logging.getLogger("NotificationService")
        # SMTP configuration (replace with your email and App Password)
        self.sender_email = "your-email@gmail.com"
        self.app_password = "your-app-password"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def notify(self, transaction: Transaction) -> None:
        """Send email notifications to account owner(s) based on transaction type."""
        source_account_id = transaction.account_id
        related_account = transaction.related_account if transaction.related_account else None
        recipient_email = "recipient-email@example.com"  # Replace with actual account owner email

        if transaction.transaction_type == TransactionType.TRANSFER and related_account:
            message = (
                f"Transfer of ${transaction.amount:.2f} completed on {transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"From Account: {source_account_id}\n"
                f"To Account: {related_account}"
            )
        else:
            message = (
                f"{transaction.transaction_type.value.capitalize()} of ${transaction.amount:.2f} completed on "
                f"{transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for Account: {source_account_id}"
            )

        # Prepare email
        msg = MIMEText(message)
        msg['Subject'] = f"Transaction Notification - {transaction.transaction_type.value}"
        msg['From'] = self.sender_email
        msg['To'] = recipient_email

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)
            self.logger.info(f"Email notification sent for transaction {transaction.transaction_id}")
        except Exception as e:
            self.logger.error(f"Failed to send notification for transaction {transaction.transaction_id}: {str(e)}")
            print(f"Notification failed: {str(e)}")  # Fallback print for debugging