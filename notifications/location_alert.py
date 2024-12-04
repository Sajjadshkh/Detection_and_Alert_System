from utils.location import get_dynamic_location
from utils.logger import log_info
from notifications.telegram_alert import send_telegram_alert
from notifications.email_alert import send_email_alert
from notifications.sms_alert import send_sms_alert

def send_location_alert(message):
    latitude, longitude = get_dynamic_location()

    google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

    location_message = f"{message}\nLocation: {google_maps_link}"

    try:
        send_telegram_alert(location_message)
        send_email_alert("Alert: Fire Detected with Location", location_message)
        send_sms_alert(location_message)
        log_info(f"Alert with location sent: {location_message}")
    except Exception as e:
        log_info(f"Error sending alert with location: {e}")