
import pyttsx3
import threading
import time

def test_tts_main_thread():
    print("Testing TTS in Main Thread...")
    try:
        engine = pyttsx3.init()
        engine.say("This is a test from the main thread.")
        engine.runAndWait()
        print("✅ Main thread TTS passed.")
    except Exception as e:
        print(f"❌ Main thread TTS failed: {e}")

def tts_worker():
    print("Testing TTS in Background Thread...")
    try:
        # Initialize new engine instance for thread safety
        engine = pyttsx3.init()
        engine.say("This is a test from the background thread.")
        engine.runAndWait()
        print("✅ Background thread TTS passed.")
    except Exception as e:
        print(f"❌ Background thread TTS failed: {e}")

def test_tts_threading():
    t = threading.Thread(target=tts_worker)
    t.start()
    t.join()

if __name__ == "__main__":
    test_tts_main_thread()
    print("-" * 20)
    test_tts_threading()
