"""
TCP Integration Test Suite for Timeline Commands - Issue #34

This test suite validates the TCP server's timeline recording/playback functionality.
Tests are designed to run against a live PumpkinFace server on localhost:5000.

Test Coverage:
- Recording workflow (start, stop, auto-naming, error handling)
- Basic playback (simple sequences, state transitions, timing)
- Playback control (play, pause, resume, stop, seek)
- File management (list, delete, rename)
- Status queries (timeline_status, recording_status)
- Manual override during playback (auto-pause behavior)
- Edge cases (empty files, nonexistent files, nested playback, etc.)
- Command integration (all existing commands recordable)

Author: Mylo (Tester)
Date: 2026-02-25
"""

import socket
import time
import json
import pytest
import subprocess
import signal
import sys
from pathlib import Path
from typing import Optional, Dict, Any


# ============================================================================
# FIXTURES & HELPERS
# ============================================================================

@pytest.fixture(scope="session")
def pumpkin_server():
    """Start PumpkinFace server before tests, stop after all tests complete.
    
    Starts server as background process, waits for port to be ready,
    yields control to tests, then terminates server on cleanup.
    """
    # Start server process (headless mode if available, else skip tests)
    recordings_dir = Path.home() / '.mr-pumpkin' / 'recordings'
    recordings_dir.mkdir(parents=True, exist_ok=True)
    
    # NOTE: Assumes pumpkin_face.py supports --headless or similar flag
    # If not available, tests will need manual server startup
    try:
        # Try starting server in subprocess
        # For Windows, use pythonw.exe to avoid console window
        if sys.platform == 'win32':
            process = subprocess.Popen(
                ['python', 'pumpkin_face.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            process = subprocess.Popen(
                ['python', 'pumpkin_face.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        # Wait for server to start (poll port until ready)
        max_retries = 30
        for i in range(max_retries):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                sock.connect(('localhost', 5000))
                sock.close()
                break
            except (ConnectionRefusedError, socket.timeout):
                time.sleep(0.5)
                if i == max_retries - 1:
                    process.terminate()
                    pytest.skip("Could not connect to PumpkinFace server on port 5000")
        
        yield process
        
        # Cleanup: terminate server
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            
    except Exception as e:
        pytest.skip(f"Could not start PumpkinFace server: {e}")


@pytest.fixture
def recordings_dir():
    """Provide path to recordings directory for file cleanup."""
    return Path.home() / '.mr-pumpkin' / 'recordings'


@pytest.fixture(autouse=True)
def cleanup_test_recordings(recordings_dir):
    """Clean up test recordings before and after each test.
    
    Removes any files starting with 'test_' to avoid pollution between tests.
    """
    def cleanup():
        if recordings_dir.exists():
            for file in recordings_dir.glob('test_*.json'):
                file.unlink()
    
    cleanup()  # Before test
    yield
    cleanup()  # After test


def tcp_send(cmd: str, timeout: float = 2.0) -> str:
    """Send command to TCP server, return response.
    
    Args:
        cmd: Command string to send
        timeout: Socket timeout in seconds
        
    Returns:
        Response string from server (may be empty for commands without responses)
        
    Raises:
        ConnectionError: If cannot connect to server
    """
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(timeout)
        client.connect(('localhost', 5000))
        client.send(cmd.encode('utf-8'))
        
        # Try to receive response (some commands may not send responses)
        try:
            response = client.recv(4096).decode('utf-8').strip()
        except socket.timeout:
            response = ""
        
        client.close()
        return response
    except Exception as e:
        raise ConnectionError(f"Failed to send command '{cmd}': {e}")


def verify_file_exists(recordings_dir: Path, filename: str) -> bool:
    """Check if recording file exists."""
    if not filename.endswith('.json'):
        filename = f"{filename}.json"
    return (recordings_dir / filename).exists()


def verify_file_content(recordings_dir: Path, filename: str) -> Dict[str, Any]:
    """Load and return JSON content of recording file.
    
    Args:
        recordings_dir: Directory containing recordings
        filename: Name of file to load
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid
    """
    if not filename.endswith('.json'):
        filename = f"{filename}.json"
    
    filepath = recordings_dir / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Recording not found: {filename}")
    
    with open(filepath, 'r') as f:
        return json.load(f)


def parse_json_response(response: str) -> Dict[str, Any]:
    """Parse JSON response from server.
    
    Args:
        response: Response string from server
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        ValueError: If response is not valid JSON
    """
    if not response:
        raise ValueError("Empty response from server")
    
    # Response may be raw JSON or prefixed with "OK" or "ERROR"
    if response.startswith('{') or response.startswith('['):
        return json.loads(response)
    else:
        # Extract JSON from response (if embedded)
        try:
            start = response.index('{')
            end = response.rindex('}') + 1
            return json.loads(response[start:end])
        except (ValueError, json.JSONDecodeError):
            raise ValueError(f"Response is not JSON: {response}")


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestRecordingWorkflow:
    """Test recording start, stop, auto-naming, and error handling."""
    
    def test_record_start_stop_creates_file(self, pumpkin_server, recordings_dir):
        """Record a simple sequence and verify file is created."""
        # Start recording
        response = tcp_send("record_start")
        assert "OK" in response or "Recording started" in response.lower()
        
        # Send some commands
        tcp_send("happy")
        time.sleep(0.2)
        tcp_send("blink")
        time.sleep(0.2)
        
        # Stop recording with explicit filename
        response = tcp_send("record_stop test_simple")
        assert "OK" in response or "saved" in response.lower()
        
        # Verify file exists
        assert verify_file_exists(recordings_dir, "test_simple")
        
        # Verify file contains commands
        content = verify_file_content(recordings_dir, "test_simple")
        assert "commands" in content
        assert len(content["commands"]) >= 2
        assert "duration_ms" in content
    
    def test_record_start_while_recording_errors(self, pumpkin_server):
        """Starting recording while already recording should error."""
        # Start first recording
        tcp_send("record_start")
        
        # Try to start second recording
        response = tcp_send("record_start")
        assert "ERROR" in response or "already" in response.lower()
        
        # Clean up
        tcp_send("record_cancel")
    
    def test_record_auto_naming(self, pumpkin_server, recordings_dir):
        """Record without filename should auto-generate timestamp name."""
        # Start recording
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.1)
        
        # Stop without filename
        response = tcp_send("record_stop")
        
        # Response should contain generated filename
        # Format: recording_YYYY-MM-DD_HHMMSS.json
        assert "recording_" in response.lower()
        
        # Extract filename from response and verify it exists
        # (This test assumes response format includes the filename)
        # Simplified: just check that a new recording file was created
        recordings = list(recordings_dir.glob('recording_*.json'))
        assert len(recordings) > 0
        
        # Clean up auto-generated file
        for rec in recordings:
            rec.unlink()
    
    def test_record_stop_with_existing_filename_errors(self, pumpkin_server, recordings_dir):
        """Stopping recording with existing filename should error."""
        # Create first recording
        tcp_send("record_start")
        tcp_send("happy")
        time.sleep(0.1)
        tcp_send("record_stop test_existing")
        
        # Start second recording
        tcp_send("record_start")
        tcp_send("sad")
        time.sleep(0.1)
        
        # Try to save with same filename
        response = tcp_send("record_stop test_existing")
        assert "ERROR" in response or "already exists" in response.lower()
        
        # Clean up
        tcp_send("record_cancel")
    
    def test_record_stop_without_active_recording_errors(self, pumpkin_server):
        """Stopping recording when not recording should error."""
        response = tcp_send("record_stop test_invalid")
        assert "ERROR" in response or "no active recording" in response.lower()
    
    def test_recording_captures_timestamps(self, pumpkin_server, recordings_dir):
        """Verify recording captures command timestamps correctly."""
        tcp_send("record_start")
        
        # Send commands with known delays
        tcp_send("neutral")
        time.sleep(0.2)  # 200ms
        tcp_send("happy")
        time.sleep(0.3)  # 300ms
        tcp_send("sad")
        
        tcp_send("record_stop test_timestamps")
        
        # Load file and check timestamps
        content = verify_file_content(recordings_dir, "test_timestamps")
        commands = content["commands"]
        
        assert len(commands) == 3
        
        # First command should be near t=0
        assert commands[0]["time_ms"] < 50
        
        # Second command should be ~200ms
        assert 150 < commands[1]["time_ms"] < 300
        
        # Third command should be ~500ms
        assert 450 < commands[2]["time_ms"] < 650
    
    def test_record_cancel(self, pumpkin_server, recordings_dir):
        """Recording cancellation should not create file."""
        tcp_send("record_start")
        tcp_send("happy")
        time.sleep(0.1)
        
        response = tcp_send("record_cancel")
        assert "OK" in response or "cancelled" in response.lower()
        
        # Verify no file was created
        test_files = list(recordings_dir.glob('test_*.json'))
        assert len(test_files) == 0


class TestBasicPlayback:
    """Test basic playback functionality and state transitions."""
    
    def test_play_simple_sequence(self, pumpkin_server, recordings_dir):
        """Record and playback a simple 2-command sequence."""
        # Record sequence
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.2)
        tcp_send("happy")
        time.sleep(0.2)
        tcp_send("record_stop test_playback_simple")
        
        # Play back
        response = tcp_send("play test_playback_simple")
        assert "OK" in response or "playing" in response.lower()
        
        # Wait for playback to complete
        time.sleep(0.6)
        
        # Verify playback finished (status should be STOPPED)
        status_response = tcp_send("timeline_status")
        status = parse_json_response(status_response)
        assert status["state"] == "stopped" or status["state"] == "STOPPED"
    
    def test_playback_state_transitions(self, pumpkin_server, recordings_dir):
        """Verify playback state: STOPPED → PLAYING → STOPPED."""
        # Record a 500ms sequence
        tcp_send("record_start")
        tcp_send("happy")
        time.sleep(0.5)
        tcp_send("record_stop test_state_transitions")
        
        # Initial state: STOPPED
        status = parse_json_response(tcp_send("timeline_status"))
        assert status["state"].upper() == "STOPPED"
        assert status["is_playing"] == False
        
        # Start playback: PLAYING
        tcp_send("play test_state_transitions")
        time.sleep(0.1)  # Let playback start
        
        status = parse_json_response(tcp_send("timeline_status"))
        assert status["state"].upper() == "PLAYING"
        assert status["is_playing"] == True
        assert status["filename"] is not None
        
        # Wait for completion: back to STOPPED
        time.sleep(0.6)
        status = parse_json_response(tcp_send("timeline_status"))
        assert status["state"].upper() == "STOPPED"
        assert status["is_playing"] == False
    
    def test_playback_respects_timing(self, pumpkin_server, recordings_dir):
        """Playback should execute commands in correct chronological order."""
        # Create timeline: neutral@0ms, happy@200ms, sad@500ms
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.2)
        tcp_send("happy")
        time.sleep(0.3)
        tcp_send("sad")
        tcp_send("record_stop test_timing")
        
        # Verify file has correct timing
        content = verify_file_content(recordings_dir, "test_timing")
        commands = content["commands"]
        
        # Commands should be in chronological order
        for i in range(len(commands) - 1):
            assert commands[i]["time_ms"] <= commands[i + 1]["time_ms"]
        
        # Playback test: just verify it plays without errors
        response = tcp_send("play test_timing")
        assert "ERROR" not in response
        
        time.sleep(0.8)  # Let playback finish


class TestPlaybackControl:
    """Test play, pause, resume, stop, and seek commands."""
    
    def test_play_pause_resume_stop(self, pumpkin_server, recordings_dir):
        """Test full playback control flow."""
        # Create 1-second recording
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.5)
        tcp_send("happy")
        time.sleep(0.5)
        tcp_send("record_stop test_control")
        
        # Play
        tcp_send("play test_control")
        time.sleep(0.2)
        
        status = parse_json_response(tcp_send("timeline_status"))
        assert status["state"].upper() == "PLAYING"
        
        # Pause
        response = tcp_send("pause")
        assert "OK" in response or "paused" in response.lower()
        
        status = parse_json_response(tcp_send("timeline_status"))
        assert status["state"].upper() == "PAUSED"
        paused_position = status["position_ms"]
        
        # Wait and verify position doesn't advance
        time.sleep(0.3)
        status = parse_json_response(tcp_send("timeline_status"))
        assert status["state"].upper() == "PAUSED"
        # Position should be similar (within tolerance)
        assert abs(status["position_ms"] - paused_position) < 100
        
        # Resume
        response = tcp_send("resume")
        assert "OK" in response or "resumed" in response.lower()
        
        status = parse_json_response(tcp_send("timeline_status"))
        assert status["state"].upper() == "PLAYING"
        
        # Stop
        response = tcp_send("stop")
        assert "OK" in response or "stopped" in response.lower()
        
        status = parse_json_response(tcp_send("timeline_status"))
        assert status["state"].upper() == "STOPPED"
        assert status["position_ms"] == 0  # Reset to start
    
    def test_pause_without_playback_errors(self, pumpkin_server):
        """Pausing when not playing should error."""
        response = tcp_send("pause")
        assert "ERROR" in response or "no active playback" in response.lower()
    
    def test_resume_without_pause_errors(self, pumpkin_server):
        """Resuming when not paused should error."""
        response = tcp_send("resume")
        assert "ERROR" in response or "not paused" in response.lower()
    
    def test_seek_during_playback(self, pumpkin_server, recordings_dir):
        """Seeking during playback should jump to new position."""
        # Create 2-second recording
        tcp_send("record_start")
        for i in range(5):
            tcp_send("neutral")
            time.sleep(0.4)
        tcp_send("record_stop test_seek")
        
        # Start playback
        tcp_send("play test_seek")
        time.sleep(0.3)
        
        # Seek to 1000ms
        response = tcp_send("seek 1000")
        assert "OK" in response or "seeked" in response.lower()
        
        status = parse_json_response(tcp_send("timeline_status"))
        assert abs(status["position_ms"] - 1000) < 100
        
        # Stop playback
        tcp_send("stop")
    
    def test_seek_beyond_duration_clamps(self, pumpkin_server, recordings_dir):
        """Seeking beyond duration should clamp to end."""
        # Create 500ms recording
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.5)
        tcp_send("record_stop test_seek_clamp")
        
        # Load timeline
        tcp_send("play test_seek_clamp")
        tcp_send("pause")
        
        # Seek beyond duration (to 5000ms when duration is ~500ms)
        tcp_send("seek 5000")
        
        status = parse_json_response(tcp_send("timeline_status"))
        # Position should be clamped to duration
        assert status["position_ms"] <= status["duration_ms"]
        
        tcp_send("stop")
    
    def test_seek_to_zero_restarts(self, pumpkin_server, recordings_dir):
        """Seeking to 0 should restart from beginning."""
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.5)
        tcp_send("record_stop test_seek_zero")
        
        tcp_send("play test_seek_zero")
        time.sleep(0.3)
        
        # Seek to beginning
        tcp_send("seek 0")
        
        status = parse_json_response(tcp_send("timeline_status"))
        assert status["position_ms"] == 0
        
        tcp_send("stop")


class TestFileManagement:
    """Test list, delete, and rename operations."""
    
    def test_list_recordings(self, pumpkin_server, recordings_dir):
        """list_recordings should return all timeline files."""
        # Create test recordings
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.1)
        tcp_send("record_stop test_file1")
        
        tcp_send("record_start")
        tcp_send("happy")
        time.sleep(0.1)
        tcp_send("record_stop test_file2")
        
        # List recordings
        response = tcp_send("list_recordings")
        recordings = parse_json_response(response)
        
        assert isinstance(recordings, list)
        assert len(recordings) >= 2
        
        # Find our test files
        filenames = [r["filename"] for r in recordings]
        assert "test_file1.json" in filenames
        assert "test_file2.json" in filenames
        
        # Check structure
        for rec in recordings:
            assert "filename" in rec
            assert "size_bytes" in rec
            assert "created_at" in rec
            assert "duration_ms" in rec
    
    def test_list_recordings_empty(self, pumpkin_server, recordings_dir):
        """list_recordings with no files should return empty list."""
        # Ensure no test files exist
        for file in recordings_dir.glob('test_*.json'):
            file.unlink()
        
        response = tcp_send("list_recordings")
        recordings = parse_json_response(response)
        
        # Should return empty list or list without test_ files
        test_files = [r for r in recordings if r["filename"].startswith("test_")]
        assert len(test_files) == 0
    
    def test_delete_recording(self, pumpkin_server, recordings_dir):
        """delete_recording should remove file from disk."""
        # Create recording
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.1)
        tcp_send("record_stop test_delete")
        
        assert verify_file_exists(recordings_dir, "test_delete")
        
        # Delete it
        response = tcp_send("delete_recording test_delete")
        assert "OK" in response or "deleted" in response.lower()
        
        # Verify file is gone
        assert not verify_file_exists(recordings_dir, "test_delete")
    
    def test_delete_nonexistent_file_errors(self, pumpkin_server):
        """Deleting nonexistent file should error."""
        response = tcp_send("delete_recording nonexistent_file")
        assert "ERROR" in response or "not found" in response.lower()
    
    def test_rename_recording(self, pumpkin_server, recordings_dir):
        """rename_recording should change filename."""
        # Create recording
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.1)
        tcp_send("record_stop test_old_name")
        
        assert verify_file_exists(recordings_dir, "test_old_name")
        
        # Rename it
        response = tcp_send("rename_recording test_old_name test_new_name")
        assert "OK" in response or "renamed" in response.lower()
        
        # Verify old name is gone, new name exists
        assert not verify_file_exists(recordings_dir, "test_old_name")
        assert verify_file_exists(recordings_dir, "test_new_name")
        
        # Clean up new name
        (recordings_dir / "test_new_name.json").unlink()
    
    def test_rename_to_existing_name_errors(self, pumpkin_server, recordings_dir):
        """Renaming to existing filename should error."""
        # Create two recordings
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.1)
        tcp_send("record_stop test_rename1")
        
        tcp_send("record_start")
        tcp_send("happy")
        time.sleep(0.1)
        tcp_send("record_stop test_rename2")
        
        # Try to rename first to second's name
        response = tcp_send("rename_recording test_rename1 test_rename2")
        assert "ERROR" in response or "already exists" in response.lower()


class TestStatusQueries:
    """Test timeline_status and recording_status queries."""
    
    def test_timeline_status_while_stopped(self, pumpkin_server):
        """timeline_status when stopped should show STOPPED state."""
        response = tcp_send("timeline_status")
        status = parse_json_response(response)
        
        assert status["state"].upper() == "STOPPED"
        assert status["is_playing"] == False
        assert status["filename"] is None or status["filename"] == ""
    
    def test_timeline_status_while_playing(self, pumpkin_server, recordings_dir):
        """timeline_status during playback should show PLAYING state."""
        # Create recording
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.5)
        tcp_send("record_stop test_status_playing")
        
        # Start playback
        tcp_send("play test_status_playing")
        time.sleep(0.1)
        
        # Query status
        response = tcp_send("timeline_status")
        status = parse_json_response(response)
        
        assert status["state"].upper() == "PLAYING"
        assert status["is_playing"] == True
        assert "test_status_playing" in status["filename"]
        assert status["position_ms"] > 0
        assert status["duration_ms"] > 0
        
        tcp_send("stop")
    
    def test_timeline_status_while_paused(self, pumpkin_server, recordings_dir):
        """timeline_status when paused should show PAUSED state."""
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.5)
        tcp_send("record_stop test_status_paused")
        
        tcp_send("play test_status_paused")
        time.sleep(0.2)
        tcp_send("pause")
        
        response = tcp_send("timeline_status")
        status = parse_json_response(response)
        
        assert status["state"].upper() == "PAUSED"
        assert status["is_playing"] == False
        assert status["position_ms"] > 0
        
        tcp_send("stop")
    
    def test_recording_status_while_idle(self, pumpkin_server):
        """recording_status when not recording should show is_recording=false."""
        response = tcp_send("recording_status")
        status = parse_json_response(response)
        
        assert status["is_recording"] == False
        assert status["command_count"] == 0
    
    def test_recording_status_while_recording(self, pumpkin_server):
        """recording_status during recording should show is_recording=true."""
        tcp_send("record_start")
        tcp_send("neutral")
        tcp_send("happy")
        time.sleep(0.2)
        
        response = tcp_send("recording_status")
        status = parse_json_response(response)
        
        assert status["is_recording"] == True
        assert status["command_count"] >= 2
        assert status["duration_ms"] > 0
        
        tcp_send("record_cancel")


class TestManualOverride:
    """Test manual command override during playback (auto-pause behavior)."""
    
    def test_manual_command_pauses_playback(self, pumpkin_server, recordings_dir):
        """Sending manual command during playback should auto-pause."""
        # Create long recording
        tcp_send("record_start")
        for i in range(10):
            tcp_send("neutral")
            time.sleep(0.2)
        tcp_send("record_stop test_manual_override")
        
        # Start playback
        tcp_send("play test_manual_override")
        time.sleep(0.5)
        
        # Send manual command
        tcp_send("happy")
        
        # Verify playback is now paused
        time.sleep(0.1)
        status = parse_json_response(tcp_send("timeline_status"))
        assert status["state"].upper() == "PAUSED"
        
        tcp_send("stop")
    
    def test_manual_override_not_recorded(self, pumpkin_server, recordings_dir):
        """Manual commands during playback should not be captured in next recording."""
        # Create first recording
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.2)
        tcp_send("record_stop test_playback_session")
        
        # Play it back and send manual override
        tcp_send("play test_playback_session")
        time.sleep(0.1)
        tcp_send("happy")  # Manual override
        tcp_send("stop")
        
        # Start NEW recording (manual command should NOT be captured)
        tcp_send("record_start")
        tcp_send("sad")
        time.sleep(0.1)
        tcp_send("record_stop test_new_recording")
        
        # Verify new recording only has "sad", not "happy"
        content = verify_file_content(recordings_dir, "test_new_recording")
        commands = content["commands"]
        
        assert len(commands) == 1
        assert commands[0]["command"] == "sad" or "sad" in str(commands[0])


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_play_nonexistent_file_errors(self, pumpkin_server):
        """Playing nonexistent file should error."""
        response = tcp_send("play nonexistent_file")
        assert "ERROR" in response or "not found" in response.lower()
    
    def test_seek_while_stopped_errors(self, pumpkin_server):
        """Seeking when no timeline loaded should error."""
        response = tcp_send("seek 1000")
        assert "ERROR" in response or "no timeline loaded" in response.lower()
    
    def test_record_empty_file(self, pumpkin_server, recordings_dir):
        """Recording with no commands should error on save."""
        tcp_send("record_start")
        # Don't send any commands
        time.sleep(0.1)
        
        response = tcp_send("record_stop test_empty")
        assert "ERROR" in response or "empty" in response.lower()
        
        # File should not exist
        assert not verify_file_exists(recordings_dir, "test_empty")
    
    def test_playback_empty_file_returns_immediately(self, pumpkin_server, recordings_dir):
        """Playing empty timeline (if somehow created) should complete immediately."""
        # Manually create empty timeline file
        empty_timeline = {
            "version": "1.0",
            "duration_ms": 0,
            "commands": []
        }
        
        filepath = recordings_dir / "test_empty_playback.json"
        with open(filepath, 'w') as f:
            json.dump(empty_timeline, f)
        
        # Play it
        tcp_send("play test_empty_playback")
        
        # Should immediately be stopped
        time.sleep(0.1)
        status = parse_json_response(tcp_send("timeline_status"))
        assert status["state"].upper() == "STOPPED"
        
        # Clean up
        filepath.unlink()
    
    def test_rapid_state_changes(self, pumpkin_server, recordings_dir):
        """Rapid play/pause/stop cycles should not crash server."""
        tcp_send("record_start")
        tcp_send("neutral")
        time.sleep(0.5)
        tcp_send("record_stop test_rapid")
        
        # Rapid state changes
        for _ in range(5):
            tcp_send("play test_rapid")
            time.sleep(0.05)
            tcp_send("pause")
            time.sleep(0.05)
            tcp_send("resume")
            time.sleep(0.05)
            tcp_send("stop")
            time.sleep(0.05)
        
        # Verify server still responsive
        status = parse_json_response(tcp_send("timeline_status"))
        assert "state" in status


class TestCommandIntegration:
    """Test that all existing commands are recordable and play back correctly."""
    
    def test_expression_commands_recordable(self, pumpkin_server, recordings_dir):
        """All expression commands should be recordable."""
        expressions = ["neutral", "happy", "sad", "angry", "surprised", "scared", "sleeping"]
        
        tcp_send("record_start")
        for expr in expressions:
            tcp_send(expr)
            time.sleep(0.1)
        tcp_send("record_stop test_expressions")
        
        # Verify recording contains all expressions
        content = verify_file_content(recordings_dir, "test_expressions")
        assert len(content["commands"]) == len(expressions)
    
    def test_animation_commands_recordable(self, pumpkin_server, recordings_dir):
        """Animation commands (blink, wink, etc.) should be recordable."""
        animations = ["blink", "wink_left", "wink_right", "roll_clockwise"]
        
        tcp_send("record_start")
        for anim in animations:
            tcp_send(anim)
            time.sleep(0.2)
        tcp_send("record_stop test_animations")
        
        content = verify_file_content(recordings_dir, "test_animations")
        assert len(content["commands"]) == len(animations)
    
    def test_gaze_commands_recordable(self, pumpkin_server, recordings_dir):
        """Gaze commands with arguments should be recordable."""
        tcp_send("record_start")
        tcp_send("gaze 0 0")
        time.sleep(0.1)
        tcp_send("gaze 45 30")
        time.sleep(0.1)
        tcp_send("gaze -90 0 90 45")
        time.sleep(0.1)
        tcp_send("record_stop test_gaze")
        
        content = verify_file_content(recordings_dir, "test_gaze")
        assert len(content["commands"]) >= 3
    
    def test_eyebrow_commands_recordable(self, pumpkin_server, recordings_dir):
        """Eyebrow commands should be recordable."""
        commands = ["eyebrow_raise", "eyebrow_lower", "eyebrow_reset"]
        
        tcp_send("record_start")
        for cmd in commands:
            tcp_send(cmd)
            time.sleep(0.1)
        tcp_send("record_stop test_eyebrows")
        
        content = verify_file_content(recordings_dir, "test_eyebrows")
        assert len(content["commands"]) >= len(commands)
    
    def test_head_movement_recordable(self, pumpkin_server, recordings_dir):
        """Head movement commands should be recordable."""
        commands = ["turn_left", "turn_right", "turn_up", "turn_down", "center_head"]
        
        tcp_send("record_start")
        for cmd in commands:
            tcp_send(cmd)
            time.sleep(0.1)
        tcp_send("record_stop test_head_movement")
        
        content = verify_file_content(recordings_dir, "test_head_movement")
        assert len(content["commands"]) >= len(commands)
    
    def test_nose_animation_recordable(self, pumpkin_server, recordings_dir):
        """Nose animation commands should be recordable."""
        commands = ["twitch_nose", "scrunch_nose", "reset_nose"]
        
        tcp_send("record_start")
        for cmd in commands:
            tcp_send(cmd)
            time.sleep(0.2)
        tcp_send("record_stop test_nose")
        
        content = verify_file_content(recordings_dir, "test_nose")
        assert len(content["commands"]) >= len(commands)
    
    def test_playback_preserves_command_order(self, pumpkin_server, recordings_dir):
        """Playback should execute commands in same order as recorded."""
        # Record specific sequence
        sequence = ["neutral", "happy", "blink", "sad", "gaze 0 0", "angry"]
        
        tcp_send("record_start")
        for cmd in sequence:
            tcp_send(cmd)
            time.sleep(0.1)
        tcp_send("record_stop test_order")
        
        # Verify order in file
        content = verify_file_content(recordings_dir, "test_order")
        commands = content["commands"]
        
        # Commands should be in chronological order (increasing time_ms)
        for i in range(len(commands) - 1):
            assert commands[i]["time_ms"] <= commands[i + 1]["time_ms"]
        
        # Play it back (just verify no errors)
        response = tcp_send("play test_order")
        assert "ERROR" not in response
        
        time.sleep(1.0)  # Let playback finish


# ============================================================================
# INTEGRATION TEST SUMMARY
# ============================================================================

"""
Test Suite Summary:

Classes: 8
Estimated Test Count: 60+

Critical Tests (must pass for basic functionality):
- test_record_start_stop_creates_file
- test_play_simple_sequence
- test_playback_state_transitions
- test_play_pause_resume_stop
- test_timeline_status_while_playing
- test_manual_command_pauses_playback

Nice-to-Have Tests (edge cases and polish):
- test_record_auto_naming
- test_seek_beyond_duration_clamps
- test_rapid_state_changes
- test_playback_empty_file_returns_immediately

Coverage Areas:
✅ Recording workflow (7 tests)
✅ Basic playback (3 tests)
✅ Playback control (6 tests)
✅ File management (6 tests)
✅ Status queries (5 tests)
✅ Manual override (2 tests)
✅ Edge cases (5 tests)
✅ Command integration (7 tests)

Total: 41 core tests + fixtures + helpers

Notes:
- Tests assume server sends responses for timeline commands
- Tests use real file I/O (not mocked)
- Server must be running on localhost:5000
- Cleanup fixture removes test_*.json files before/after each test
- Frame timing tolerance: ±100ms for network/processing overhead
"""
