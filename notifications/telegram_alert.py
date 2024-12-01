import telebot
from utils.config import TELEGRAM_API_TOKEN, CHAT_ID

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.reply_to(message, "Welcome to Sirang system alert bot")

def send_telegram_alert(message):
    try:
        bot.send_message(CHAT_ID, message)
        print("Telegram alert sent!")
    except Exception as e:
        print(f"Failed to send telegram message: {e}")

if __name__ == "__main__":
    try:
        bot.polling()
    except Exception as e:
        print(f"Error in bot.polling: {e}")