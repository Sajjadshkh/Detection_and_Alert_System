import sys, os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

import telebot
import time
from utils.config import TELEGRAM_API_TOKEN, CHAT_ID

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.reply_to(message, "Welcome to Sirang system alert bot")

def send_telegram_alert(message, max_retries=3, delay=5):
    attempt = 0
    while attempt < max_retries:
        try:
            bot.send_message(CHAT_ID, message) 
            print("Telegram alert sent!")
            return  # Exit after sending the telegram successfully
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {e}")
            
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to send telegram message after multiple attempts.")
                return  # Exit after max retries

if __name__ == "__main__":
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"Error in bot.polling: {e}")
            time.sleep(5)  # Wait for 5 seconds before retrying