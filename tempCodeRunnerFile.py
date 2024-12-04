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
from notifications import send_telegram_alert, send_email_alert, send_sms_alert
from notifications.telegram_alert import start_polling
from notifications.telegram_alert import retry_pending_telegram
from notifications.email_alert import retry_pending_emails
from utils.database import create_table, save_email, save_telegram

# Initialize variables
fire_detected = False
last_alert_time = 0
ALERT_INTERVAL = 90
create_table()

# Initialize the camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video source.")
    sys.exit()

# Queue for managing alerts
alert_queue = Queue()

# Lock for alert sending
alert_lock = Lock()

def send_alerts(message):
    with alert_lock:
        if is_connected_to_internet():
            try:
                send_telegram_alert(message)
                send_email_alert("Alert: Fire Detected", message)
                send_sms_alert(message)
                log_info(f"Alert sent: {message}")
            except Exception as e:
                log_info(f"Failed to send alert: {e}")
        else:
            log_info("Internet not connected. Saving alert to database.")
            save_telegram(message)  # Save telegram message
            save_email("Alert: Fire Detected", message)  # Save email message

def process_alerts():
    while True:
        message = alert_queue.get()
        try:
            send_alerts(message)
        except Exception as e:
            log_info(f"Error processing alert: {e}")
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
        print(f"Error starting thread for {target_function.__name__}: {e}")
        time.sleep(retry_interval)
        return None

# Start background threads
polling_thread = start_thread(start_polling)
retry_thread_email = start_thread(retry_pending_emails)
retry_thread_telegram = start_thread(retry_pending_telegram)

# Start alert processing thread
alert_processor = threading.Thread(target=process_alerts, daemon=True)
alert_processor.start()

# Main fire detection loop
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Exiting...")
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
    print(f"Error in main loop: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()