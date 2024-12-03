import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.config import SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL

def send_email_alert(subject, message, max_retries=3, delay=5):
    attempt = 0
    while attempt < max_retries:
        try:
            # Set up the MIME message
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = RECIPIENT_EMAIL
            msg['Subject'] = subject
            
            # Attach the message body
            msg.attach(MIMEText(message, 'plain'))
            
            # Create the SMTP server connection
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()  # Secure the connection
            
            # Login to the email account
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            # Send the email
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
            server.quit()
            
            print("Email alert sent!")
            return  # Exit after sending the email successfully
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {e}")
            
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to send email after multiple attempts.")
                return  # Exit after max retries
