import cv2
import threading
import time
from threading import Lock
from utils.logger import log_info
from utils.internet_check import is_connected_to_internet
from notifications.telegram_alert import start_polling, retry_pending_telegram
from notifications.email_alert import retry_pending_emails
from notifications.sms_alert import retry_pending_sms
from notifications.location_alert import send_alert_with_location, retry_pending_locations
from utils.database import save_email, save_telegram, save_sms, save_location, create_table
from utils.location import get_location
from fire_detection.detector import detect_fire
from ui.startui import start_ui
from ui.config import video_sources, rooms


# Create database tables
create_table()

# Initialize variables
ALERT_INTERVAL = 90 
alert_lock = Lock()  # Lock for alert sending
last_alert_times = {}  # Track the last alert time for each room


# Function to check internet connectivity and send alerts
def send_alerts(room_id, message):
    global last_alert_times
    current_time = time.time()

    with alert_lock:  # Lock for thread safety
        # Initialize the last alert time for the room if not present
        if room_id not in last_alert_times:
            last_alert_times[room_id] = 0

        # Check if ALERT_INTERVAL has passed for this room
        if current_time - last_alert_times[room_id] >= ALERT_INTERVAL:
            if is_connected_to_internet():
                try:
                    send_alert_with_location(message)
                    log_info(f"Alert with location sent for room {room_id}: {message}")
                except Exception as e:
                    log_info(f"Failed to send alert for room {room_id}: {e}")
            else:
                log_info(f"Internet not connected for room {room_id}. Saving alert to database.")
                save_telegram(message)
                save_email(f"Alert: Fire Detected in Room {room_id}", message)
                save_sms(message)
                latitude, longitude = get_location()
                if latitude is not None and longitude is not None:
                    save_location(latitude, longitude)
                else:
                    log_info(f"Failed to get dynamic location for room {room_id}.")

            # Update the last alert time for this room
            last_alert_times[room_id] = current_time
        else:
            remaining_time = ALERT_INTERVAL - (current_time - last_alert_times[room_id])
            log_info(f"Alert skipped for room {room_id}. Next alert in {remaining_time:.2f} seconds.")


# Function to process alerts directly without using a queue
def process_alerts_directly(room_id, message):
    if message:  # Ensure message is not None or empty
        log_info(f"Processing alert for room {room_id}: {message}")
        try:
            send_alerts(room_id, message)  # Attempt to send the alert
        except Exception as e:
            log_info(f"Error processing alert for room {room_id}: {e}")


# General thread starting function
def start_thread(target_function, args=None, join_thread=False, retry_interval=5):
    try:
        args = args or ()
        thread = threading.Thread(target=target_function, args=args)
        thread.daemon = True  # Set daemon so the thread will close when the program exits
        thread.start()
        if join_thread:
            thread.join()
        return thread
    except Exception as e:
        log_info(f"Error starting thread for {target_function.__name__}: {e}")
        time.sleep(retry_interval)
        return None


def simulate_fire_detection(room_id):
    try:
        # Convert room_id to an index for video source
        room_index = int(room_id) - 101  # Assume rooms start from 101
        video_source = video_sources[room_index]  # Access video for the specific room

        if not video_source:
            log_info(f"No video source found for room {room_id}. No detection performed.")
            return

        # Open the video source
        frame = cv2.VideoCapture(video_source)
        if not frame.isOpened():
            log_info(f"Failed to open video source for room {room_id}.")
            return

        log_info(f"Started fire detection for room {room_id} using video source: {video_source}")

        fire_detected_last = False

        while True:
            ret, img = frame.read()
            if not ret:
                log_info(f"End of video for room {room_id} or failed to read frame.")
                break

            fire_detected = False
            try:
                _, fire_detected = detect_fire(img)  # Fire detection logic
            except Exception as e:
                log_info(f"Error in fire detection for room {room_id}: {e}")
                continue

            current_time = time.time()
            last_alert_time = last_alert_times.get(room_id, 0)
            remaining_time = ALERT_INTERVAL - (current_time - last_alert_time)

            if fire_detected:
                room_name = rooms.get(room_id, "Unknown Room")
                message = f"Fire detected in {room_name} (Room {room_id})"

                # Only send alert and log if enough time has passed since the last alert
                if current_time - last_alert_time >= ALERT_INTERVAL:
                    log_info(f"Fire detected: {message}")
                    process_alerts_directly(room_id, message)
                    fire_detected_last = True
                elif fire_detected_last:
                    # If fire was detected previously and not enough time has passed, skip logging
                    pass
            else:
                if fire_detected_last:
                    log_info(f"Fire extinguished in {room_name} (Room {room_id}).")
                fire_detected_last = False  # Reset if fire is not detected

            # Update last alert time after a valid alert is sent
            if current_time - last_alert_time >= ALERT_INTERVAL:
                last_alert_times[room_id] = current_time

            time.sleep(1)  # Delay to reduce CPU usage

        frame.release()
        log_info(f"Finished fire detection for room {room_id}.")
    except Exception as e:
        log_info(f"Error in simulate_fire_detection for room {room_id}: {e}")


# Start UI (ensure this is in the main thread)
def start_ui_thread():
    start_ui()  # This will run in the main thread


# Start background threads for notifications
polling_thread = start_thread(start_polling)
retry_thread_email = start_thread(retry_pending_emails)
retry_thread_telegram = start_thread(retry_pending_telegram)
retry_thread_sms = start_thread(retry_pending_sms)
retry_thread_locations = start_thread(retry_pending_locations)


# Start UI and fire detection simulation in separate threads
if __name__ == "__main__":
    # Start fire detection simulation for specific rooms
    fire_detection_threads = []
    for room_id in ["101", "102", "103", "104", "105", "106"]:
        thread = start_thread(simulate_fire_detection, args=(room_id,))
        fire_detection_threads.append(thread)

    # Start UI in the main thread
    start_ui_thread()