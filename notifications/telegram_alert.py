import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

import telebot
import time
from threading import Lock
from utils.config import TELEGRAM_API_TOKEN, CHAT_ID
from utils.internet_check import is_connected_to_internet
from utils.database import save_telegram, get_pending_telegram, mark_telegram_as_sent
from utils.logger import log_info


bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.reply_to(message, "Welcome to Sirang system alert bot")

def send_telegram_alert(message, max_retries=3, delay=5):
    attempt = 0
    while attempt < max_retries:
        try:
            if is_connected_to_internet():
                bot.send_message(CHAT_ID, message)
                print("Telegram alert sent!")
                return
            else:
                save_telegram(message)
                print("Internet is not connected. Telegram Alert saved to database.")
                return
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to send telegram message after multiple attempts.")
                save_telegram(message)
                return
            

            
def retry_pending_telegram():
    while True:
        if is_connected_to_internet():
            print("Internet is connected. Trying to send pending telegram messages.\n")
            pending_telegram = get_pending_telegram()

            if not pending_telegram:
                print("No pending telegram messages to send.")
            else:
                for alert in pending_telegram:
                    alert_id, message = alert
                    try:
                        send_telegram_alert(message)
                        mark_telegram_as_sent(alert_id)
                        print(f"Telegram message with ID {alert_id} sent successfully.")
                    except Exception as e:
                        print(f"Failed to send pending telegram message ID {alert_id}: {e}")
        else:
            print("Internet is not connected. Waiting for connection...")
        time.sleep(60)


def start_polling():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Error in bot.polling: {e}")
            time.sleep(5)