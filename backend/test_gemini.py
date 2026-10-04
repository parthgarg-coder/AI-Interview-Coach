import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", api_key is not None)

url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.8-flash:generateContent"
)

headers = {
    "Content-Type": "application/json",
    "X-goog-api-key": api_key
}

data = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Reply with exactly: Gemini connection working"
                }
            ]
        }
    ]
}

response = requests.post(
    url,
    headers=headers,
    json=data,
    timeout=60
)

print("Status:", response.status_code)
print(response.text)