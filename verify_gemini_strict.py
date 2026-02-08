
import requests
import json

KEY = "AIzaSyDqeuZRrvNP1ifm8vZskqQPxjx608EB2YI"
MODEL = "gemini-2.0-flash"

def test_chat():
    print(f"Testing Chat with {MODEL}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": KEY
    }
    payload = {
        "contents": [{"parts": [{"text": "Hello, strict checking."}]}]
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(resp.json()['candidates'][0]['content']['parts'][0]['text'])
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_chat()
