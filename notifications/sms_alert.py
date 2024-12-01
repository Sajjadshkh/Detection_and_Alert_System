from twilio.rest import Client
from utils.config import TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, RECIPIENT_PHONE_NUMBER

def send_sms_alert(message):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=RECIPIENT_PHONE_NUMBER
        )
        print("SMS alert sent!")
    except Exception as e:
        print(f"Failed to send SMS: {e}")