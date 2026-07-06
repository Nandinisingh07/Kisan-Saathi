import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

if not account_sid or not auth_token:
    print("Error: TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN not set in environment.")
    sys.exit(1)

to_number = "+91XXXXXXXXXX"
from_number = "+17622912153"
url = "https://decaf-brim-steadfast.ngrok-free.dev/ivr/voice"

print(f"Placing outbound call from {from_number} to {to_number} using URL: {url}")

api_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"
payload = {
    "To": to_number,
    "From": from_number,
    "Url": url
}

response = requests.post(api_url, data=payload, auth=(account_sid, auth_token))

if response.status_code == 201:
    print(f"Call placed successfully! Call SID: {response.json().get('sid')}")
else:
    print(f"Failed to place call. Status code: {response.status_code}")
    print(response.text)
