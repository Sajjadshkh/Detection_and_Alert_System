import telebot
from utils.config import TELEGRAM_API_TOKEN, CHAT_ID

def send_telegram_alert(message):
    bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
    try:
        bot.send_message(CHAT_ID, message)
        print("Telegram alert sent!")
    except Exception as e:
        print(f"Failed to send telegram message: {e}")