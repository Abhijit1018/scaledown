
import requests

KEY = "2ZLW63JCLq4d5kWOj2Cxx1Sm6qburOljakHJUoZR"

def check_google():
    print(f"Checking Google Gemini with key: {KEY[:5]}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={KEY}"
    payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print("Success!")
            print(resp.json())
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_google()
