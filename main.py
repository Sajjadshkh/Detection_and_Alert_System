import sys
import os

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

import cv2
import time
import threading
from threading import Lock
from fire_detection import detect_fire
from notifications import send_telegram_alert, send_email_alert, send_sms_alert
from utils.logger import log_info
from notifications.telegram_alert import start_polling

fire_detected = False
last_alert_time = 0
ALERT_INTERVAL = 90

# Video Capture
cap = cv2.VideoCapture(0)


alert_lock = Lock()

def send_alerts(message):
    with alert_lock:
        send_telegram_alert(message)
        send_email_alert("Alert: Fire Detected", message)
        send_sms_alert(message)
        log_info(f"Alert sent: {message}")

# new thread for run polling
if __name__ == "__main__":
    polling_thread = threading.Thread(target=start_polling)
    polling_thread.start()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame, fire_detected = detect_fire(frame)

    if fire_detected and time.time() - last_alert_time > ALERT_INTERVAL:
        last_alert_time = time.time()
        # use thread
        alert_thread = threading.Thread(target=send_alerts, args=("Fire detected in the area!",))
        alert_thread.start()

    cv2.imshow("Fire Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()