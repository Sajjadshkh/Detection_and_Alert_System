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
            # ارسال پیام به تلگرام
            bot.send_message(CHAT_ID, message)  # پیام به چت ارسال می‌شود
            print("Telegram alert sent!")
            return  # پس از ارسال موفق پیام، از حلقه خارج می‌شود
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {e}")
            
            if attempt < max_retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to send telegram message after multiple attempts.")
                return  # پس از تلاش‌های متعدد، از حلقه خارج می‌شود

if __name__ == "__main__":
    try:
        bot.polling()
    except Exception as e:
        print(f"Error in bot.polling: {e}")