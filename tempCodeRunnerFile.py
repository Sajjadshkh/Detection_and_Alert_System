import sys
import os
import time
import threading
import cv2
from queue import Queue
from threading import Lock
from fire_detection import detect_fire
from utils.logger import log_info
from utils.internet_check import is_connected_to_internet
from notifications.telegram_alert import start_polling, retry_pending_telegram
from notifications.email_alert import retry_pending_emails
from notifications.sms_alert import retry_pending_sms
from utils.database import create_table, save_email, save_telegram, save_sms, save_location
from notifications.location_alert import send_alert_with_location
from utils.location import get_dynamic_location

# Initialize variables
fire_detected = False
last_alert_time = 0
ALERT_INTERVAL = 90
create_table()

# Initialize the camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video source.\n")
    sys.exit()

# Queue for managing alerts
alert_queue = Queue()

# Lock for alert sending
alert_lock = Lock()

# Function to check internet connectivity and send alerts
def send_alerts(message):
    with alert_lock:
        if is_connected_to_internet():
            try:
                send_alert_with_location(message)
                log_info(f"Alert with location sent: {message}")
            except Exception as e:
                log_info(f"Failed to send alert: {e}\n")
        else:
            log_info("Internet not connected. Saving alert to database.\n")
            save_telegram(message)  # Save telegram message
            save_email("Alert: Fire Detected", message)  # Save email message
            save_sms(message)   # Save sms message
            latitude, longitude = get_dynamic_location()
            if latitude is not None and longitude is not None:
                save_location(latitude, longitude)

# Function to process alerts from the queue
def process_alerts():
    while True:
        message = alert_queue.get()
        try:
            send_alerts(message)
        except Exception as e:
            log_info(f"Error processing alert: {e}\n")
        alert_queue.task_done()

# General thread starting function
def start_thread(target_function, args=None, join_thread=False, retry_interval=5):
    try:
        args = args or ()
        thread = threading.Thread(target=target_function, args=args)
        thread.start()
        if join_thread:
            thread.join()
        return thread
    except Exception as e:
        print(f"Error starting thread for {target_function.__name__}: {e}\n")
        time.sleep(retry_interval)
        return None

# Start background threads
polling_thread = start_thread(start_polling)
retry_thread_email = start_thread(retry_pending_emails)
retry_thread_telegram = start_thread(retry_pending_telegram)
retry_thread_sms = start_thread(retry_pending_sms)

# Start alert processing thread
alert_processor = threading.Thread(target=process_alerts, daemon=True)
alert_processor.start()

# Main fire detection loop
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Exiting...\n")
            break

        # Detect fire in the frame
        frame, fire_detected = detect_fire(frame)

        # Trigger alert if fire is detected and interval has passed
        if fire_detected and time.time() - last_alert_time > ALERT_INTERVAL:
            last_alert_time = time.time()
            alert_queue.put("Fire detected in the area!")

        # Display the frame
        cv2.imshow("Fire Detection", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"Error in main loop: {e}\n")
finally:
    cap.release()
    cv2.destroyAllWindows()