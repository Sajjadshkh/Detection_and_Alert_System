import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.config import SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL
from utils.database import save_email, get_pending_emails, mark_email_as_sent
from utils.internet_check import is_connected_to_internet


def send_email_alert(subject, message, offline=False, max_retries=3, delay=5):
    attempt = 0
    while attempt < max_retries:
        try:
            if is_connected_to_internet():
                msg = MIMEMultipart()
                msg['From'] = SENDER_EMAIL
                msg['To'] = RECIPIENT_EMAIL
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'plain'))

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()  # use tls for more secure
                server.login(SENDER_EMAIL, SENDER_PASSWORD)

                server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
                server.quit()

                print("Email alert sent!")
                return
            else:
                save_email(subject, message)
                print("Internet is not connected. Email Alert saved to database.")
                return
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {e}")

            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to send email after multiple attempts.")
                save_email(subject, message)
                print("Email saved to database for retry.")
                return

def retry_pending_emails():
    while True:
        if is_connected_to_internet():
            print("Internet is connected. Trying to send pending emails.\n")
            pending_emails = get_pending_emails()

            if not pending_emails:
                print("No pending emails to send.")
            else:
                for email in pending_emails:
                    email_id, subject, body = email
                    try:
                        send_email_alert(subject, body)
                        mark_email_as_sent(email_id)
                        print(f"Email with ID {email_id} sent successfully.")
                    except Exception as e:
                        print(f"Failed to send pending email ID {email_id}: {e}")
        else:
            print("Internet is not connected. Waiting for connection...")
        time.sleep(60)