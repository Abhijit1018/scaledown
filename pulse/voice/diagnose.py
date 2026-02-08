"""
Diagnostic script for Pulse Voice Module.
Tests Microphone, STT, and TTS in isolation.
"""

import time
import sys
import pulse.voice.stt as stt_module
import pulse.voice.tts as tts_module

def test_stt():
    print("\n--- Testing Speech-to-Text (STT) ---")
    print("1. Initializing Whisper...")
    try:
        stt = stt_module.WhisperSTT()
        print("✅ Initialization successful")
    except Exception as e:
        print(f"❌ Failed to initialize STT: {e}")
        return False

    print("2. Testing Microphone Input (Speak now!)")
    try:
        text = stt.listen(timeout=5)
        if text:
            print(f"✅ Heard: '{text}'")
            return True
        else:
            print("⚠️ No speech detected. Check microphone settings.")
            return False
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return False

def test_tts():
    print("\n--- Testing Text-to-Speech (TTS) ---")
    print("1. Initializing pyttsx3...")
    try:
        # Re-initialize engine for fresh test
        import pyttsx3
        engine = pyttsx3.init()
        print("✅ Initialization successful")
    except Exception as e:
        print(f"❌ Failed to initialize TTS: {e}")
        return False

    print("2. Speaking test phrase...")
    try:
        engine.say("Testing voice diagnostic sequence.")
        engine.runAndWait()
        print("✅ TTS completed without error (did you hear audio?)")
        return True
    except Exception as e:
        print(f"❌ TTS execution failed: {e}")
        return False

if __name__ == "__main__":
    print("Pulse Voice Diagnostic Tool")
    print("===========================")
    
    stt_ok = test_stt()
    tts_ok = test_tts()
    
    print("\n--- Diagnostic Summary ---")
    print(f"STT (Microphone): {'PASS' if stt_ok else 'FAIL'}")
    print(f"TTS (Speakers):   {'PASS' if tts_ok else 'FAIL'}")
    
    if not stt_ok:
        print("\nFix Suggestion: Check 'Sound Settings' -> 'Input Device' in Windows.")
        print("Ensure 'Python' or 'Terminal' has microphone access.")
    
    if not tts_ok:
        print("\nFix Suggestion: Ensure speakers are not muted.")
