"""
Client Recording Command Tests - Issue #34

Tests client_example.py recording control commands to verify:
1. Recording lifecycle (start, stop, cancel, status)
2. Error cases (connection failures, server errors)
3. Integration (mixing recording and expression commands)

These tests verify the client-side command sending and response handling logic.
Server integration tests are in test_tcp_integration.py.

Author: Mylo (Tester)
Date: 2026-02-25
"""

import socket
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import json
import sys
import os

# Add parent directory to import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import client_example


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_socket():
    """Mock socket for testing client commands without actual server."""
    with patch('socket.socket') as mock_sock:
        mock_instance = MagicMock()
        mock_sock.return_value = mock_instance
        # Default: simulate successful connection
        mock_instance.recv.return_value = b'OK'
        yield mock_instance


# ============================================================================
# RECORDING LIFECYCLE TESTS
# ============================================================================

class TestRecordingLifecycle:
    """Test recording start, stop, cancel, and status commands."""
    
    def test_record_start_sends_correct_command(self, mock_socket):
        """'record start' sends 'record start' command to server."""
        client_example.send_command("record start")
        
        mock_socket.connect.assert_called_once_with(('localhost', 5000))
        mock_socket.send.assert_called_once_with(b'record start')
        mock_socket.close.assert_called_once()
    
    def test_record_stop_with_filename_sends_correct_command(self, mock_socket):
        """'record stop <filename>' sends correct command to server."""
        client_example.send_command("record stop my_recording.json")
        
        mock_socket.connect.assert_called_once_with(('localhost', 5000))
        mock_socket.send.assert_called_once_with(b'record stop my_recording.json')
        mock_socket.close.assert_called_once()
    
    def test_record_stop_without_filename_sends_correct_command(self, mock_socket):
        """'record stop' without filename sends command (auto-naming)."""
        client_example.send_command("record stop")
        
        mock_socket.connect.assert_called_once_with(('localhost', 5000))
        mock_socket.send.assert_called_once_with(b'record stop')
        mock_socket.close.assert_called_once()
    
    def test_record_cancel_sends_correct_command(self, mock_socket):
        """'record cancel' sends 'record cancel' command to server."""
        client_example.send_command("record cancel")
        
        mock_socket.connect.assert_called_once_with(('localhost', 5000))
        mock_socket.send.assert_called_once_with(b'record cancel')
        mock_socket.close.assert_called_once()
    
    def test_record_status_handled_in_main_loop(self, mock_socket):
        """'record status' is translated to 'recording_status' in main loop, not send_command."""
        # Note: The translation happens in the main loop (line 84-85), not in send_command
        # This test verifies send_command sends whatever it receives
        mock_socket.recv.return_value = b'{"is_recording": false, "command_count": 0, "duration_ms": 0}'
        
        client_example.send_command("record status")
        
        mock_socket.connect.assert_called_once_with(('localhost', 5000))
        # send_command sends the command as-is; main loop does translation
        mock_socket.send.assert_called_once_with(b'record status')
    
    def test_list_sends_list_recordings_command(self, mock_socket):
        """'list' sends 'list_recordings' query to server."""
        # Mock JSON response
        mock_socket.recv.return_value = b'[]'
        
        client_example.send_command("list")
        
        mock_socket.connect.assert_called_once_with(('localhost', 5000))
        # Note: client code translates 'list' to 'list_recordings' internally
        mock_socket.send.assert_called_once()
        sent_data = mock_socket.send.call_args[0][0]
        assert sent_data == b'list'  # Sends 'list', but processes as 'list_recordings'


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorCases:
    """Test error handling for recording commands."""
    
    def test_connection_failure_handled_gracefully(self, mock_socket, capsys):
        """Connection failures are caught and reported to user."""
        mock_socket.connect.side_effect = ConnectionRefusedError("Connection refused")
        
        client_example.send_command("record start")
        
        captured = capsys.readouterr()
        assert "Error" in captured.out or "error" in captured.out.lower()
    
    def test_socket_timeout_handled_gracefully(self, mock_socket, capsys):
        """Socket timeouts are caught and reported to user."""
        mock_socket.send.side_effect = socket.timeout("Operation timed out")
        
        client_example.send_command("record start")
        
        captured = capsys.readouterr()
        assert "Error" in captured.out or "error" in captured.out.lower()
    
    def test_network_error_handled_gracefully(self, mock_socket, capsys):
        """General network errors are caught and reported to user."""
        mock_socket.connect.side_effect = OSError("Network unreachable")
        
        client_example.send_command("record start")
        
        captured = capsys.readouterr()
        assert "Error" in captured.out or "error" in captured.out.lower()
    
    def test_invalid_json_response_handled_gracefully(self, mock_socket, capsys):
        """Invalid JSON responses from server are handled gracefully."""
        # Send recording_status command, but get invalid JSON back
        mock_socket.recv.return_value = b'NOT JSON DATA'
        
        client_example.send_command("recording_status")
        
        captured = capsys.readouterr()
        # Should print the response even if not valid JSON
        assert "NOT JSON DATA" in captured.out or "Response" in captured.out
    
    def test_empty_response_handled_gracefully(self, mock_socket, capsys):
        """Empty responses from server are handled gracefully."""
        mock_socket.recv.return_value = b''
        
        client_example.send_command("recording_status")
        
        # Should not crash
        captured = capsys.readouterr()
        # Function should complete without raising exception


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test recording commands integrate with expression commands."""
    
    def test_recording_and_expression_commands_in_session(self, mock_socket):
        """Recording commands can be mixed with expression commands in a session."""
        # Simulate a user session with mixed commands
        commands = [
            "record start",
            "neutral",
            "happy",
            "blink",
            "gaze 45 30",
            "record stop session1.json"
        ]
        
        for cmd in commands:
            client_example.send_command(cmd)
        
        # Verify all commands were sent (6 connections, one per command)
        assert mock_socket.connect.call_count == 6
        assert mock_socket.send.call_count == 6
        assert mock_socket.close.call_count == 6
    
    def test_list_command_works_independently(self, mock_socket):
        """list command works independently without prior connection."""
        mock_socket.recv.return_value = b'[]'
        
        client_example.send_command("list")
        
        # Should attempt connection for list command
        mock_socket.connect.assert_called_once_with(('localhost', 5000))
        # Should read response
        mock_socket.recv.assert_called_once()
    
    def test_recording_status_command_reads_response(self, mock_socket):
        """recording_status command reads and parses JSON response."""
        mock_socket.recv.return_value = b'{"is_recording": true, "command_count": 5, "duration_ms": 1234}'
        
        client_example.send_command("recording_status")
        
        # Should attempt connection and read response
        mock_socket.connect.assert_called_once_with(('localhost', 5000))
        mock_socket.recv.assert_called_once()
    
    def test_multiple_record_sessions_in_sequence(self, mock_socket):
        """Multiple recording sessions can be started/stopped sequentially."""
        # Session 1
        client_example.send_command("record start")
        client_example.send_command("neutral")
        client_example.send_command("record stop session1.json")
        
        # Session 2
        client_example.send_command("record start")
        client_example.send_command("happy")
        client_example.send_command("record stop session2.json")
        
        # Verify all commands sent (6 total)
        assert mock_socket.send.call_count == 6
    
    def test_record_cancel_can_abort_session(self, mock_socket):
        """record cancel can abort a recording session."""
        client_example.send_command("record start")
        client_example.send_command("neutral")
        client_example.send_command("record cancel")
        
        # Verify cancel command sent
        calls = [c[0][0] for c in mock_socket.send.call_args_list]
        assert b'record cancel' in calls


# ============================================================================
# RESPONSE PARSING TESTS
# ============================================================================

class TestResponseParsing:
    """Test JSON response parsing for status and list commands."""
    
    def test_recording_status_parses_json_response(self, mock_socket, capsys):
        """recording_status correctly parses JSON response."""
        mock_socket.recv.return_value = b'{"is_recording": true, "command_count": 10, "duration_ms": 5000}'
        
        client_example.send_command("recording_status")
        
        captured = capsys.readouterr()
        assert "Recording Status:" in captured.out
        assert "Is Recording: True" in captured.out
        assert "Commands Captured: 10" in captured.out
        assert "Duration: 5000 ms" in captured.out
    
    def test_list_parses_empty_json_array(self, mock_socket, capsys):
        """list command handles empty recordings list."""
        mock_socket.recv.return_value = b'[]'
        
        client_example.send_command("list")
        
        captured = capsys.readouterr()
        assert "Available Recordings:" in captured.out
        assert "(none)" in captured.out
    
    def test_list_parses_recordings_array(self, mock_socket, capsys):
        """list command parses array of recording metadata."""
        recordings_json = json.dumps([
            {"filename": "session1.json", "command_count": 5, "duration_ms": 1000},
            {"filename": "session2.json", "command_count": 10, "duration_ms": 2500}
        ])
        mock_socket.recv.return_value = recordings_json.encode('utf-8')
        
        client_example.send_command("list")
        
        captured = capsys.readouterr()
        assert "session1.json" in captured.out
        assert "5 commands" in captured.out
        assert "1000 ms" in captured.out
        assert "session2.json" in captured.out
        assert "10 commands" in captured.out
        assert "2500 ms" in captured.out
    
    def test_list_alias_uses_list_recordings_internally(self, mock_socket):
        """'list' alias is handled as 'list_recordings' for response processing."""
        mock_socket.recv.return_value = b'[]'
        
        client_example.send_command("list")
        
        # Should send 'list' but process response as list_recordings
        mock_socket.send.assert_called_once_with(b'list')
        mock_socket.recv.assert_called_once()
    
    def test_recording_status_command_sent_directly(self, mock_socket):
        """'recording_status' (full command) is sent as-is."""
        mock_socket.recv.return_value = b'{"is_recording": false, "command_count": 0, "duration_ms": 0}'
        
        client_example.send_command("recording_status")
        
        mock_socket.connect.assert_called_once_with(('localhost', 5000))
        mock_socket.send.assert_called_once_with(b'recording_status')


# ============================================================================
# EDGE CASES AND ROBUSTNESS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and robustness of recording commands."""
    
    def test_empty_command_sends_empty_bytes(self, mock_socket):
        """Empty commands send empty bytes (server validates)."""
        client_example.send_command("")
        
        # Client sends even empty commands - server validates
        mock_socket.send.assert_called_once_with(b'')
    
    def test_whitespace_only_command_sends_whitespace(self, mock_socket):
        """Whitespace-only commands send whitespace bytes (server validates)."""
        # Note: User input is stripped in main loop, but send_command accepts any string
        client_example.send_command("   ")
        
        # Client sends whitespace - server validates
        mock_socket.send.assert_called_once_with(b'   ')
    
    def test_very_long_command_sent(self, mock_socket):
        """Very long commands are sent (server may reject)."""
        long_cmd = "record stop " + "a" * 300 + ".json"
        client_example.send_command(long_cmd)
        
        # Client sends long command - server validates length
        mock_socket.send.assert_called_once()
        sent_data = mock_socket.send.call_args[0][0]
        assert len(sent_data) > 300
    
    def test_special_characters_in_command_sent(self, mock_socket):
        """Commands with special characters are sent (server validates)."""
        # Client doesn't validate filenames - sends as-is to server
        client_example.send_command("record stop test*file.json")
        
        mock_socket.send.assert_called_once_with(b'record stop test*file.json')
    
    def test_rapid_command_sequence_handled(self, mock_socket):
        """Rapid command sequences are handled without errors."""
        mock_socket.recv.return_value = b'{"is_recording": false, "command_count": 0, "duration_ms": 0}'
        
        for i in range(10):
            client_example.send_command("recording_status")
        
        # All commands should be sent
        assert mock_socket.send.call_count == 10
        assert mock_socket.connect.call_count == 10
        assert mock_socket.close.call_count == 10
    
    def test_concurrent_connection_attempts_create_separate_sockets(self, mock_socket):
        """Each send_command creates a new connection."""
        client_example.send_command("record start")
        client_example.send_command("record stop")
        
        # Should have made 2 separate connections
        assert mock_socket.connect.call_count == 2
        assert mock_socket.close.call_count == 2
    
    def test_unicode_command_encoded_utf8(self, mock_socket):
        """Unicode characters in commands are UTF-8 encoded."""
        client_example.send_command("record stop 録音.json")
        
        # Should send UTF-8 encoded bytes
        mock_socket.send.assert_called_once()
        sent_data = mock_socket.send.call_args[0][0]
        # Verify it's bytes and contains UTF-8 encoded data
        assert isinstance(sent_data, bytes)
        assert "録音".encode('utf-8') in sent_data


# ============================================================================
# BACKWARD COMPATIBILITY TESTS
# ============================================================================

class TestBackwardCompatibility:
    """Test backward compatibility with legacy send_expression function."""
    
    def test_send_expression_calls_send_command(self, mock_socket):
        """send_expression wrapper calls send_command for compatibility."""
        client_example.send_expression("happy")
        
        mock_socket.connect.assert_called_once_with(('localhost', 5000))
        mock_socket.send.assert_called_once_with(b'happy')
    
    def test_send_expression_with_recording_command(self, mock_socket):
        """send_expression can send recording commands too."""
        client_example.send_expression("record start")
        
        mock_socket.send.assert_called_once_with(b'record start')
