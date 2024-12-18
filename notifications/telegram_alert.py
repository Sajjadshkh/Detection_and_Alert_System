import sys
import os
import time
from threading import Lock
from telebot import TeleBot
from utils.config import TELEGRAM_API_TOKEN, CHAT_ID
from utils.internet_check import is_connected_to_internet
from utils.database import save_telegram, get_pending_telegram, mark_telegram_as_sent
from utils.logger import log_info

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Initialize bot and lock
bot = TeleBot(TELEGRAM_API_TOKEN)
lock = Lock()

@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.reply_to(message, "Welcome to Sirang system alert bot")

def send_telegram_alert(message, max_retries=3, delay=5):
    """
    Send a Telegram alert with retries. Save to the database if sending fails.
    """
    attempt = 0
    while attempt < max_retries:
        try:
            if is_connected_to_internet():
                bot.send_message(CHAT_ID, message)
                log_info(f"Telegram alert sent successfully: {message}\n")
                return
            else:
                save_telegram(message)
                log_info(f"Internet is not connected. Telegram alert saved to database: {message}\n")
                return
        except Exception as e:
            attempt += 1
            log_info(f"Attempt {attempt} to send Telegram alert failed: {e}\n")
            if attempt < max_retries:
                time.sleep(delay)
            else:
                log_info(f"Failed to send Telegram alert after {max_retries} attempts. Saving to database.\n")
                save_telegram(message)
                return

def retry_pending_telegram():
    """
    Retry sending pending Telegram alerts stored in the database.
    """
    while True:
        try:
            if is_connected_to_internet():
                log_info("Internet connected. Checking for pending Telegram messages.\n")
                pending_telegram = get_pending_telegram()

                if not pending_telegram:
                    log_info("No pending Telegram messages to send.\n")
                else:
                    for alert in pending_telegram:
                        alert_id, message = alert
                        try:
                            # send_telegram_alert(message)
                            mark_telegram_as_sent(alert_id)
                            log_info(f"Pending Telegram message ID {alert_id} sent successfully.\n")
                        except Exception as e:
                            log_info(f"Failed to send pending Telegram message ID {alert_id}: {e}")
            else:
                log_info("Internet not connected. Waiting to retry pending Telegram messages.\n")
        except Exception as e:
            log_info(f"Error in retry_pending_telegram: {e}\n")
        time.sleep(60)

def start_polling():
    """
    Start polling for Telegram bot commands.
    """
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            log_info(f"Error in bot.polling: {e}")
            time.sleep(5)