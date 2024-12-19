from utils.location import get_location
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
    latitude, longitude = get_location()
    log_info(f"Received location: latitude={latitude}, longitude={longitude}")

    if latitude is None or longitude is None:
        log_info("Location data not available. Skipping alert.")
        return

    google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    combined_message = f"{message}\nLocation: {google_maps_link}"
    combined_message2 = f"latitude={latitude}, longitude={longitude}"

    if is_connected_to_internet():
        try:
            send_telegram_alert(combined_message)
            send_email_alert("Alert: Fire Detected with Location", combined_message)
            send_sms_alert(combined_message2)
            log_info(f"Alert with location sent: {combined_message}")
        except Exception as e:
            log_info(f"Error sending alert with location: {e}")
            save_alert_to_database(message, latitude, longitude)
    else:
        log_info("Internet not connected. Saving alert and location to database.")
        save_alert_to_database(message, latitude, longitude)



def save_alert_to_database(alert_message, latitude, longitude):
    google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
    combined_message = f"{alert_message}\nLocation: {google_maps_link}"

    save_telegram(combined_message)
    save_email("Alert: Fire Detected with Location", combined_message)
    save_sms(combined_message)
    save_location(latitude, longitude)
    log_info(f"Combined alert and location saved to database: {combined_message}")





def retry_pending_locations(max_retries=3):
    pending_locations = get_pending_locations()
    log_info(f"Found {len(pending_locations)} pending locations.")

    for location_id, latitude, longitude in pending_locations:
        if latitude is None or longitude is None:
            log_info(f"Skipping location ID {location_id}: Missing latitude or longitude.")
            continue

        google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
        location_message = f"Fire detected in Bedroom (Room 103)\nLocation: {google_maps_link}"
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
