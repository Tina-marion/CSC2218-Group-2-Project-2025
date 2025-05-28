# infrastructure/notifications/email_notification_service.py
import smtplib
from email.mime.text import MIMEText
from domain.models.transaction import Transaction
import logging

class EmailNotificationService(NotificationServicePort): # type: ignore
    def __init__(self, sender_email: str, sender_password: str, recipient_email: str):
        self.logger = logging.getLogger("EmailNotificationService")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email

    def notify(self, transaction: Transaction) -> None:
        try:
            source_account_id = transaction.account_id
            related_account = getattr(transaction, 'related_account', None)

            if transaction.transaction_type == transaction.TransactionType.TRANSFER and related_account:
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

            self.logger.info(f"Sending notification: {subject} - {message}")

            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, msg.as_string())
                self.logger.info("Notification email sent successfully.")

        except smtplib.SMTPAuthenticationError:
            self.logger.error("Authentication failed. Check email credentials.")
            print("Authentication failed. Check email credentials in email_notification_service.py.")
        except Exception as e:
            self.logger.error(f"Failed to send notification: {str(e)}")
            print(f"Failed to send notification: {str(e)}")
