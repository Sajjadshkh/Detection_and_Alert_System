from utils.location import get_dynamic_location
from utils.logger import log_info
from notifications.telegram_alert import send_telegram_alert
from notifications.email_alert import send_email_alert
from notifications.sms_alert import send_sms_alert
from utils.database import (
    save_location,
    save_telegram,
    save_email,
    save_sms,
    get_pending_locations,
    mark_location_as_sent,
)
from utils.internet_check import is_connected_to_internet


def send_alert_with_location(message):
    latitude, longitude = get_dynamic_location()

    if latitude is None or longitude is None:
        log_info("Location data not available. Skipping alert.")
        return

    google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    location_message = f"{message}\nLocation: {google_maps_link}"

    if is_connected_to_internet():
        try:
            send_telegram_alert(location_message)
            send_email_alert("Alert: Fire Detected with Location", location_message)
            send_sms_alert(location_message)
            log_info(f"Alert with location sent: {location_message}")
        except Exception as e:
            log_info(f"Error sending alert with location: {e}")
            save_alert_to_database(location_message, latitude, longitude)
    else:
        log_info("Internet not connected. Saving alert and location to database.")
        save_alert_to_database(location_message, latitude, longitude)


def save_alert_to_database(location_message, latitude, longitude):
    save_telegram(location_message)
    save_email("Alert: Fire Detected with Location", location_message)
    save_sms(location_message)
    save_location(latitude, longitude)


def retry_pending_locations(max_retries=3):
    pending_locations = get_pending_locations()

    for location_id, latitude, longitude in pending_locations:
        google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
        location_message = f"Fire detected!\nLocation: {google_maps_link}"
        attempts = 0

        while attempts < max_retries:
            try:
                send_telegram_alert(location_message)
                send_email_alert("Alert: Fire Detected with Location", location_message)
                send_sms_alert(location_message)
                mark_location_as_sent(location_id)
                log_info(f"Pending location sent successfully: {location_message}")
                break
            except Exception as e:
                attempts += 1
                log_info(f"Error sending pending location (Attempt {attempts}/{max_retries}): {e}")
                if attempts >= max_retries:
                    log_info(f"Failed to send location after {max_retries} attempts. Skipping...")