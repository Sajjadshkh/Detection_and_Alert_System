import smtplib
from utils.config import SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL

def send_email_alert(subject, message):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = f"Subject: {subject}\n\n{message}"
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, text)
        server.quit()
        print("Email alert sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")