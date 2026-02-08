"""
Custom exceptions for Pulse Ecosystem.
"""


class PulseError(Exception):
    """Base exception for all Pulse errors."""
    pass


class ConfigurationError(PulseError):
    """Raised when configuration is missing or invalid."""
    pass


class ContextOptimizationError(PulseError):
    """Raised when ScaleDown context optimization fails."""
    pass


class InferenceError(PulseError):
    """Raised when OpenRouter inference fails."""
    pass


class VoiceError(PulseError):
    """Raised when STT/TTS operations fail."""
    pass


class StorageError(PulseError):
    """Raised when database operations fail."""
    pass
