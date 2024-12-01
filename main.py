import cv2
import numpy as np
import telebot
import time


#telegram config
TELEGRAM_API_TOKEN = '7596351438:AAHUjvthAvvSM8oDc-GGtyh3wJaKK2VTCOU'
CHAT_ID = 160647701

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
bot.send_message(CHAT_ID, "Fire detected in the area!")

last_sent_time = 0


def send_telegram_alert(message):
    global last_sent_time
    current_time = time.time()
    if current_time - last_sent_time > 20: 
        try:
            bot.send_message(CHAT_ID, message)
            last_sent_time = current_time
            print("Alert sent!")
        except Exception as e:
            print(f"Failed to send message: {e}")


def detect_fire(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_bound = np.array([20, 160, 100])  
    upper_bound = np.array([35, 255, 255]) 


    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    mask = cv2.medianBlur(mask, 5)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    fire_detected = False 


    for contour in contours:
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Fire Detected", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            fire_detected = True 

    if fire_detected:
        send_telegram_alert("Fire detected in the area!") 
    return frame

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = detect_fire(frame)

    cv2.imshow("Fire Detection", frame)

    # exit with q key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()















