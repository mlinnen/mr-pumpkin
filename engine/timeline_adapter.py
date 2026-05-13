"""
engine/timeline_adapter.py
Adapter layer for timeline integration and serialization parity.
Provides thin wrappers around timeline.py Playback/RecordingSession.
"""
from typing import Any
import timeline

def load_timeline(path: str) -> Any:
    return timeline.load_timeline(path)

def save_timeline(obj: Any, path: str) -> None:
    return timeline.save_timeline(obj, path)
