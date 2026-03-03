"""
Timeline data structure and playback engine for Mr. Pumpkin.

This module provides:
- Timeline: JSON-based command sequence with frame-based timing
- PlaybackState: State tracking for timeline execution
- Playback: Frame-based playback engine integrated with 60 FPS game loop
- RecordingSession: Command capture for creating timelines
- FileManager: File operations for timeline management

Design decisions:
- Frame-based timing at 60 FPS (~16.67ms per frame)
- Millisecond timestamps for sub-second precision
- Flat file naming in ~/.mr-pumpkin/recordings/
- Nested playback support (one timeline can trigger another)
- Invalid commands during playback stop gracefully
"""

import json
import os
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class PlaybackState(Enum):
    """Playback state machine states."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class TimelineEntry:
    """Single command entry in a timeline.
    
    Attributes:
        time_ms: Timestamp in milliseconds from timeline start
        command: Command string (e.g., "set_expression", "blink")
        args: Optional dictionary of command arguments
    """
    
    def __init__(self, time_ms: int, command: str, args: Optional[Dict[str, Any]] = None):
        self.time_ms = time_ms
        self.command = command
        self.args = args or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON encoding."""
        entry = {
            "time_ms": self.time_ms,
            "command": self.command
        }
        if self.args:
            entry["args"] = self.args
        return entry
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimelineEntry':
        """Deserialize from dictionary."""
        return cls(
            time_ms=data["time_ms"],
            command=data["command"],
            args=data.get("args", {})
        )


class Timeline:
    """Timeline representation with command list and metadata.
    
    Attributes:
        version: Format version (for future compatibility)
        commands: List of TimelineEntry objects
        duration_ms: Total duration in milliseconds
    """
    
    def __init__(self, commands: Optional[List[TimelineEntry]] = None, version: str = "1.0"):
        self.version = version
        self.commands = commands or []
        self._update_duration()
    
    def _update_duration(self):
        """Calculate duration from last command timestamp."""
        if self.commands:
            self.duration_ms = max(cmd.time_ms for cmd in self.commands)
        else:
            self.duration_ms = 0
    
    def add_command(self, time_ms: int, command: str, args: Optional[Dict[str, Any]] = None):
        """Add a command to the timeline."""
        entry = TimelineEntry(time_ms, command, args)
        self.commands.append(entry)
        self._update_duration()
    
    def get_duration(self) -> int:
        """Get total timeline duration in milliseconds."""
        return self.duration_ms
    
    def seek(self, position_ms: int) -> List[TimelineEntry]:
        """Get all commands up to specified position.
        
        Args:
            position_ms: Position in timeline (milliseconds)
            
        Returns:
            List of commands at or before position_ms
        """
        return [cmd for cmd in self.commands if cmd.time_ms <= position_ms]
    
    def get_commands_in_range(self, start_ms: int, end_ms: int) -> List[TimelineEntry]:
        """Get commands in a time range.
        
        Args:
            start_ms: Range start (milliseconds)
            end_ms: Range end (milliseconds)
            
        Returns:
            List of commands within range
        """
        return [cmd for cmd in self.commands if start_ms <= cmd.time_ms < end_ms]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize timeline to dictionary for JSON encoding."""
        return {
            "version": self.version,
            "duration_ms": self.duration_ms,
            "commands": [cmd.to_dict() for cmd in self.commands]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Timeline':
        """Deserialize timeline from dictionary.
        
        Raises:
            ValueError: If data structure is invalid
        """
        if "version" not in data:
            raise ValueError("Timeline missing 'version' field")
        if "commands" not in data:
            raise ValueError("Timeline missing 'commands' field")
        
        commands = [TimelineEntry.from_dict(cmd) for cmd in data["commands"]]
        timeline = cls(commands=commands, version=data["version"])
        
        # Validate duration matches
        if "duration_ms" in data and timeline.duration_ms != data["duration_ms"]:
            # Update to match stored duration (may include padding)
            timeline.duration_ms = data["duration_ms"]
        
        return timeline
    
    def save(self, filepath: Path):
        """Save timeline to JSON file.
        
        Args:
            filepath: Path to save file
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: Path) -> 'Timeline':
        """Load timeline from JSON file.
        
        Args:
            filepath: Path to load file
            
        Returns:
            Timeline object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid or structure is wrong
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Timeline file not found: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in timeline file: {e}")
        
        return cls.from_dict(data)


class Playback:
    """Frame-based playback engine for timelines.
    
    Integrates with 60 FPS game loop. Call update(dt) each frame.
    
    Attributes:
        state: Current playback state (STOPPED/PLAYING/PAUSED)
        timeline: Currently loaded timeline
        current_position_ms: Current position in timeline (milliseconds)
        filename: Name of currently loaded file
    """
    
    def __init__(self, recordings_dir: Optional[Path] = None):
        """Initialize playback engine.
        
        Args:
            recordings_dir: Directory for timeline files (default: ~/.mr-pumpkin/recordings)
        """
        if recordings_dir is None:
            home = Path.home()
            self.recordings_dir = home / '.mr-pumpkin' / 'recordings'
        else:
            self.recordings_dir = Path(recordings_dir)
        
        self.state = PlaybackState.STOPPED
        self.timeline: Optional[Timeline] = None
        self.current_position_ms = 0
        self.filename: Optional[str] = None
        self._last_executed_index = -1
        self._command_callback = None
        self._stack: List = []  # Stack for nested playback: list of (timeline, position_ms, last_executed_index, filename)
        self._max_depth = 5  # Prevent infinite nesting
    
    def set_command_callback(self, callback):
        """Set callback function for executing commands.
        
        Args:
            callback: Function that takes (command, args) and executes it
        """
        self._command_callback = callback
    
    def play(self, filename: str):
        """Load and start playing a timeline.
        
        Args:
            filename: Name of timeline file (without .json extension if not included)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If timeline is invalid
        """
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = self.recordings_dir / filename
        self.timeline = Timeline.load(filepath)
        self.filename = filename
        self.current_position_ms = 0
        self._last_executed_index = -1
        self.state = PlaybackState.PLAYING
    
    def stop(self):
        """Stop playback and reset to beginning."""
        self.state = PlaybackState.STOPPED
        self.current_position_ms = 0
        self._last_executed_index = -1
        self._stack.clear()
    
    def pause(self):
        """Pause playback at current position."""
        if self.state == PlaybackState.PLAYING:
            self.state = PlaybackState.PAUSED
    
    def resume(self):
        """Resume playback from paused state."""
        if self.state == PlaybackState.PAUSED:
            self.state = PlaybackState.PLAYING
    
    def seek(self, position_ms: int):
        """Seek to specific position in timeline.
        
        Args:
            position_ms: Target position in milliseconds
        """
        if self.timeline is None:
            return
        
        # Clamp to valid range
        position_ms = max(0, min(position_ms, self.timeline.duration_ms))
        self.current_position_ms = position_ms
        
        # Reset execution tracking for new position
        self._last_executed_index = -1
        for i, cmd in enumerate(self.timeline.commands):
            if cmd.time_ms < position_ms:
                self._last_executed_index = i
    
    def update(self, dt_ms: float) -> List[str]:
        """Update playback state (call every frame).
        
        Args:
            dt_ms: Delta time since last frame in milliseconds
            
        Returns:
            List of error messages from command execution (if any)
        """
        if self.state != PlaybackState.PLAYING or self.timeline is None:
            return []
        
        # Advance position
        self.current_position_ms += dt_ms
        
        # Execute commands in current time window
        errors = []
        for i, cmd in enumerate(self.timeline.commands):
            # Skip already-executed commands
            if i <= self._last_executed_index:
                continue
            
            # Stop if command is in the future
            if cmd.time_ms > self.current_position_ms:
                break
            
            # Handle play_recording command (nested playback)
            if cmd.command == "play_recording":
                filename = cmd.args.get("filename", "")
                if filename and len(self._stack) < self._max_depth:
                    try:
                        # Push current state onto stack
                        self._stack.append((
                            self.timeline,
                            self.current_position_ms,
                            i,  # Mark this command as executed
                            self.filename
                        ))
                        
                        # Load sub-recording
                        if not filename.endswith('.json'):
                            filename = f"{filename}.json"
                        sub_filepath = self.recordings_dir / filename
                        sub_timeline = Timeline.load(sub_filepath)
                        
                        # Switch to sub-recording
                        self.timeline = sub_timeline
                        self.filename = filename
                        self.current_position_ms = 0
                        self._last_executed_index = -1
                        
                        # Break out of loop since we switched timelines
                        break
                    except Exception as e:
                        error_msg = f"Error loading sub-recording '{filename}' at {cmd.time_ms}ms: {e}"
                        errors.append(error_msg)
                        # Don't stop playback, just skip this command
                        self._last_executed_index = i
                elif len(self._stack) >= self._max_depth:
                    error_msg = f"Maximum nesting depth ({self._max_depth}) reached at {cmd.time_ms}ms"
                    errors.append(error_msg)
                    self._last_executed_index = i
                continue
            
            # Execute normal command
            if self._command_callback:
                try:
                    self._command_callback(cmd.command, cmd.args)
                    self._last_executed_index = i
                except Exception as e:
                    error_msg = f"Error executing command '{cmd.command}' at {cmd.time_ms}ms: {e}"
                    errors.append(error_msg)
                    # Invalid command stops playback
                    self.stop()
                    break
        
        # Check if reached end (after executing commands)
        if self.current_position_ms >= self.timeline.duration_ms:
            # Pop back to parent recording if there is one
            if self._stack:
                parent_timeline, parent_position, parent_index, parent_filename = self._stack.pop()
                self.timeline = parent_timeline
                self.current_position_ms = parent_position
                self._last_executed_index = parent_index
                self.filename = parent_filename
            else:
                self.stop()
        
        return errors
    
    def get_status(self) -> Dict[str, Any]:
        """Get current playback status.
        
        Returns:
            Dictionary with state, filename, position, duration, is_playing, stack_depth
        """
        return {
            "state": self.state.value,
            "filename": self.filename,
            "position_ms": self.current_position_ms,
            "duration_ms": self.timeline.duration_ms if self.timeline else 0,
            "is_playing": self.state == PlaybackState.PLAYING,
            "stack_depth": len(self._stack)
        }
    
    def get_duration(self, filename: Optional[str] = None) -> int:
        """Get duration of timeline.
        
        Args:
            filename: File to query (default: current timeline)
            
        Returns:
            Duration in milliseconds
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If timeline is invalid
        """
        if filename is None:
            if self.timeline is None:
                return 0
            return self.timeline.duration_ms
        
        # Load file to get duration
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = self.recordings_dir / filename
        timeline = Timeline.load(filepath)
        return timeline.duration_ms
    
    def list_recordings(self) -> List[Dict[str, Any]]:
        """List all available recordings.
        
        Returns:
            List of dictionaries with filename, size, created_at, duration, command_count
        """
        if not self.recordings_dir.exists():
            return []
        
        recordings = []
        for filepath in self.recordings_dir.glob('*.json'):
            try:
                timeline = Timeline.load(filepath)
                stat = filepath.stat()
                recordings.append({
                    "filename": filepath.name,
                    "size_bytes": stat.st_size,
                    "created_at": stat.st_ctime,
                    "duration_ms": timeline.duration_ms,
                    "command_count": len(timeline.commands)
                })
            except Exception:
                # Skip invalid files
                continue
        
        return recordings
    
    def delete_recording(self, filename: str):
        """Delete a recording file.
        
        Args:
            filename: Name of file to delete
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = self.recordings_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Recording not found: {filename}")
        
        filepath.unlink()
    
    def rename_recording(self, old_name: str, new_name: str):
        """Rename a recording file.
        
        Args:
            old_name: Current filename
            new_name: New filename
            
        Raises:
            FileNotFoundError: If old file doesn't exist
            FileExistsError: If new filename already exists
        """
        if not old_name.endswith('.json'):
            old_name = f"{old_name}.json"
        if not new_name.endswith('.json'):
            new_name = f"{new_name}.json"
        
        old_path = self.recordings_dir / old_name
        new_path = self.recordings_dir / new_name
        
        if not old_path.exists():
            raise FileNotFoundError(f"Recording not found: {old_name}")
        if new_path.exists():
            raise FileExistsError(f"Recording already exists: {new_name}")
        
        old_path.rename(new_path)


class RecordingSession:
    """Recording session for capturing command sequences.
    
    Captures commands with timestamps to create timelines.
    
    Attributes:
        is_recording: Whether recording is active
        commands: List of captured TimelineEntry objects
        start_time: Timestamp when recording started (milliseconds)
    """
    
    def __init__(self, recordings_dir: Optional[Path] = None):
        """Initialize recording session.
        
        Args:
            recordings_dir: Directory for timeline files (default: ~/.mr-pumpkin/recordings)
        """
        if recordings_dir is None:
            home = Path.home()
            self.recordings_dir = home / '.mr-pumpkin' / 'recordings'
        else:
            self.recordings_dir = Path(recordings_dir)
        
        self.is_recording = False
        self.commands: List[TimelineEntry] = []
        self.start_time: Optional[float] = None
    
    def start(self):
        """Begin command capture."""
        self.is_recording = True
        self.commands = []
        self.start_time = time.time() * 1000  # Convert to milliseconds
    
    def stop(self, filename: Optional[str] = None) -> str:
        """Stop recording and save timeline.
        
        Args:
            filename: Name for saved file (auto-generated if None)
            
        Returns:
            Filename of saved recording
            
        Raises:
            ValueError: If no commands were recorded
            FileExistsError: If filename already exists
        """
        if not self.is_recording:
            return ""
        
        self.is_recording = False
        
        if not self.commands:
            raise ValueError("Cannot save recording with no commands")
        
        # Auto-generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"recording_{timestamp}"
        
        # Add .json extension if not present
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = self.recordings_dir / filename
        
        # Check if file exists
        if filepath.exists():
            raise FileExistsError(f"Recording already exists: {filename}")
        
        # Create timeline and save
        timeline = Timeline(commands=self.commands)
        timeline.save(filepath)
        
        return filename
    
    def record_command(self, command: str, args: Optional[Dict[str, Any]] = None):
        """Record a command with current timestamp.
        
        Args:
            command: Command string
            args: Optional command arguments
        """
        if not self.is_recording:
            return
        
        # Calculate time relative to recording start
        current_time = time.time() * 1000  # Convert to milliseconds
        time_ms = int(current_time - self.start_time)
        
        entry = TimelineEntry(time_ms, command, args)
        self.commands.append(entry)
    
    def cancel(self):
        """Cancel recording without saving."""
        self.is_recording = False
        self.commands = []
        self.start_time = None


class FileManager:
    """File operations for timeline management.
    
    Provides download, upload, delete, rename, and list operations.
    """
    
    def __init__(self, recordings_dir: Optional[Path] = None):
        """Initialize file manager.
        
        Args:
            recordings_dir: Directory for timeline files (default: ~/.mr-pumpkin/recordings)
        """
        if recordings_dir is None:
            home = Path.home()
            self.recordings_dir = home / '.mr-pumpkin' / 'recordings'
        else:
            self.recordings_dir = Path(recordings_dir)
    
    def list_recordings(self) -> List[Dict[str, Any]]:
        """List all available recordings.
        
        Returns:
            List of dictionaries with filename, size, created_at, duration, command_count
        """
        if not self.recordings_dir.exists():
            return []
        
        recordings = []
        for filepath in self.recordings_dir.glob('*.json'):
            try:
                timeline = Timeline.load(filepath)
                stat = filepath.stat()
                recordings.append({
                    "filename": filepath.name,
                    "size_bytes": stat.st_size,
                    "created_at": stat.st_ctime,
                    "duration_ms": timeline.duration_ms,
                    "command_count": len(timeline.commands)
                })
            except Exception:
                # Skip invalid files
                continue
        
        return recordings
    
    def download_timeline(self, filename: str) -> str:
        """Download timeline as JSON string.
        
        Args:
            filename: Name of timeline file
            
        Returns:
            JSON string of timeline contents
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid JSON
        """
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = self.recordings_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Recording not found: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            # Validate it's valid JSON
            json.loads(content)
            return content
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in timeline file: {e}")
    
    def upload_timeline(self, filename: str, json_content: str):
        """Upload timeline from JSON string.
        
        Args:
            filename: Name for saved file
            json_content: JSON string containing timeline data
            
        Raises:
            FileExistsError: If filename already exists
            ValueError: If JSON is invalid or structure is wrong
        """
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = self.recordings_dir / filename
        
        # Check if file exists
        if filepath.exists():
            raise FileExistsError(f"Recording already exists: {filename}")
        
        # Validate JSON structure by parsing
        try:
            data = json.loads(json_content)
            timeline = Timeline.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
        except Exception as e:
            raise ValueError(f"Invalid timeline structure: {e}")
        
        # Save to file
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_content)
    
    def delete_timeline(self, filename: str):
        """Delete a timeline file.
        
        Args:
            filename: Name of file to delete
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        filepath = self.recordings_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Recording not found: {filename}")
        
        filepath.unlink()
    
    def rename_timeline(self, old_name: str, new_name: str):
        """Rename a timeline file.
        
        Args:
            old_name: Current filename
            new_name: New filename
            
        Raises:
            FileNotFoundError: If old file doesn't exist
            FileExistsError: If new filename already exists
        """
        if not old_name.endswith('.json'):
            old_name = f"{old_name}.json"
        if not new_name.endswith('.json'):
            new_name = f"{new_name}.json"
        
        old_path = self.recordings_dir / old_name
        new_path = self.recordings_dir / new_name
        
        if not old_path.exists():
            raise FileNotFoundError(f"Recording not found: {old_name}")
        if new_path.exists():
            raise FileExistsError(f"Recording already exists: {new_name}")
        
        old_path.rename(new_path)
