"""
Comprehensive test suite for recording chaining (issue #55).

Tests the stack-based playback engine feature that allows one recording
to embed another via the play_recording command.

Test Coverage:
- Single level chaining (parent -> sub -> parent)
- Stack clearing on stop()
- play_recording is NOT dispatched to command callback
- Depth limit enforcement (max 5 levels)
- Missing/invalid sub-recording file handling
- play_recording in _VALID_COMMANDS
- Multi-level nesting (parent -> sub1 -> sub2 -> sub1)
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, call
from timeline import Timeline, TimelineEntry, Playback, PlaybackState


# Helper functions

def make_timeline(commands_list, duration_ms=None):
    """Helper: create Timeline from list of (time_ms, command, args) tuples."""
    timeline = Timeline()
    for item in commands_list:
        time_ms, cmd = item[0], item[1]
        args = item[2] if len(item) > 2 else None
        timeline.add_command(time_ms, cmd, args)
    if duration_ms is not None:
        timeline.duration_ms = duration_ms
    return timeline


def save_timeline(timeline, dir_path, filename):
    """Save a timeline to a temp directory."""
    if not filename.endswith('.json'):
        filename = f"{filename}.json"
    filepath = dir_path / filename
    timeline.save(filepath)
    return filepath


# Test cases

def test_single_level_chaining_command_execution_order(tmp_path):
    """Test that commands execute in correct order: parent-before, sub, parent-after."""
    # Create sub-recording with 2 commands
    sub_timeline = make_timeline([
        (0, "set_expression", {"expression": "happy"}),
        (500, "blink"),
    ], duration_ms=1000)
    save_timeline(sub_timeline, tmp_path, "sub.json")
    
    # Create parent with play_recording in the middle
    parent_timeline = make_timeline([
        (0, "set_expression", {"expression": "neutral"}),
        (500, "play_recording", {"filename": "sub"}),
        (600, "set_expression", {"expression": "sad"}),
    ], duration_ms=2000)
    save_timeline(parent_timeline, tmp_path, "parent.json")
    
    # Setup playback with callback
    playback = Playback(recordings_dir=tmp_path)
    mock_callback = Mock()
    playback.set_command_callback(mock_callback)
    
    # Play parent
    playback.play("parent.json")
    
    # Update to execute first command (neutral at 0ms)
    playback.update(100)
    
    # Update to trigger play_recording (at 500ms)
    playback.update(500)
    
    # Now we should be in sub-recording, update to execute sub commands
    playback.update(100)  # Execute happy at 0ms in sub
    playback.update(500)  # Execute blink at 500ms in sub
    playback.update(500)  # Finish sub (1000ms), pop back to parent
    
    # Update to execute final command in parent (sad at 600ms from parent perspective)
    playback.update(200)
    
    # Verify command execution order
    assert mock_callback.call_count == 4
    calls = mock_callback.call_args_list
    
    # First: parent neutral
    assert calls[0] == call("set_expression", {"expression": "neutral"})
    # Second: sub happy
    assert calls[1] == call("set_expression", {"expression": "happy"})
    # Third: sub blink
    assert calls[2] == call("blink", {})
    # Fourth: parent sad (resumes after sub)
    assert calls[3] == call("set_expression", {"expression": "sad"})


def test_chaining_completes_and_stops(tmp_path):
    """Test that playback state is STOPPED after parent and sub both complete."""
    # Sub-recording
    sub_timeline = make_timeline([
        (0, "blink"),
    ], duration_ms=500)
    save_timeline(sub_timeline, tmp_path, "sub.json")
    
    # Parent with sub in middle
    parent_timeline = make_timeline([
        (0, "set_expression", {"expression": "neutral"}),
        (200, "play_recording", {"filename": "sub"}),
        (300, "set_expression", {"expression": "happy"}),
    ], duration_ms=1000)
    save_timeline(parent_timeline, tmp_path, "parent.json")
    
    playback = Playback(recordings_dir=tmp_path)
    mock_callback = Mock()
    playback.set_command_callback(mock_callback)
    
    playback.play("parent.json")
    
    # Execute all commands and advance to completion
    playback.update(100)   # neutral
    playback.update(200)   # trigger play_recording
    playback.update(600)   # complete sub and pop back
    playback.update(800)   # happy and complete parent
    
    # Verify stopped
    assert playback.state == PlaybackState.STOPPED
    assert len(playback._stack) == 0


def test_play_recording_not_dispatched_to_callback(tmp_path):
    """Test that play_recording command is NOT sent to the command callback."""
    # Sub-recording
    sub_timeline = make_timeline([
        (0, "blink"),
    ], duration_ms=500)
    save_timeline(sub_timeline, tmp_path, "sub.json")
    
    # Parent with play_recording
    parent_timeline = make_timeline([
        (0, "set_expression", {"expression": "neutral"}),
        (200, "play_recording", {"filename": "sub"}),
    ], duration_ms=1000)
    save_timeline(parent_timeline, tmp_path, "parent.json")
    
    playback = Playback(recordings_dir=tmp_path)
    mock_callback = Mock()
    playback.set_command_callback(mock_callback)
    
    playback.play("parent.json")
    playback.update(300)  # Execute neutral and trigger play_recording
    playback.update(600)  # Execute blink in sub
    
    # Verify callback was NOT called with play_recording
    calls = mock_callback.call_args_list
    command_names = [call_args[0][0] for call_args in calls]
    
    assert "play_recording" not in command_names
    assert "set_expression" in command_names
    assert "blink" in command_names


def test_stack_cleared_on_stop(tmp_path):
    """Test that stop() clears the playback stack mid-sub-recording."""
    # Sub-recording with long duration
    sub_timeline = make_timeline([
        (0, "blink"),
        (500, "set_expression", {"expression": "happy"}),
    ], duration_ms=2000)
    save_timeline(sub_timeline, tmp_path, "sub.json")
    
    # Parent
    parent_timeline = make_timeline([
        (0, "set_expression", {"expression": "neutral"}),
        (200, "play_recording", {"filename": "sub"}),
    ], duration_ms=1000)
    save_timeline(parent_timeline, tmp_path, "parent.json")
    
    playback = Playback(recordings_dir=tmp_path)
    mock_callback = Mock()
    playback.set_command_callback(mock_callback)
    
    playback.play("parent.json")
    playback.update(300)  # Enter sub-recording
    
    # Verify we're in nested state
    assert len(playback._stack) > 0
    assert playback.state == PlaybackState.PLAYING
    
    # Stop mid-playback
    playback.stop()
    
    # Verify stack is cleared
    assert len(playback._stack) == 0
    assert playback.state == PlaybackState.STOPPED
    assert playback.current_position_ms == 0


def test_depth_limit_exceeded(tmp_path):
    """Test that exceeding max_depth (5) prevents further nesting."""
    # Create a chain of recordings that would nest 6 deep
    # Each recording plays the next one
    
    # Deepest recording (level 6 - should not be reached)
    for i in range(7):
        if i == 0:
            # Leaf recording (no sub-recording)
            timeline = make_timeline([
                (0, "blink"),
            ], duration_ms=500)
        else:
            # Each level plays the previous one
            timeline = make_timeline([
                (0, "set_expression", {"expression": "neutral"}),
                (100, "play_recording", {"filename": f"level{i-1}"}),
            ], duration_ms=1000)
        save_timeline(timeline, tmp_path, f"level{i}.json")
    
    playback = Playback(recordings_dir=tmp_path)
    mock_callback = Mock()
    playback.set_command_callback(mock_callback)
    
    # Play level 6 (which tries to nest 6 deep total)
    playback.play("level6.json")
    
    # Advance through multiple levels
    for _ in range(10):
        errors = playback.update(200)
        if errors:
            # Check for depth limit error
            assert any("Maximum nesting depth" in err for err in errors)
            break
    
    # Verify we don't have more than max_depth items on stack
    assert len(playback._stack) <= playback._max_depth


def test_missing_sub_recording_file(tmp_path):
    """Test that missing sub-recording file is handled gracefully."""
    # Parent references non-existent sub
    parent_timeline = make_timeline([
        (0, "set_expression", {"expression": "neutral"}),
        (200, "play_recording", {"filename": "nonexistent"}),
        (300, "set_expression", {"expression": "happy"}),
    ], duration_ms=1000)
    save_timeline(parent_timeline, tmp_path, "parent.json")
    
    playback = Playback(recordings_dir=tmp_path)
    mock_callback = Mock()
    playback.set_command_callback(mock_callback)
    
    playback.play("parent.json")
    
    # Execute first command
    playback.update(100)
    
    # Try to execute play_recording with missing file
    errors = playback.update(200)
    
    # Should get error about missing file
    assert len(errors) > 0
    assert any("nonexistent" in err.lower() for err in errors)
    
    # Playback should continue (not crash)
    assert playback.state == PlaybackState.PLAYING
    
    # Should still execute the next command (happy)
    playback.update(200)
    assert mock_callback.call_count == 2
    calls = mock_callback.call_args_list
    assert calls[0] == call("set_expression", {"expression": "neutral"})
    assert calls[1] == call("set_expression", {"expression": "happy"})


def test_play_recording_in_valid_commands():
    """Test that play_recording is in _VALID_COMMANDS in generator.py."""
    from skill.generator import _VALID_COMMANDS
    
    assert "play_recording" in _VALID_COMMANDS


def test_multi_level_nesting_parent_sub1_sub2(tmp_path):
    """Test multi-level nesting: parent -> sub1 -> sub2, then unwinding correctly."""
    # Level 2: deepest sub-recording
    sub2_timeline = make_timeline([
        (0, "blink"),
    ], duration_ms=500)
    save_timeline(sub2_timeline, tmp_path, "sub2.json")
    
    # Level 1: sub1 calls sub2
    sub1_timeline = make_timeline([
        (0, "set_expression", {"expression": "happy"}),
        (200, "play_recording", {"filename": "sub2"}),
        (300, "wink_left"),
    ], duration_ms=1000)
    save_timeline(sub1_timeline, tmp_path, "sub1.json")
    
    # Level 0: parent calls sub1
    parent_timeline = make_timeline([
        (0, "set_expression", {"expression": "neutral"}),
        (200, "play_recording", {"filename": "sub1"}),
        (300, "set_expression", {"expression": "sad"}),
    ], duration_ms=2000)
    save_timeline(parent_timeline, tmp_path, "parent.json")
    
    playback = Playback(recordings_dir=tmp_path)
    mock_callback = Mock()
    playback.set_command_callback(mock_callback)
    
    playback.play("parent.json")
    
    # Execute step by step
    playback.update(100)   # parent: neutral
    playback.update(200)   # parent: trigger sub1
    playback.update(100)   # sub1: happy
    playback.update(200)   # sub1: trigger sub2
    playback.update(100)   # sub2: blink
    playback.update(500)   # complete sub2, pop to sub1
    playback.update(200)   # sub1: wink_left
    playback.update(600)   # complete sub1, pop to parent
    playback.update(200)   # parent: sad
    
    # Verify execution order
    calls = mock_callback.call_args_list
    assert len(calls) == 5
    
    # Order: parent neutral, sub1 happy, sub2 blink, sub1 wink, parent sad
    assert calls[0] == call("set_expression", {"expression": "neutral"})
    assert calls[1] == call("set_expression", {"expression": "happy"})
    assert calls[2] == call("blink", {})
    assert calls[3] == call("wink_left", {})
    assert calls[4] == call("set_expression", {"expression": "sad"})


def test_stack_depth_status_query(tmp_path):
    """Test that get_status() returns correct stack_depth during nested playback."""
    # Sub-recording
    sub_timeline = make_timeline([
        (0, "blink"),
    ], duration_ms=1000)
    save_timeline(sub_timeline, tmp_path, "sub.json")
    
    # Parent
    parent_timeline = make_timeline([
        (0, "set_expression", {"expression": "neutral"}),
        (200, "play_recording", {"filename": "sub"}),
    ], duration_ms=2000)
    save_timeline(parent_timeline, tmp_path, "parent.json")
    
    playback = Playback(recordings_dir=tmp_path)
    playback.play("parent.json")
    
    # Before entering sub
    status = playback.get_status()
    assert status["stack_depth"] == 0
    
    # Enter sub-recording
    playback.update(300)
    status = playback.get_status()
    assert status["stack_depth"] == 1
    
    # Complete sub and pop back
    playback.update(1200)
    status = playback.get_status()
    assert status["stack_depth"] == 0


def test_empty_filename_in_play_recording(tmp_path):
    """Test that play_recording with empty filename is ignored."""
    parent_timeline = make_timeline([
        (0, "set_expression", {"expression": "neutral"}),
        (200, "play_recording", {"filename": ""}),
        (300, "set_expression", {"expression": "happy"}),
    ], duration_ms=1000)
    save_timeline(parent_timeline, tmp_path, "parent.json")
    
    playback = Playback(recordings_dir=tmp_path)
    mock_callback = Mock()
    playback.set_command_callback(mock_callback)
    
    playback.play("parent.json")
    playback.update(100)   # neutral
    playback.update(300)   # empty play_recording (should skip)
    playback.update(100)   # happy
    
    # Should only execute neutral and happy, not crash
    assert mock_callback.call_count == 2
    calls = mock_callback.call_args_list
    assert calls[0] == call("set_expression", {"expression": "neutral"})
    assert calls[1] == call("set_expression", {"expression": "happy"})


def test_play_recording_near_end_of_parent(tmp_path):
    """Test play_recording near the end of parent timeline."""
    sub_timeline = make_timeline([
        (0, "blink"),
    ], duration_ms=500)
    save_timeline(sub_timeline, tmp_path, "sub.json")
    
    # play_recording just before duration ends
    parent_timeline = make_timeline([
        (0, "set_expression", {"expression": "neutral"}),
        (900, "play_recording", {"filename": "sub"}),
    ], duration_ms=1000)
    save_timeline(parent_timeline, tmp_path, "parent.json")
    
    playback = Playback(recordings_dir=tmp_path)
    mock_callback = Mock()
    playback.set_command_callback(mock_callback)
    
    playback.play("parent.json")
    playback.update(100)    # neutral
    playback.update(900)   # should trigger play_recording
    
    # Should be in the sub-recording
    assert playback.state == PlaybackState.PLAYING
    assert len(playback._stack) == 1
    
    # Complete the sub - this will pop back to parent at position 900ms
    playback.update(600)
    
    # Back at parent but still playing (position 900ms + 600ms = 1500ms in parent timeline)
    # Need one more update to reach parent's duration
    assert playback.state == PlaybackState.PLAYING
    assert len(playback._stack) == 0
    
    # Advance to finish parent
    playback.update(100)
    assert playback.state == PlaybackState.STOPPED
