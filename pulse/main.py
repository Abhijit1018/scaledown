"""
Main entry point for Pulse.
"""

import sys
import argparse
from pulse.config import get_default_config
from pulse.core.brain import Brain

def main():
    parser = argparse.ArgumentParser(description="Pulse AI - Personal Assistant")
    parser.add_argument("--mode", choices=["chat", "voice"], default="chat", help="Interaction mode")
    parser.add_argument("--model", type=str, help="Override default LLM model")
    args = parser.parse_args()

    # Load config
    config = get_default_config()
    if args.model:
        config.default_model = args.model

    # Initialize Brain
    try:
        brain = Brain(config)
    except Exception as e:
        print(f"Failed to initialize Pulse: {e}")
        return

    if args.mode == "voice":
        try:
            from pulse.voice.voice_loop import VoiceLoop
            loop = VoiceLoop(brain, config)
            loop.start()
        except ImportError as e:
            print(f"Voice dependencies missing: {e}")
            print("Please install: pip install SpeechRecognition pyaudio pyttsx3 openai-whisper")
        except Exception as e:
            print(f"Voice mode error: {e}")

    else:
        # CLI Chat Mode (Simple fallback if not using Streamlit)
        print(f"Pulse CLI (Model: {config.default_model})")
        print("Type 'exit' to quit.")
        
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() in ("exit", "quit"):
                    break
                
                response = brain.think(user_input)
                print(f"Pulse: {response}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
