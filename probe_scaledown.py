
import requests

KEY = "2ZLW63JCLq4d5kWOj2Cxx1Sm6qburOljakHJUoZR"
BASE_URL = "https://api.scaledown.xyz"

def probe(url, method="GET", payload=None):
    headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=5)
        else:
            resp = requests.post(url, headers=headers, json=payload, timeout=5)
        print(f"{method} {url} -> {resp.status_code}")
        if resp.status_code == 200:
             print(resp.json())
        else:
             print(resp.text[:200])
    except Exception as e:
        print(f"Error {url}: {e}")

if __name__ == "__main__":
    print("Probing ScaleDown API for LLM endpoints...")
    probe(f"{BASE_URL}/v1/models")
    
    chat_payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}]
    }
    probe(f"{BASE_URL}/v1/chat/completions", method="POST", payload=chat_payload)
    probe(f"{BASE_URL}/chat/completions", method="POST", payload=chat_payload)
