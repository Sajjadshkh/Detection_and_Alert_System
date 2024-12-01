import cv2
import time
import threading
from fire_detection import detect_fire
from notifications import send_telegram_alert, send_email_alert, send_sms_alert
from utils.logger import log_info

fire_detected = False
last_alert_time = 0
ALERT_INTERVAL = 90

# Video Capture
cap = cv2.VideoCapture(0)

# تابع برای ارسال هشدارها
def send_alerts(message):
    send_telegram_alert(message)
    send_email_alert("Alert: Fire Detected", message)
    send_sms_alert(message)
    log_info(f"Alert sent: {message}")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame, fire_detected = detect_fire(frame)

    if fire_detected and time.time() - last_alert_time > ALERT_INTERVAL:
        last_alert_time = time.time()
        # ایجاد ترد برای ارسال هشدار
        alert_thread = threading.Thread(target=send_alerts, args=("Fire detected in the area!",))
        alert_thread.start()

    # نمایش فریم
    cv2.imshow("Fire Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()