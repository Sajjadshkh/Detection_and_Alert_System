from twilio.rest import Client

def send_sms_alert(account_sid, auth_token, from_phone, to_phone, message):
    client = Client(account_sid, auth_token)

    try:
        sms = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        print(f"SMS sent successfully. SID: {sms.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")