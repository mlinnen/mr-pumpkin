#!/usr/bin/env python3
"""
Test script for timeline.py WI-3 through WI-6 features.
Tests seek, recording, status, and file management.
"""

import json
import tempfile
import time
from pathlib import Path
from timeline import Timeline, TimelineEntry, Playback, RecordingSession, FileManager, PlaybackState


def test_seek():
    """Test WI-3: Seek support."""
    print("Testing seek support...")
    
    # Create test timeline
    with tempfile.TemporaryDirectory() as tmpdir:
        recordings_dir = Path(tmpdir)
        
        # Create and save a test timeline
        timeline = Timeline()
        timeline.add_command(0, "cmd1")
        timeline.add_command(1000, "cmd2")
        timeline.add_command(2000, "cmd3")
        timeline.add_command(3000, "cmd4")
        timeline.save(recordings_dir / "test.json")
        
        # Create playback
        playback = Playback(recordings_dir)
        executed_commands = []
        
        def callback(cmd, args):
            executed_commands.append(cmd)
        
        playback.set_command_callback(callback)
        
        # Test seek while stopped
        playback.play("test.json")
        playback.stop()
        playback.seek(1500)
        assert playback.current_position_ms == 1500, "Seek position incorrect"
        
        # Test seek while paused
        playback.play("test.json")
        playback.pause()
        playback.seek(2500)
        assert playback.current_position_ms == 2500, "Seek position during pause incorrect"
        assert playback.state == PlaybackState.PAUSED, "State changed unexpectedly"
        
        # Test seek while playing
        playback.resume()
        playback.seek(500)
        assert playback.current_position_ms == 500, "Seek position during play incorrect"
        assert playback.state == PlaybackState.PLAYING, "State changed unexpectedly"
        
        # Test edge cases
        playback.seek(-100)  # Should clamp to 0
        assert playback.current_position_ms == 0, "Negative seek not clamped to 0"
        
        playback.seek(10000)  # Should clamp to duration
        assert playback.current_position_ms == timeline.duration_ms, "Seek past end not clamped"
    
    print("✓ Seek support working")


def test_recording():
    """Test WI-5: Recording session."""
    print("Testing recording session...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        recordings_dir = Path(tmpdir)
        session = RecordingSession(recordings_dir)
        
        # Test start/stop
        session.start()
        assert session.is_recording, "Recording not started"
        
        session.record_command("set_expression", {"expression": "happy"})
        time.sleep(0.01)  # Small delay
        session.record_command("blink")
        
        filename = session.stop()
        assert filename.endswith(".json"), "Filename missing .json extension"
        assert not session.is_recording, "Recording still active after stop"
        
        # Verify file was created
        assert (recordings_dir / filename).exists(), "Recording file not created"
        
        # Verify content
        timeline = Timeline.load(recordings_dir / filename)
        assert len(timeline.commands) == 2, f"Expected 2 commands, got {len(timeline.commands)}"
        assert timeline.commands[0].command == "set_expression", "First command incorrect"
        assert timeline.commands[1].command == "blink", "Second command incorrect"
        
        # Test auto-naming
        time.sleep(1.1)  # Ensure unique timestamp (1 second granularity)
        session.start()
        session.record_command("test")
        filename2 = session.stop()
        assert "recording_" in filename2, "Auto-generated name incorrect"
        assert filename2 != filename, "Auto-generated names should be unique"
        
        # Test duplicate filename error
        session.start()
        session.record_command("test")
        try:
            session.stop(filename)
            assert False, "Should raise FileExistsError"
        except FileExistsError:
            pass
        
        # Test empty recording error
        session.start()
        try:
            session.stop("empty")
            assert False, "Should raise ValueError for empty recording"
        except ValueError as e:
            assert "no commands" in str(e), "Wrong error message"
        
        # Test cancel
        session.start()
        session.record_command("test")
        session.cancel()
        assert not session.is_recording, "Cancel failed"
        assert len(session.commands) == 0, "Commands not cleared"
    
    print("✓ Recording session working")


def test_status_queries():
    """Test WI-6: Status query API."""
    print("Testing status queries...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        recordings_dir = Path(tmpdir)
        
        # Create test timeline
        timeline = Timeline()
        timeline.add_command(0, "cmd1")
        timeline.add_command(1000, "cmd2")
        timeline.save(recordings_dir / "test.json")
        
        playback = Playback(recordings_dir)
        
        # Test status when stopped
        status = playback.get_status()
        assert status["state"] == "stopped", "State incorrect"
        assert status["filename"] is None, "Filename should be None"
        assert status["position_ms"] == 0, "Position should be 0"
        assert status["is_playing"] is False, "is_playing should be False"
        
        # Test status when playing
        playback.play("test.json")
        status = playback.get_status()
        assert status["state"] == "playing", "State should be playing"
        assert status["filename"] == "test.json", "Filename incorrect"
        assert status["duration_ms"] == 1000, "Duration incorrect"
        assert status["is_playing"] is True, "is_playing should be True"
        
        # Test status when paused
        playback.pause()
        status = playback.get_status()
        assert status["state"] == "paused", "State should be paused"
        assert status["is_playing"] is False, "is_playing should be False"
    
    print("✓ Status queries working")


def test_file_management():
    """Test WI-4: File management commands."""
    print("Testing file management...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        recordings_dir = Path(tmpdir)
        fm = FileManager(recordings_dir)
        
        # Create test timelines
        timeline1 = Timeline()
        timeline1.add_command(0, "cmd1")
        timeline1.save(recordings_dir / "test1.json")
        
        timeline2 = Timeline()
        timeline2.add_command(0, "cmd2")
        timeline2.save(recordings_dir / "test2.json")
        
        # Test list_recordings
        recordings = fm.list_recordings()
        assert len(recordings) == 2, f"Expected 2 recordings, got {len(recordings)}"
        filenames = [r["filename"] for r in recordings]
        assert "test1.json" in filenames, "test1.json missing"
        assert "test2.json" in filenames, "test2.json missing"
        
        # Test download_timeline
        content = fm.download_timeline("test1.json")
        data = json.loads(content)
        assert "commands" in data, "JSON missing commands field"
        assert data["commands"][0]["command"] == "cmd1", "Content incorrect"
        
        # Test download without .json extension
        content2 = fm.download_timeline("test1")
        assert content == content2, "Extension handling failed"
        
        # Test download non-existent file
        try:
            fm.download_timeline("nonexistent.json")
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            pass
        
        # Test upload_timeline
        new_timeline = {
            "version": "1.0",
            "duration_ms": 500,
            "commands": [
                {"time_ms": 0, "command": "test_upload"}
            ]
        }
        fm.upload_timeline("uploaded.json", json.dumps(new_timeline))
        assert (recordings_dir / "uploaded.json").exists(), "Upload failed"
        
        # Verify uploaded content
        loaded = Timeline.load(recordings_dir / "uploaded.json")
        assert loaded.commands[0].command == "test_upload", "Uploaded content incorrect"
        
        # Test upload duplicate
        try:
            fm.upload_timeline("uploaded.json", json.dumps(new_timeline))
            assert False, "Should raise FileExistsError"
        except FileExistsError:
            pass
        
        # Test upload invalid JSON
        try:
            fm.upload_timeline("invalid.json", "{invalid json")
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "Invalid JSON" in str(e), "Wrong error message"
        
        # Test delete_timeline
        fm.delete_timeline("test2.json")
        assert not (recordings_dir / "test2.json").exists(), "Delete failed"
        
        # Test delete non-existent
        try:
            fm.delete_timeline("nonexistent.json")
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            pass
        
        # Test rename_timeline
        fm.rename_timeline("test1.json", "renamed.json")
        assert not (recordings_dir / "test1.json").exists(), "Old file still exists"
        assert (recordings_dir / "renamed.json").exists(), "New file not created"
        
        # Test rename non-existent
        try:
            fm.rename_timeline("nonexistent.json", "new.json")
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            pass
        
        # Test rename to existing file
        try:
            fm.rename_timeline("renamed.json", "uploaded.json")
            assert False, "Should raise FileExistsError"
        except FileExistsError:
            pass
    
    print("✓ File management working")


def test_seek_during_playback():
    """Test seek integration with playback state machine."""
    print("Testing seek during playback...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        recordings_dir = Path(tmpdir)
        
        # Create test timeline
        timeline = Timeline()
        timeline.add_command(0, "cmd0")
        timeline.add_command(100, "cmd100")
        timeline.add_command(200, "cmd200")
        timeline.add_command(500, "cmd500")
        timeline.save(recordings_dir / "seek_test.json")
        
        playback = Playback(recordings_dir)
        executed = []
        
        def callback(cmd, args):
            executed.append(cmd)
        
        playback.set_command_callback(callback)
        playback.play("seek_test.json")
        
        # Execute first two commands
        playback.update(150)
        assert len(executed) == 2, "Should have executed 2 commands"
        assert executed == ["cmd0", "cmd100"], "Wrong commands executed"
        
        # Seek backward
        executed.clear()
        playback.seek(50)
        playback.update(10)
        # Should not re-execute cmd0 (already executed before seek position)
        assert len(executed) == 0, "Should not re-execute commands"
        
        # Seek forward to middle of timeline
        playback.seek(250)
        assert playback.current_position_ms == 250, "Seek position incorrect"
        
        # Commands between old position and new position are skipped
        executed.clear()
        playback.update(10)  # Now at 260ms
        assert "cmd200" not in executed, "Should not execute skipped commands"
        
        # Continue playback and verify cmd500 executes
        playback.update(250)  # Move to 510ms
        assert "cmd500" in executed, "cmd500 should execute during normal playback"
        
        # Verify playback stops at end
        assert playback.state == PlaybackState.STOPPED, "Should stop at end"
        
        # Seek past end
        playback.play("seek_test.json")
        playback.seek(1000)
        assert playback.current_position_ms == timeline.duration_ms, "Seek past end not clamped"
    
    print("✓ Seek during playback working")


if __name__ == "__main__":
    print("Testing timeline.py features (WI-3, WI-4, WI-5, WI-6)...\n")
    
    test_seek()
    test_recording()
    test_status_queries()
    test_file_management()
    test_seek_during_playback()
    
    print("\n✓ All tests passed!")
