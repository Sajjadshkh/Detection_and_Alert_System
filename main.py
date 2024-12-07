import cv2
import threading
import time
from threading import Lock
from utils.logger import log_info
from utils.internet_check import is_connected_to_internet
from notifications.telegram_alert import start_polling, retry_pending_telegram
from notifications.email_alert import retry_pending_emails
from notifications.sms_alert import retry_pending_sms
from notifications.location_alert import send_alert_with_location
from utils.database import save_email, save_telegram, save_sms, save_location
from utils.location import get_dynamic_location
from fire_detection.ui import start_ui, rooms, video_sources
from fire_detection.detector import detect_fire


# Initialize variables
ALERT_INTERVAL = 90
alert_lock = Lock()  # Lock for alert sending

# Function to check internet connectivity and send alerts
def send_alerts(message):
    with alert_lock:
        if is_connected_to_internet():
            try:
                send_alert_with_location(message)
                log_info(f"Alert with location sent: {message}")
            except Exception as e:
                log_info(f"Failed to send alert: {e}")
        else:
            log_info("Internet not connected. Saving alert to database.")
            save_telegram(message)
            save_email("Alert: Fire Detected", message)
            save_sms(message)
            latitude, longitude = get_dynamic_location()
            if latitude is not None and longitude is not None:
                save_location(latitude, longitude)
            else:
                log_info("Failed to get dynamic location.")


# Function to process alerts directly without using a queue
def process_alerts_directly(message):
    if message:  # Ensure message is not None or empty
        log_info(f"Processing alert: {message}")
        try:
            send_alerts(message)  # Attempt to send the alert
        except Exception as e:
            log_info(f"Error processing alert: {e}")


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


# Function to simulate a fire detection event
def simulate_fire_detection(room_id):
    try:
        # Convert room_id to an index for video source
        room_index = int(room_id) - 101  # Assume rooms start from 101
        video_source = video_sources[room_index]  # Access video for the specific room

        # Check if video source is valid
        if not video_source:
            log_info(f"No video source found for room {room_id}. No detection performed.")
            return

        # Open the video source
        frame = cv2.VideoCapture(video_source)
        if not frame.isOpened():
            log_info(f"Failed to open video source for room {room_id}.")
            return

        log_info(f"Started fire detection for room {room_id} using video source: {video_source}")

        while True:
            ret, img = frame.read()  # Read the next frame
            if not ret:
                log_info(f"End of video for room {room_id} or failed to read frame.")
                break  # Exit loop if no more frames are available

            # Perform fire detection on the current frame
            fire_detected = False
            try:
                _, fire_detected = detect_fire(img)  # Fire detection logic
            except Exception as e:
                log_info(f"Error in fire detection for room {room_id}: {e}")
                continue  # Skip this frame if there's an error

            if fire_detected:
                room_name = rooms.get(room_id, "Unknown Room")
                message = f"Fire detected in {room_name} (Room {room_id})"
                log_info(f"Fire detected: {message}")
                process_alerts_directly(message)
                break  # Exit loop after sending an alert

            # Add delay to reduce CPU usage if needed
            time.sleep(0.10)
        
        frame.release()  # Release the video source after processing
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


# Start UI and fire detection simulation in separate threads
if __name__ == "__main__":
    # Start fire detection simulation for specific rooms
    fire_detection_thread_101 = start_thread(simulate_fire_detection, args=("101",))
    fire_detection_thread_102 = start_thread(simulate_fire_detection, args=("102",)) 
    fire_detection_thread_103 = start_thread(simulate_fire_detection, args=("103",))
    fire_detection_thread_104 = start_thread(simulate_fire_detection, args=("104",))
    fire_detection_thread_105 = start_thread(simulate_fire_detection, args=("105",))
    fire_detection_thread_106 = start_thread(simulate_fire_detection, args=("106",))

    # Start UI in the main thread
    start_ui_thread()