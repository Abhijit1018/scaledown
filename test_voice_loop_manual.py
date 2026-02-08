
import sys
import os
import time
from pulse.config import PulseConfig
from pulse.core.brain import Brain
from pulse.voice.voice_loop import VoiceLoop

def test_manual_voice_loop():
    print("Initializing Config & Brain...")
    config = PulseConfig.from_env()
    brain = Brain(config)
    
    print("Initializing Voice Loop...")
    voice_loop = VoiceLoop(brain, config)
    
    print("\n--- STARTING VOICE LOOP (Manual Test) ---")
    print("Speak 'Pulse' or 'Hello' to wake it up.")
    print("Press Ctrl+C to stop.")
    
    # We call _run_loop directly to block main thread
    voice_loop._run_loop()

if __name__ == "__main__":
    test_manual_voice_loop()
