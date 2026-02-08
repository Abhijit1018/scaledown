
import requests
import json
import os

from pulse.config import PulseConfig
from pulse.core.openrouter_client import OpenRouterClient

def test_reasoning():
    config = PulseConfig.from_env()
    # Ensure key is loaded (it's hardcoded in config.py now)
    client = OpenRouterClient(
        api_key=config.openrouter_api_key, 
        default_model=config.default_model
    )
    
    print(f"Testing Reasoning with {config.default_model}...")
    
    messages = [
        {"role": "user", "content": "How many r's are in the word 'strawberry'?"}
    ]
    
    try:
        # Pass reasoning param
        result = client.chat(messages, reasoning={"enabled": True})
        
        print(f"Content: {result['content']}")
        print(f"Reasoning Details: {result.get('reasoning_details')}")
        
        if result.get('reasoning_details'):
            print("✅ Reasoning details received!")
        else:
            print("⚠️ No reasoning details found (model might not support it or didn't use it).")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_reasoning()
