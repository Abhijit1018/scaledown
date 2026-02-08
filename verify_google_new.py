
import requests

KEY = "AIzaSyDqeuZRrvNP1ifm8vZskqQPxjx608EB2YI"

def check_google():
    print(f"Checking Google Gemini with key: {KEY[:5]}...")
    models = ["gemini-1.5-flash", "gemini-1.5-pro-latest"]
    
    for model in models:
        print(f"\nTrying model: {model}")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={KEY}"
        payload = {"contents": [{"parts": [{"text": "Hello, are you working?"}]}]}
        try:
            resp = requests.post(url, json=payload, timeout=10)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                print("Success!")
                print(resp.json()['candidates'][0]['content']['parts'][0]['text'])
                break # Found a working one
            else:
                print(f"Error: {resp.text[:100]}...")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    check_google()
