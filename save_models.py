
import requests

KEY = "AIzaSyDqeuZRrvNP1ifm8vZskqQPxjx608EB2YI"

def list_and_save():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={KEY}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            with open("clean_models.txt", "w") as f:
                for m in models:
                    if 'generateContent' in m['supportedGenerationMethods']:
                        f.write(m['name'] + "\n")
            print(f"Saved {len(models)} models to clean_models.txt")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    list_and_save()
