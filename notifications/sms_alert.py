from twilio.rest import Client
import time
from utils.config import TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, RECIPIENT_PHONE_NUMBER

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_sms_alert(message, max_retries=3, delay=5):
    attempt = 0
    while attempt < max_retries:
        try:
            message_sent = client.messages.create(
                body=message, 
                from_=TWILIO_PHONE_NUMBER,
                to=RECIPIENT_PHONE_NUMBER
            )
            print(f"SMS alert sent! SID: {message_sent.sid}")
            return  # Exit after sending the SMS successfully
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {e}")
            
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to send SMS after multiple attempts.")
                return  # Exit after max retries
