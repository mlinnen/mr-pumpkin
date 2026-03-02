"""
Integration-style test suite for skill/ package — Generator + Uploader pipeline (Issue #39)

Tests generator and uploader working together with all external dependencies mocked.
Validates end-to-end flow from natural language prompt to successful server upload.

Author: Mylo (Tester)
Date: 2026-03-02
Issue: #39 — Mr. Pumpkin Recording Skill
"""

# TODO: adjust imports once skill/ package is finalized

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Deferred imports — skill/ package not yet created
try:
    from skill.generator import generate_timeline
    from skill.uploader import upload_timeline
    SKILL_AVAILABLE = True
except ImportError:
    SKILL_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not SKILL_AVAILABLE,
    reason="skill/ package not yet created — anticipatory tests for Issue #39"
)


# ============================================================================
# SHARED FIXTURES
# ============================================================================

@pytest.fixture
def valid_timeline_dict():
    """Canonical valid timeline as returned by a well-behaved LLM."""
    return {
        "version": "1.0",
        "duration_ms": 3000,
        "commands": [
            {"time_ms": 0, "command": "set_expression", "args": {"expression": "surprised"}},
            {"time_ms": 500, "command": "blink"},
            {"time_ms": 1000, "command": "set_expression", "args": {"expression": "happy"}},
            {"time_ms": 2000, "command": "wink_left"},
            {"time_ms": 3000, "command": "set_expression", "args": {"expression": "neutral"}},
        ]
    }


@pytest.fixture
def mock_llm_provider(valid_timeline_dict):
    """Mock LLM provider that returns valid timeline JSON."""
    provider = Mock()
    provider.generate.return_value = json.dumps(valid_timeline_dict)
    return provider


def _make_tcp_socket(recv_responses):
    """Helper: build a mock socket with pre-set recv responses."""
    sock = MagicMock()
    sock.recv.side_effect = [
        r if isinstance(r, bytes) else r.encode()
        for r in recv_responses
    ]
    return sock


def _patch_tcp(recv_responses):
    """Context helper: patch skill.uploader.socket.socket with mock responses."""
    return patch("skill.uploader.socket.socket")


# ============================================================================
# FULL PIPELINE TESTS
# ============================================================================

class TestFullPipeline:
    """Natural language → mock LLM → valid timeline → mock TCP upload → success."""

    def test_full_pipeline_prompt_to_upload(self, mock_llm_provider):
        """
        Full pipeline: prompt → generate_timeline() → upload_timeline() → None.

        This is the primary happy-path integration test. Every external call
        (LLM API and TCP socket) is mocked — no real network activity occurs.
        """
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = _make_tcp_socket([b"READY\n", b"OK Uploaded sunrise.json\n"])
            MockSocket.return_value = sock

            # Step 1: generate
            timeline = generate_timeline(
                "make the pumpkin look surprised, blink, smile, wink, then go neutral",
                provider=mock_llm_provider,
            )

            # Step 2: upload
            result = upload_timeline("sunrise", timeline, protocol="tcp")

        assert timeline is not None
        assert result is None

    def test_pipeline_produces_valid_timeline_structure(self, mock_llm_provider):
        """Generated timeline dict has the required schema fields before upload."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = _make_tcp_socket([b"READY\n", b"OK Uploaded test.json\n"])
            MockSocket.return_value = sock

            timeline = generate_timeline("blink twice", provider=mock_llm_provider)

            assert "version" in timeline
            assert timeline["version"] == "1.0"
            assert "duration_ms" in timeline
            assert isinstance(timeline["duration_ms"], int)
            assert "commands" in timeline
            assert isinstance(timeline["commands"], list)
            assert len(timeline["commands"]) > 0

    def test_pipeline_json_uploaded_to_server_is_valid(self, mock_llm_provider):
        """JSON bytes sent to the TCP server are valid parseable JSON."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = _make_tcp_socket([b"READY\n", b"OK Uploaded check.json\n"])
            MockSocket.return_value = sock

            timeline = generate_timeline("happy dance", provider=mock_llm_provider)
            upload_timeline("check", timeline, protocol="tcp")

            all_sent = b"".join(c[0][0] for c in sock.sendall.call_args_list)
            # Extract JSON portion (everything between first { and last })
            start = all_sent.find(b"{")
            end = all_sent.rfind(b"}") + 1
            assert start != -1 and end > start, "No JSON braces found in sent data"
            json_bytes = all_sent[start:end]
            parsed = json.loads(json_bytes)
            assert parsed["version"] == "1.0"

    def test_llm_provider_called_exactly_once_per_generate(self, mock_llm_provider):
        """LLM provider is called exactly once per generate_timeline() call."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = _make_tcp_socket([b"READY\n", b"OK Uploaded once.json\n"])
            MockSocket.return_value = sock

            generate_timeline("blink", provider=mock_llm_provider)

        mock_llm_provider.generate.assert_called_once()

    def test_filename_passed_to_upload_appears_in_tcp_handshake(self, mock_llm_provider):
        """The filename supplied to upload_timeline appears in the TCP upload command."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = _make_tcp_socket([b"READY\n", b"OK Uploaded spooky_dance.json\n"])
            MockSocket.return_value = sock

            timeline = generate_timeline("spooky dance", provider=mock_llm_provider)
            upload_timeline("spooky_dance", timeline, protocol="tcp")

            all_sent = b"".join(c[0][0] for c in sock.sendall.call_args_list)
            assert b"spooky_dance" in all_sent


# ============================================================================
# GENERATE SUCCEEDS, UPLOAD FAILS
# ============================================================================

class TestGenerateSucceedsUploadFails:
    """Error from uploader propagates clearly to the caller."""

    def test_upload_error_propagates_as_value_error(self, mock_llm_provider):
        """Generator succeeds but uploader raises → ValueError propagates."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = _make_tcp_socket([b"READY\n", b"ERROR: disk full\n"])
            MockSocket.return_value = sock

            timeline = generate_timeline("blink", provider=mock_llm_provider)

            with pytest.raises(ValueError):
                upload_timeline("fail_test", timeline, protocol="tcp")

    def test_upload_connection_error_propagates(self, mock_llm_provider):
        """Generator succeeds but TCP connection fails → OSError propagates."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = MagicMock()
            MockSocket.return_value = sock
            sock.connect.side_effect = ConnectionRefusedError("No server running")

            timeline = generate_timeline("blink", provider=mock_llm_provider)

            with pytest.raises((ConnectionError, OSError)):
                upload_timeline("conn_fail", timeline, protocol="tcp")

    def test_generate_result_not_mutated_on_upload_failure(self, mock_llm_provider):
        """Timeline dict returned by generator is not modified if upload fails."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = _make_tcp_socket([b"READY\n", b"ERROR: whatever\n"])
            MockSocket.return_value = sock

            timeline = generate_timeline("blink", provider=mock_llm_provider)
            original_commands = list(timeline["commands"])

            try:
                upload_timeline("mutate_test", timeline, protocol="tcp")
            except ValueError:
                pass

            assert timeline["commands"] == original_commands


# ============================================================================
# DUPLICATE FILENAME TESTS
# ============================================================================

class TestDuplicateFilename:
    """Uploading a timeline with an already-existing name raises ValueError."""

    def test_duplicate_filename_raises_value_error(self, mock_llm_provider):
        """Server reports timeline already exists → ValueError with informative message."""
        with patch("skill.uploader.socket.socket") as MockSocket:
            sock = _make_tcp_socket([
                b"READY\n",
                b"ERROR: timeline 'my_animation' already exists\n"
            ])
            MockSocket.return_value = sock

            timeline = generate_timeline("blink and smile", provider=mock_llm_provider)

            with pytest.raises(ValueError) as exc_info:
                upload_timeline("my_animation", timeline, protocol="tcp")

            error_text = str(exc_info.value).lower()
            assert "my_animation" in error_text or "already exists" in error_text or "duplicate" in error_text

    def test_duplicate_error_does_not_overwrite(self, mock_llm_provider):
        """On duplicate error, the uploader must NOT retry with a different name automatically."""
        upload_call_count = [0]

        with patch("skill.uploader.socket.socket") as MockSocket:
            def make_sock(*args, **kwargs):
                sock = MagicMock()
                upload_call_count[0] += 1
                sock.recv.side_effect = [
                    b"READY\n",
                    b"ERROR: timeline 'dup_test' already exists\n"
                ]
                return sock

            MockSocket.side_effect = make_sock

            timeline = generate_timeline("blink", provider=mock_llm_provider)

            with pytest.raises(ValueError):
                upload_timeline("dup_test", timeline, protocol="tcp")

        # Uploader should attempt exactly once — no silent retry
        assert upload_call_count[0] == 1

    def test_two_different_names_both_succeed(self, mock_llm_provider):
        """Two separate uploads with different names both succeed independently."""
        for filename, response in [
            ("animation_a", b"OK Uploaded animation_a.json\n"),
            ("animation_b", b"OK Uploaded animation_b.json\n"),
        ]:
            with patch("skill.uploader.socket.socket") as MockSocket:
                sock = _make_tcp_socket([b"READY\n", response])
                MockSocket.return_value = sock

                timeline = generate_timeline("blink", provider=mock_llm_provider)
                result = upload_timeline(filename, timeline, protocol="tcp")

            assert result is None
