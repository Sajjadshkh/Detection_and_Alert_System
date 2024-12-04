import sys
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.config import SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL
from utils.database import save_email, get_pending_emails, mark_email_as_sent
from utils.internet_check import is_connected_to_internet
from utils.logger import log_info

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

def send_email_alert(subject, message, max_retries=3, delay=5):
    """
    Send an email alert. Save to database if sending fails.
    """
    attempt = 0
    while attempt < max_retries:
        try:
            if is_connected_to_internet():
                # Setup email message
                msg = MIMEMultipart()
                msg['From'] = SENDER_EMAIL
                msg['To'] = RECIPIENT_EMAIL
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'plain'))

                # Send email
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()  # Secure connection
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
                server.quit()

                log_info(f"Email alert sent successfully: {subject}\n")
                return
            else:
                save_email(subject, message)
                log_info(f"Internet is not connected. Email alert saved to database: {subject}\n")
                return
        except Exception as e:
            attempt += 1
            log_info(f"Attempt {attempt} to send email failed: {e}")
            if attempt < max_retries:
                time.sleep(delay)
            else:
                log_info(f"Failed to send email after {max_retries} attempts. Saving to database.\n")
                save_email(subject, message)
                return

def retry_pending_emails():
    """
    Retry sending pending emails stored in the database.
    """
    while True:
        try:
            if is_connected_to_internet():
                log_info("Internet connected. Checking for pending emails.\n")
                pending_emails = get_pending_emails()

                if not pending_emails:
                    log_info("No pending emails to send.\n")
                else:
                    for email in pending_emails:
                        email_id, subject, body = email
                        try:
                            send_email_alert(subject, body)
                            mark_email_as_sent(email_id)
                            log_info(f"Pending email with ID {email_id} sent successfully.\n")
                        except Exception as e:
                            log_info(f"Failed to send pending email ID {email_id}: {e}\n")
            else:
                log_info("Internet not connected. Waiting to retry pending emails.\n")
        except Exception as e:
            log_info(f"Error in retry_pending_emails: {e}\n")
        time.sleep(60)