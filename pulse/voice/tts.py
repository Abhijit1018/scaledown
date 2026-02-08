"""
Text-to-Speech (TTS) implementation.
"""

from abc import ABC, abstractmethod
from pulse.exceptions import VoiceError, ConfigurationError


class TTSEngine(ABC):
    """Abstract base class for TTS engines."""
    
    @abstractmethod
    def speak(self, text: str, blocking: bool = True):
        """Convert text to speech."""
        pass


class Pyttsx3TTS(TTSEngine):
    """
    Offline TTS using pyttsx3.
    """
    
    def __init__(self, rate: int = 175, voice_id: str = None):
        try:
            import pyttsx3
            # Initialize engine only once? pyttsx3.init() is a factory.
            # But the loop handling is tricky. We'll init per instance but be careful.
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            
            if voice_id:
                self.engine.setProperty('voice', voice_id)
            else:
                # Try to find a good female voice defaults
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if "zira" in voice.name.lower():  # Windows standard female
                        self.engine.setProperty('voice', voice.id)
                        break
                        
        except ImportError:
            raise VoiceError("pyttsx3 is not installed. Run: pip install pyttsx3")

    def speak(self, text: str, blocking: bool = True):
        try:
            self.engine.say(text)
            if blocking:
                self.engine.runAndWait()
            else:
                self.engine.startLoop(False)
                self.engine.iterate()
                self.engine.endLoop()
        except RuntimeError:
            # Handle "run loop already started"
            pass


class ElevenLabsTTS(TTSEngine):
    """
    Cloud-based high-fidelity TTS using ElevenLabs.
    """
    
    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"): # Default "Rachel"
        self.api_key = api_key
        self.voice_id = voice_id
        
        if not api_key:
            raise ConfigurationError("ElevenLabs API key is missing.")

    def speak(self, text: str, blocking: bool = True):
        try:
            import requests
            from pydub import AudioSegment
            from pydub.playback import play
            import io
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
            }
            
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            
            # Play audio
            # pydub requires ffmpeg installed.
            # Alternative: use simpleaudio or playsound if pydub is heavy.
            # For robustness we'll try to just write temp file and play it if pydub fails?
            # Actually let's assume pydub + simpleaudio/ffmpeg
            
            audio_data = io.BytesIO(response.content)
            audio = AudioSegment.from_file(audio_data, format="mp3")
            play(audio)
            
        except ImportError:
             raise VoiceError("pydub/requests not installed. Run: pip install requests pydub")
        except Exception as e:
            print(f"ElevenLabs Error: {e}")


class SystemTTS(TTSEngine):
    """
    Robust Windows TTS using PowerShell (System.Speech).
    Avoids Python threading/COM issues by running in a separate process.
    """
    def speak(self, text: str, blocking: bool = True):
        import subprocess
        
        # Escape quotes for PowerShell
        safe_text = text.replace('"', "'").replace("\n", " ")
        
        # PowerShell command to speak
        ps_command = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\"{safe_text}\")"
        
        try:
            if blocking:
                subprocess.run(["powershell", "-Command", ps_command], check=True)
            else:
                subprocess.Popen(["powershell", "-Command", ps_command])
        except Exception as e:
            print(f"SystemTTS Error: {e}")
