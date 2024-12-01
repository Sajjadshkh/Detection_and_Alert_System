import cv2
import numpy as np
import telebot
import time
import smtplib

# Telegram config
TELEGRAM_API_TOKEN = '7596351438:AAHUjvthAvvSM8oDc-GGtyh3wJaKK2VTCOU'
CHAT_ID = 160647701

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
last_telegram_sent_time = 0
last_email_sent_time = 0 
fire_detected = False  # Variable to track fire detection status

# Email config
SENDER_EMAIL = 'sajjad.sheykhi.2004@gmail.com'
SENDER_PASSWORD = 'gbtc immn ptyb sluk'
RECIPIENT_EMAIL = 'gta.sajjadsh@gmail.com'

# Time intervals
ALERT_INTERVAL = 60  # 1 minute interval for alerts (60 seconds)


def send_telegram_alert(message):
    global last_telegram_sent_time
    current_time = time.time()
    if current_time - last_telegram_sent_time > ALERT_INTERVAL:  # Check if 1 minute has passed
        try:
            bot.send_message(CHAT_ID, message)
            last_telegram_sent_time = current_time
            print("Telegram alert sent!")
        except Exception as e:
            print(f"Failed to send telegram message: {e}")


def send_email_alert(subject, message):
    global last_email_sent_time
    current_time = time.time()
    if current_time - last_email_sent_time > ALERT_INTERVAL:  # Check if 1 minute has passed
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls() # Use ssl for more secure
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            text = f"Subject: {subject}\n\n{message}"
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, text)
            server.quit()

            last_email_sent_time = current_time
            print("Email alert sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")


def detect_fire(frame):
    global fire_detected
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([20, 160, 100])
    upper_bound = np.array([35, 255, 255])
    
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    mask = cv2.medianBlur(mask, 5)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    fire_detected = False  # Reset fire_detected at the start of each frame check
    for contour in contours:
        if cv2.contourArea(contour) > 550:  # Adjust the threshold as needed
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Fire Detected", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            fire_detected = True  # Set fire_detected to True when fire is detected

    # If fire is detected and the alerts haven't been sent recently
    if fire_detected:
        send_telegram_alert("Fire detected in the area!")
        send_email_alert("Alert: Fire Detected", "Fire detected in the area!")

    return frame


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = detect_fire(frame)
    cv2.imshow("Fire Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()