
import os
import requests
import scaledown
import inspect

KEY = "2ZLW63JCLq4d5kWOj2Cxx1Sm6qburOljakHJUoZR"

def check_openrouter():
    print("Checking OpenRouter...")
    headers = {"Authorization": f"Bearer {KEY}"}
    resp = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers)
    print(f"OpenRouter Auth Check: {resp.status_code} - {resp.text}")

def check_google():
    print("\nChecking Google Gemini...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={KEY}"
    payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
    resp = requests.post(url, json=payload)
    print(f"Google Gemini Check: {resp.status_code}")
    if resp.status_code != 200:
        print(resp.text[:200])

def inspect_scaledown():
    print("\nInspecting ScaleDown...")
    print(f"ScaleDown Version: {getattr(scaledown, '__version__', 'unknown')}")
    print(f"Contents: {dir(scaledown)}")
    
    # Check Pipeline for generation
    if hasattr(scaledown, 'Pipeline'):
        print(f"Pipeline methods: {dir(scaledown.Pipeline)}")

    # Check Compressor
    if hasattr(scaledown, 'ScaleDownCompressor'):
        print(f"Compressor methods: {dir(scaledown.ScaleDownCompressor)}")

if __name__ == "__main__":
    check_openrouter()
    check_google()
    inspect_scaledown()
