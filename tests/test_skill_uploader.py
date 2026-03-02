"""
Test suite for skill/uploader.py — Timeline Upload Client (Issue #39)

Tests upload_timeline() via TCP and WebSocket protocols using mocked connections.
Validates success, error, duplicate, timeout, and protocol-selection behaviors.

Author: Mylo (Tester)
Date: 2026-03-02
Issue: #39 — Mr. Pumpkin Recording Skill
"""

# TODO: adjust imports once skill/ package is finalized

import pytest
import json
import os
import socket
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Deferred import — skill/ package not yet created
try:
    from skill.uploader import upload_timeline
    SKILL_AVAILABLE = True
except ImportError:
    SKILL_AVAILABLE = False

# WebSocket support is optional
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not SKILL_AVAILABLE,
    reason="skill/ package not yet created — anticipatory tests for Issue #39"
)


# ============================================================================
# SHARED FIXTURES
# ============================================================================

@pytest.fixture
def sample_timeline():
    """Minimal valid timeline dict for upload tests."""
    return {
        "version": "1.0",
        "duration_ms": 2000,
        "commands": [
            {"time_ms": 0, "command": "set_expression", "args": {"expression": "happy"}},
            {"time_ms": 1000, "command": "blink"},
            {"time_ms": 2000, "command": "set_expression", "args": {"expression": "neutral"}},
        ]
    }


@pytest.fixture
def mock_socket_factory():
    """
    Factory fixture: returns a function that creates a pre-configured mock socket.
    Call with recv_responses=[b'READY', b'OK Uploaded foo.json'] to simulate conversation.
    """
    def _make(recv_responses=None):
        sock = MagicMock()
        if recv_responses:
            sock.recv.side_effect = [r if isinstance(r, bytes) else r.encode() for r in recv_responses]
        return sock
    return _make


# ============================================================================
# TCP HAPPY PATH TESTS
# ============================================================================

class TestTCPHappyPath:
    """TCP upload succeeds end-to-end with proper handshake."""

    def test_tcp_upload_returns_none_on_success(self, sample_timeline):
        """Successful TCP upload returns None (no return value needed)."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            # _recv_line reads chunks until it finds a newline
            sock.recv.side_effect = [b"READY\n", b"OK Uploaded foo.json\n"]

            result = upload_timeline("foo", sample_timeline, protocol="tcp")

            assert result is None

    def test_tcp_sends_upload_command_first(self, sample_timeline):
        """First message sent to server is 'upload_timeline <filename>'."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"OK Uploaded foo.json\n"]

            upload_timeline("foo", sample_timeline, protocol="tcp")

            first_send = sock.sendall.call_args_list[0]
            sent_bytes = first_send[0][0]
            assert b"upload_timeline" in sent_bytes
            assert b"foo" in sent_bytes

    def test_tcp_sends_json_content_after_ready(self, sample_timeline):
        """After READY response, JSON content is sent over the socket."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"OK Uploaded foo.json\n"]

            upload_timeline("foo", sample_timeline, protocol="tcp")

            all_sent = b"".join(c[0][0] for c in sock.sendall.call_args_list)
            assert b'"version"' in all_sent
            assert b'"commands"' in all_sent

    def test_tcp_sends_end_upload_marker(self, sample_timeline):
        """END_UPLOAD marker is sent to terminate the upload."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"OK Uploaded foo.json\n"]

            upload_timeline("foo", sample_timeline, protocol="tcp")

            all_sent = b"".join(c[0][0] for c in sock.sendall.call_args_list)
            assert b"END_UPLOAD" in all_sent

    def test_tcp_connects_to_correct_default_host_port(self, sample_timeline):
        """TCP connects to localhost:5000 by default."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"OK Uploaded foo.json\n"]

            upload_timeline("foo", sample_timeline, protocol="tcp")

            sock.connect.assert_called_once()
            host, port = sock.connect.call_args[0][0]
            assert host == "localhost"
            assert port == 5000


# ============================================================================
# TCP DUPLICATE ERROR TESTS
# ============================================================================

class TestTCPDuplicateError:
    """TCP upload raises ValueError when server reports duplicate timeline."""

    def test_duplicate_timeline_raises_value_error(self, sample_timeline):
        """Server responds 'ERROR: timeline already exists' → ValueError raised."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"ERROR: timeline 'foo' already exists\n"]

            with pytest.raises(ValueError):
                upload_timeline("foo", sample_timeline, protocol="tcp")

    def test_duplicate_error_message_is_informative(self, sample_timeline):
        """ValueError message for duplicate includes the filename."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"ERROR: timeline 'foo' already exists\n"]

            with pytest.raises(ValueError) as exc_info:
                upload_timeline("foo", sample_timeline, protocol="tcp")

            assert "foo" in str(exc_info.value) or "already exists" in str(exc_info.value)


# ============================================================================
# TCP GENERIC ERROR TESTS
# ============================================================================

class TestTCPGenericError:
    """TCP upload raises ValueError on any ERROR response from server."""

    def test_generic_server_error_raises_value_error(self, sample_timeline):
        """Server responds 'ERROR: ...' (any kind) → ValueError raised."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"ERROR: invalid JSON structure\n"]

            with pytest.raises(ValueError):
                upload_timeline("foo", sample_timeline, protocol="tcp")

    def test_error_prefix_in_response_always_raises(self, sample_timeline):
        """Any response starting with ERROR triggers ValueError."""
        error_responses = [
            b"ERROR: disk full\n",
            b"ERROR: permission denied\n",
            b"ERROR: unknown format\n",
        ]
        for error_response in error_responses:
            with patch("skill.uploader.socket.socket") as MockSocket:
                sock = MagicMock()
                MockSocket.return_value = sock
                sock.recv.side_effect = [b"READY\n", error_response]

                with pytest.raises(ValueError):
                    upload_timeline("foo", sample_timeline, protocol="tcp")


# ============================================================================
# TCP CONNECTION FAILURE TESTS
# ============================================================================

class TestTCPConnectionFailure:
    """TCP upload raises appropriate error when connection cannot be established."""

    def test_connection_refused_raises_error(self, sample_timeline):
        """Socket connection refused → ConnectionError or OSError raised."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.connect.side_effect = ConnectionRefusedError("Connection refused")

            with pytest.raises((ConnectionError, OSError)):
                upload_timeline("foo", sample_timeline, protocol="tcp")

    def test_network_unreachable_raises_error(self, sample_timeline):
        """Network unreachable → OSError raised."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.connect.side_effect = OSError("Network unreachable")

            with pytest.raises(OSError):
                upload_timeline("foo", sample_timeline, protocol="tcp")


# ============================================================================
# TCP TIMEOUT TESTS
# ============================================================================

class TestTCPTimeout:
    """TCP upload raises error when server is unresponsive."""

    def test_recv_timeout_raises_error(self, sample_timeline):
        """Server never responds (recv times out) → timeout error raised."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = socket.timeout("timed out")

            with pytest.raises((socket.timeout, TimeoutError, OSError)):
                upload_timeline("foo", sample_timeline, protocol="tcp")

    def test_no_ready_response_does_not_hang_indefinitely(self, sample_timeline):
        """If READY is never received, upload raises an error (not infinite wait)."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            # Simulate server sending garbage instead of READY
            sock.recv.return_value = b"UNKNOWN RESPONSE\n"

            with pytest.raises(Exception):
                upload_timeline("foo", sample_timeline, protocol="tcp")


# ============================================================================
# WEBSOCKET HAPPY PATH TESTS
# ============================================================================

class TestWebSocketHappyPath:
    """WebSocket upload succeeds with single-message protocol."""

    @pytest.mark.skipif(not WEBSOCKETS_AVAILABLE, reason="websockets not installed")
    def test_websocket_upload_returns_none_on_success(self, sample_timeline):
        """Successful WebSocket upload returns None."""
        with patch("skill.uploader._upload_ws") as mock_ws_upload:
            mock_ws_upload.return_value = None
            result = upload_timeline("foo", sample_timeline, protocol="websocket")

        assert result is None

    @pytest.mark.skipif(not WEBSOCKETS_AVAILABLE, reason="websockets not installed")
    def test_websocket_sends_single_message_with_json(self, sample_timeline):
        """WebSocket upload function is called with filename and JSON string."""
        with patch("skill.uploader._upload_ws") as mock_ws_upload:
            mock_ws_upload.return_value = None
            upload_timeline("foo", sample_timeline, protocol="websocket")

        mock_ws_upload.assert_called_once()
        call_args = mock_ws_upload.call_args
        # _upload_ws(filename, json_string, host, port)
        filename_arg = call_args[0][0]
        json_arg = call_args[0][1]
        assert filename_arg == "foo"
        parsed = json.loads(json_arg)
        assert parsed["version"] == "1.0"


# ============================================================================
# WEBSOCKET ERROR TESTS
# ============================================================================

class TestWebSocketErrors:
    """WebSocket upload raises ValueError on server error responses."""

    @pytest.mark.skipif(not WEBSOCKETS_AVAILABLE, reason="websockets not installed")
    def test_websocket_error_response_raises_value_error(self, sample_timeline):
        """WebSocket server responds ERROR → ValueError raised."""
        with patch("skill.uploader._upload_ws") as mock_ws_upload:
            mock_ws_upload.side_effect = ValueError("ERROR: timeline 'foo' already exists")
            with pytest.raises(ValueError):
                upload_timeline("foo", sample_timeline, protocol="websocket")


# ============================================================================
# NO AUTOPLAY TESTS
# ============================================================================

class TestNoAutoplay:
    """After upload, no play command is automatically sent."""

    def test_no_play_command_sent_after_tcp_upload(self, sample_timeline):
        """Successful TCP upload does NOT send a 'play' command."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"OK Uploaded foo.json\n"]

            upload_timeline("foo", sample_timeline, protocol="tcp")

            all_sent = b"".join(c[0][0] for c in sock.sendall.call_args_list)
            assert b"play" not in all_sent

    @pytest.mark.skipif(not WEBSOCKETS_AVAILABLE, reason="websockets not installed")
    def test_no_play_command_sent_after_websocket_upload(self, sample_timeline):
        """Successful WebSocket upload does NOT send a 'play' command."""
        with patch("skill.uploader._upload_ws") as mock_ws_upload:
            mock_ws_upload.return_value = None
            upload_timeline("foo", sample_timeline, protocol="websocket")

        mock_ws_upload.assert_called_once()
        # The websocket upload helper is called once and only once (no play command)
        assert mock_ws_upload.call_count == 1


# ============================================================================
# PROTOCOL DEFAULT TESTS
# ============================================================================

class TestProtocolDefault:
    """Default protocol is TCP when not specified."""

    def test_default_protocol_is_tcp(self, sample_timeline):
        """Calling upload_timeline without protocol= uses TCP (port 5000)."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"OK Uploaded foo.json\n"]

            upload_timeline("foo", sample_timeline)  # No protocol arg

            sock.connect.assert_called_once()
            _, port = sock.connect.call_args[0][0]
            assert port == 5000


# ============================================================================
# CUSTOM HOST/PORT TESTS
# ============================================================================

class TestCustomHostPort:
    """Custom host and port are passed through to the socket connection."""

    def test_custom_host_used_for_tcp_connection(self, sample_timeline):
        """Non-default host is passed to socket.connect."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"OK Uploaded foo.json\n"]

            upload_timeline("foo", sample_timeline, host="192.168.1.100", protocol="tcp")

            sock.connect.assert_called_once()
            host, _ = sock.connect.call_args[0][0]
            assert host == "192.168.1.100"

    def test_custom_port_used_for_tcp_connection(self, sample_timeline):
        """Non-default port is passed to socket.connect."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"OK Uploaded foo.json\n"]

            upload_timeline("foo", sample_timeline, tcp_port=9999, protocol="tcp")

            sock.connect.assert_called_once()
            _, port = sock.connect.call_args[0][0]
            assert port == 9999

    def test_custom_host_and_port_both_applied(self, sample_timeline):
        """Both custom host and custom port are used together."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.recv.side_effect = [b"READY\n", b"OK Uploaded foo.json\n"]

            upload_timeline("foo", sample_timeline, host="10.0.0.1", tcp_port=5050, protocol="tcp")

            sock.connect.assert_called_once()
            host, port = sock.connect.call_args[0][0]
            assert host == "10.0.0.1"
            assert port == 5050
