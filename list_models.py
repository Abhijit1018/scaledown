
import requests

KEY = "AIzaSyDqeuZRrvNP1ifm8vZskqQPxjx608EB2YI"

def list_models():
    print(f"Listing models with key: {KEY[:5]}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={KEY}"
    try:
        resp = requests.get(url, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            print(f"Found {len(models)} models.")
            for m in models:
                if 'generateContent' in m['supportedGenerationMethods']:
                    print(f"- {m['name']}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    list_models()
