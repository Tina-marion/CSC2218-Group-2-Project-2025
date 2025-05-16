import smtplib
from email.mime.text import MIMEText
from domain.models.transaction import Transaction, TransactionType
import logging

class NotificationService:
    def __init__(self):
        self.logger = logging.getLogger("NotificationService")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "your.email@gmail.com"  # Replace with your Gmail
        self.sender_password = "your-app-password"  # Replace with your App Password
        self.recipient_email = "recipient.email@example.com"  # Replace with recipient email

    def notify(self, transaction: Transaction) -> None:
        """Send email notifications to account owner(s) based on transaction type."""
        try:
            source_account_id = transaction.account_id
            related_account = transaction.related_account if transaction.related_account else None

            if transaction.transaction_type == TransactionType.TRANSFER and related_account:
                message = (
                    f"Transfer of ${transaction.amount:.2f} completed on {transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"From Account: {source_account_id}\n"
                    f"To Account: {related_account}"
                )
                subject = "ZenBank Transfer Notification"
            else:
                message = (
                    f"{transaction.transaction_type.value.capitalize()} of ${transaction.amount:.2f} completed on "
                    f"{transaction.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for Account: {source_account_id}"
                )
                subject = f"ZenBank {transaction.transaction_type.value.capitalize()} Notification"

            # Log the notification
            self.logger.info(f"Sending notification: {subject} - {message}")

            # Prepare email
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email

            # Send email using smtplib
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, msg.as_string())
                self.logger.info("Notification email sent successfully.")

        except smtplib.SMTPAuthenticationError:
            self.logger.error("Authentication failed. Check email credentials.")
            print("Authentication failed. Check email credentials in notification_service.py.")
        except Exception as e:
            self.logger.error(f"Failed to send notification: {str(e)}")
            print(f"Failed to send notification: {str(e)}")