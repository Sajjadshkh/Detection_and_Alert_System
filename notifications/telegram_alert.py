import requests

def send_telegram_alert(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Telegram message sent successfully.")
        else:
            print(f"Failed to send message: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")