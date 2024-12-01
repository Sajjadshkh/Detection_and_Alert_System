import cv2
import time
from fire_detection import detect_fire
from notifications import send_telegram_alert, send_email_alert, send_sms_alert
from utils.logger import log_info

fire_detected = False
last_alert_time = 0
ALERT_INTERVAL = 90

# Video Capture
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame, fire_detected = detect_fire(frame)

    if fire_detected and time.time() - last_alert_time > ALERT_INTERVAL:
        send_telegram_alert("Fire detected in the area!")
        send_email_alert("Alert: Fire Detected", "Fire detected in the area!")
        send_sms_alert("Fire detected in the area!")
        last_alert_time = time.time()

        log_info("Fire detected and alerts sent.")

    # Display the frame
    cv2.imshow("Fire Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()