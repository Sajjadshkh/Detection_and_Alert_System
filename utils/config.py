import telebot

# Telegram config
TELEGRAM_API_TOKEN = '7596351438:AAHUjvthAvvSM8oDc-GGtyh3wJaKK2VTCOU'
CHAT_ID = 160647701

bot = telebot.TeleBot(TELEGRAM_API_TOKEN)
last_telegram_sent_time = 0
last_email_sent_time = 0 
last_sms_sent_time = 0
fire_detected = False  # Variable to track fire detection status

# Email config
SENDER_EMAIL = 'sajjad.sheykhi.2004@gmail.com'
SENDER_PASSWORD = 'gbtc immn ptyb sluk'
RECIPIENT_EMAIL = 'gta.sajjadsh@gmail.com'

# Twilio config
TWILIO_SID = 'AC057ecf3ca2ca3803de4d69527707d765'
TWILIO_AUTH_TOKEN = '548d21c88a43c78ea563dc9d2884cb13'
TWILIO_PHONE_NUMBER = '+17755469714'
RECIPIENT_PHONE_NUMBER = '+989361249466'

