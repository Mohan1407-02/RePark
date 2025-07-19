import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(account_sid, auth_token)

def send_sms(to_number, message):
    try:
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        print(f"✅ SMS sent to {to_number}: SID {message.sid}")
    except Exception as e:
        print(f"❌ Failed to send SMS: {e}")
