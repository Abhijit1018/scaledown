
import sys
import os
import time
from pulse.config import PulseConfig
from pulse.core.brain import Brain

def test_voice_brain_interaction():
    print("Initializing Brain...")
    try:
        config = PulseConfig.from_env()
        brain = Brain(config)
        print("Brain initialized.")
    except Exception as e:
        print(f"❌ Brain init failed: {e}")
        return

    test_input = "What time is it?"
    print(f"\nSimulating Voice Input: '{test_input}'")
    
    start_t = time.time()
    try:
        response = brain.think(test_input)
        end_t = time.time()
        print(f"✅ Response: {response}")
        print(f"⏱️ Latency: {end_t - start_t:.2f}s")
    except Exception as e:
        print(f"❌ brain.think failed: {e}")

if __name__ == "__main__":
    test_voice_brain_interaction()
