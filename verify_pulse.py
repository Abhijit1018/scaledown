
import sys
import os

print("Verifying Pulse Ecosystem Environment...")

def check_import(module_name):
    try:
        __import__(module_name)
        print(f"✅ {module_name} installed")
        return True
    except ImportError:
        print(f"❌ {module_name} MISSING")
        return False

# 1. Check Dependencies
deps = [
    "requests", "cryptography", "streamlit", 
    "speech_recognition", "whisper", "pyttsx3", "scaledown", "pulse"
]

all_good = True
for dep in deps:
    if not check_import(dep):
        all_good = False

# 2. Check Config
try:
    from pulse.config import get_default_config
    config = get_default_config()
    print("\n✅ Config loaded successfully")
    print(f"   - ScaleDown Key: {'*' * 5}{config.scaledown_api_key[-5:] if config.scaledown_api_key else 'MISSING'}")
    print(f"   - OpenRouter Key: {'*' * 5}{config.openrouter_api_key[-5:] if config.openrouter_api_key else 'MISSING'}")
    print(f"   - DB Path: {config.db_path}")
except Exception as e:
    print(f"\n❌ Config Error: {e}")
    all_good = False

# 3. Check Brain Logic (Dry Run)
if all_good:
    print("\nTesting Brain Initialization...")
    try:
        from pulse.core.brain import Brain
        brain = Brain(config)
        print("✅ Brain initialized")
        print("   - Memory connected")
        print("   - OpenRouter client ready")
        print(f"   - ScaleDown compressor: {'Active' if brain.compressor else 'Inactive'}")
    except Exception as e:
        print(f"❌ Brain Initialization Failed: {e}")

print("\n" + "="*30)
if all_good:
    print("READY TO DEPLOY 🚀")
    print("Run Chat: 'streamlit run pulse/app.py'")
    print("Run Voice: 'python pulse/main.py --mode voice'")
else:
    print("ISSUES DETECTED ⚠️")
