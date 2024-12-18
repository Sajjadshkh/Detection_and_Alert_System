from twilio.rest import Client
import time
from utils.config import TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, RECIPIENT_PHONE_NUMBER
from utils.logger import log_info
from utils.database import save_sms, get_pending_sms, mark_sms_as_sent
from utils.internet_check import is_connected_to_internet

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_sms_alert(message, max_retries=3, delay=5):
    attempt = 0
    while attempt < max_retries:
        try:
            if is_connected_to_internet():
                message_sent = client.messages.create(
                    body=message, 
                    from_=TWILIO_PHONE_NUMBER,
                    to=RECIPIENT_PHONE_NUMBER
                )
                log_info(f"SMS alert sent! SID: {message_sent.sid}")
                return  # Exit after sending the SMS successfully
            else:
                save_sms(message) 
                log_info("Internet not connected. SMS alert saved to database.")
                return
        except Exception as e:
            attempt += 1
            log_info(f"Attempt {attempt} failed: {e}")
            
            if attempt < max_retries:
                log_info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                log_info("Failed to send SMS after multiple attempts.")
                save_sms(message)
                return  # Exit after max retries
            
def retry_pending_sms():
    while True:
        if is_connected_to_internet():
            log_info("Internet is connected. Trying to send pending SMS messages.\n")

            pending_sms = get_pending_sms()

            if not pending_sms:
                log_info("No pending SMS messages to send.")
            else:
                for sms in pending_sms:
                    sms_id, message = sms
                    try:
                        # send_sms_alert(message) 
                        mark_sms_as_sent(sms_id)
                        log_info(f"SMS with ID {sms_id} sent successfully.")
                    except Exception as e:
                        log_info(f"Failed to send pending SMS message ID {sms_id}: {e}")
        else:
            log_info("Internet is not connected. Waiting for connection...")

        time.sleep(60)