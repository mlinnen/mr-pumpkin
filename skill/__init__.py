"""
Mr. Pumpkin recording skill — LLM-powered timeline generation and upload.

Public API:
    generate_timeline(prompt, provider=None) -> dict
    upload_timeline(filename, timeline_dict, ...) -> None
    upload_audio(filename, audio_bytes, ...) -> None
"""

from .generator import generate_timeline, LLMProvider, GeminiProvider
from .uploader import upload_timeline, upload_audio

__all__ = [
    "generate_timeline",
    "upload_timeline",
    "upload_audio",
    "LLMProvider",
    "GeminiProvider",
]
