"""
Configuration management for Pulse Ecosystem.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

from pulse.exceptions import ConfigurationError


@dataclass
class PulseConfig:
    """
    Central configuration for Pulse Ecosystem.
    
    All settings can be overridden via environment variables or
    passed directly to the constructor.
    """
    
    # API Keys (Required)
    # API Keys (Required)
    scaledown_api_key: str = ""
    openrouter_api_key: str = "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"
    
    # Model Settings
    default_model: str = "arcee-ai/trinity-large-preview:free"
    fallback_model: str = "google/gemini-2.0-flash-exp:free"
    # List of reliable free models to cycle through
    # This list is ordered by preference
    fallback_models: list = field(default_factory=lambda: [
        "google/gemini-2.0-flash-exp:free",              # Most stable free option
        "google/gemini-2.0-pro-exp-02-05:free",
        "mistralai/mistral-7b-instruct:free",
    ])
    
    # Voice Settings
    tts_engine: str = "system"  # "system" (PowerShell), "pyttsx3", or "elevenlabs"
    stt_engine: str = "whisper"
    wake_words: list = field(default_factory=lambda: ["pulse", "hello", "hey", "hi", "ok pulse"])
    whisper_model_size: str = "base"
    
    # Storage Settings
    db_path: str = field(default_factory=lambda: str(Path.home() / ".pulse" / "pulse_data.db"))
    encryption_key: Optional[str] = None  # Auto-generated if not provided
    
    # ScaleDown Settings
    enable_context_optimization: bool = True
    compression_rate: str = "auto"
    
    # Optional API Keys
    elevenlabs_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "PulseConfig":
        """
        Create configuration from environment variables.
        
        Environment variables:
            SCALEDOWN_API_KEY: ScaleDown API key
            OPENROUTER_API_KEY: OpenRouter API key
            PULSE_DEFAULT_MODEL: Default LLM model
            PULSE_FALLBACK_MODEL: Fallback LLM model
            PULSE_TTS_ENGINE: TTS engine (pyttsx3/elevenlabs)
            PULSE_WAKE_WORD: Wake word for voice activation
            PULSE_DB_PATH: Database file path
            ELEVENLABS_API_KEY: ElevenLabs API key (optional)
        """
        config = cls(
            scaledown_api_key=os.environ.get("SCALEDOWN_API_KEY", ""),
            openrouter_api_key=os.environ.get("OPENROUTER_API_KEY", ""),
            default_model=os.environ.get("PULSE_DEFAULT_MODEL", cls.default_model),
            fallback_model=os.environ.get("PULSE_FALLBACK_MODEL", cls.fallback_model),
            tts_engine=os.environ.get("PULSE_TTS_ENGINE", cls.tts_engine),
            wake_words=os.environ.get("PULSE_WAKE_WORDS", "pulse,hello,hey,hi").split(","),
            db_path=os.environ.get("PULSE_DB_PATH", str(Path.home() / ".pulse" / "pulse_data.db")),
            elevenlabs_api_key=os.environ.get("ELEVENLABS_API_KEY"),
        )
        return config
    
    def validate(self) -> None:
        """Validate that required configuration is present."""
        errors = []
        
        if not self.scaledown_api_key:
            errors.append("SCALEDOWN_API_KEY is required")
        
        if not self.openrouter_api_key:
            errors.append("OPENROUTER_API_KEY is required")
        
        if self.tts_engine == "elevenlabs" and not self.elevenlabs_api_key:
            errors.append("ELEVENLABS_API_KEY is required when using ElevenLabs TTS")
        
        if errors:
            raise ConfigurationError("; ".join(errors))
    
    def ensure_directories(self) -> None:
        """Ensure necessary directories exist."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)


# Convenience function to load config with pre-set API keys
def get_default_config() -> PulseConfig:
    """
    Get default configuration with API keys.
    Falls back to environment variables if not hardcoded.
    """
    config = PulseConfig(
        scaledown_api_key=os.environ.get(
            "SCALEDOWN_API_KEY",
            "2ZLW63JCLq4d5kWOj2Cxx1Sm6qburOljakHJUoZR"
        ),
        openrouter_api_key=os.environ.get(
            "OPENROUTER_API_KEY",
            "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"
        ),
    )
    config.ensure_directories()
    return config
