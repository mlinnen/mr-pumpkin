"""
Test suite for the `help` command (Issue #56).

Tests validate that the `help` command sent over TCP or WebSockets returns
a list of all commands with syntax for each.

PROVISIONAL: Vi has not yet landed the help command implementation.
These tests are written against the expected interface. Once the implementation
lands in command_handler.py, run `python -m pytest tests/test_help_command.py -v`
to verify all pass.

Expected interface:
  - router.execute("help") returns a non-empty string
  - The response is valid JSON (dict with command entries) OR a structured plain-text string
  - Every known command name appears in the response
  - Argument/syntax info is present (e.g., filenames, angles, magnitudes)
  - Command is case-insensitive (matches existing strip().lower() normalization)
  - Extra leading/trailing whitespace is tolerated (strip() handles this already)

Author: Mylo (Tester)
Issue: #56
Date: 2026-03-04
"""

import json
import pygame
import pytest
from pumpkin_face import PumpkinFace, Expression
from command_handler import CommandRouter


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pumpkin():
    """Create a PumpkinFace instance for testing."""
    pygame.init()
    face = PumpkinFace(width=1920, height=1080)
    yield face
    pygame.quit()


@pytest.fixture
def router(pumpkin):
    """Create a CommandRouter for testing command execution."""
    return CommandRouter(pumpkin, Expression)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _response_text(router) -> str:
    """Return the help response as a plain string."""
    return router.execute("help")


def _try_parse_json(text: str):
    """Return parsed JSON object or None if text is not JSON."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


# ---------------------------------------------------------------------------
# 1. Non-empty response
# ---------------------------------------------------------------------------

class TestHelpResponseExists:
    """The help command must return a non-empty, non-None response."""

    # PROVISIONAL: requires Vi's implementation
    def test_help_returns_non_empty_string(self, router):
        """help command must return a non-empty string."""
        response = router.execute("help")
        assert response is not None, "help must return a response, not None"
        assert isinstance(response, str), "help response must be a string"
        assert len(response.strip()) > 0, "help response must not be empty"

    # PROVISIONAL
    def test_help_response_length_reasonable(self, router):
        """help response should be long enough to contain meaningful content."""
        response = router.execute("help")
        # Must be more than just "OK" or a one-word reply
        assert len(response) > 20, (
            f"help response is too short ({len(response)} chars); "
            "expected a list of commands with syntax"
        )


# ---------------------------------------------------------------------------
# 2. Response contains known command names
# ---------------------------------------------------------------------------

class TestHelpContainsCommandNames:
    """The help response must reference every key command by name."""

    # PROVISIONAL
    @pytest.mark.parametrize("command_name", [
        "play",
        "stop",
        "pause",
        "resume",
        "seek",
        "record_start",
        "record_stop",
        "record_cancel",
        "blink",
        "gaze",
        "help",
    ])
    def test_help_mentions_command(self, router, command_name):
        """help response must mention the command name '{command_name}'."""
        response = router.execute("help").lower()
        assert command_name in response, (
            f"help response does not mention command '{command_name}'"
        )

    # PROVISIONAL
    def test_help_mentions_expression_commands(self, router):
        """help response should reference expression/animation commands."""
        response = router.execute("help").lower()
        # At least one of the common expression names must appear
        expression_commands = ["happy", "sad", "neutral", "angry", "expression"]
        assert any(cmd in response for cmd in expression_commands), (
            "help response should mention expression commands "
            f"(checked: {expression_commands})"
        )


# ---------------------------------------------------------------------------
# 3. Response contains syntax / argument info
# ---------------------------------------------------------------------------

class TestHelpContainsSyntaxInfo:
    """The help response must convey argument/syntax information."""

    # PROVISIONAL
    def test_help_contains_argument_indicators(self, router):
        """help response should contain argument placeholder indicators."""
        response = router.execute("help")
        # Common ways to indicate arguments: <filename>, [amount], angle, ms, etc.
        syntax_hints = ["<", "[", "filename", "ms", "angle", "magnitude", ":"]
        assert any(hint in response.lower() for hint in syntax_hints), (
            "help response should contain syntax/argument info "
            f"(looked for any of: {syntax_hints})"
        )

    # PROVISIONAL
    def test_help_play_syntax_includes_filename(self, router):
        """help response for 'play' should indicate a filename is required."""
        response = router.execute("help").lower()
        play_idx = response.find("play")
        assert play_idx != -1, "play command not found in help response"

        # The word 'filename' or a placeholder should appear somewhere near 'play'
        # or anywhere in the document (sufficient for a general help listing)
        assert "filename" in response or "<" in response, (
            "help response should indicate that 'play' requires a filename argument"
        )

    # PROVISIONAL
    def test_help_gaze_syntax_includes_angle_or_args(self, router):
        """help response for 'gaze' should indicate angle/numeric arguments."""
        response = router.execute("help").lower()
        assert "gaze" in response, "gaze not found in help response"

        numeric_hints = ["angle", "deg", "°", "<", "arg", "0", "float", "int"]
        assert any(h in response for h in numeric_hints), (
            "help response should indicate numeric arguments for 'gaze'"
        )


# ---------------------------------------------------------------------------
# 4. Response format is valid
# ---------------------------------------------------------------------------

class TestHelpResponseFormat:
    """The help response must use a consistent, parseable format."""

    # PROVISIONAL
    def test_help_response_is_json_or_structured_text(self, router):
        """help response must be valid JSON or structured plain text (not garbage)."""
        response = router.execute("help")
        parsed = _try_parse_json(response)

        if parsed is not None:
            # JSON path: must be a dict or list, not a scalar
            assert isinstance(parsed, (dict, list)), (
                "If help returns JSON, it must be a dict or list, "
                f"got {type(parsed).__name__}"
            )
        else:
            # Plain-text path: must contain at least one newline or colon
            # indicating structure (not a single unformatted blob)
            assert "\n" in response or ":" in response, (
                "If help returns plain text, it must be structured "
                "(contain newlines or colons)"
            )

    # PROVISIONAL
    def test_help_json_if_json_has_command_entries(self, router):
        """If help returns JSON, each entry should have a name and description/syntax."""
        response = router.execute("help")
        parsed = _try_parse_json(response)

        if parsed is None:
            pytest.skip("help does not return JSON — skipping JSON-specific test")

        if isinstance(parsed, dict):
            # Expect { "command_name": "syntax or description", ... }
            # or { "commands": [...] }
            assert len(parsed) > 0, "JSON help response dict must not be empty"
        elif isinstance(parsed, list):
            assert len(parsed) > 0, "JSON help response list must not be empty"
            # Each entry should be a dict with at least a 'name' key
            if isinstance(parsed[0], dict):
                assert "name" in parsed[0] or "command" in parsed[0], (
                    "JSON help list entries should have a 'name' or 'command' key"
                )


# ---------------------------------------------------------------------------
# 5. Case / whitespace variations
# ---------------------------------------------------------------------------

class TestHelpCaseAndWhitespace:
    """help command should be case-insensitive and whitespace-tolerant."""

    # PROVISIONAL
    def test_help_uppercase(self, router):
        """HELP (uppercase) should return the same response as help."""
        lower_response = router.execute("help")
        upper_response = router.execute("HELP")
        assert upper_response == lower_response, (
            "HELP and help should return identical responses"
        )

    # PROVISIONAL
    def test_help_mixed_case(self, router):
        """HeLp (mixed case) should return the same response as help."""
        lower_response = router.execute("help")
        mixed_response = router.execute("HeLp")
        assert mixed_response == lower_response, (
            "HeLp and help should return identical responses"
        )

    # PROVISIONAL
    def test_help_leading_whitespace(self, router):
        """'  help' with leading whitespace should work (strip() normalizes it)."""
        normal = router.execute("help")
        padded = router.execute("  help")
        assert padded == normal, (
            "Leading whitespace should be stripped; '  help' == 'help'"
        )

    # PROVISIONAL
    def test_help_trailing_whitespace(self, router):
        """'help  ' with trailing whitespace should work."""
        normal = router.execute("help")
        padded = router.execute("help  ")
        assert padded == normal, (
            "Trailing whitespace should be stripped; 'help  ' == 'help'"
        )

    # PROVISIONAL
    def test_help_leading_and_trailing_whitespace(self, router):
        """'  help  ' with surrounding whitespace should work."""
        normal = router.execute("help")
        padded = router.execute("  help  ")
        assert padded == normal, (
            "Surrounding whitespace should be stripped; '  help  ' == 'help'"
        )


# ---------------------------------------------------------------------------
# 6. Edge cases
# ---------------------------------------------------------------------------

class TestHelpEdgeCases:
    """Edge cases: help with subcommand arguments, repeated calls, etc."""

    # PROVISIONAL
    def test_help_with_known_subcommand_does_not_crash(self, router):
        """'help play' should return a response without raising an exception."""
        response = router.execute("help play")
        assert response is not None, "'help play' must return a response"
        assert isinstance(response, str), "'help play' response must be a string"

    # PROVISIONAL
    def test_help_with_unknown_subcommand_does_not_crash(self, router):
        """'help nonexistent_cmd' should return a response, not crash."""
        response = router.execute("help nonexistent_cmd")
        assert response is not None, "'help nonexistent_cmd' must not crash"
        assert isinstance(response, str), "response must be a string"

    # PROVISIONAL
    def test_help_with_unknown_subcommand_indicates_error_or_general_help(self, router):
        """'help unknown' should return ERROR or fall back to general help."""
        response = router.execute("help unknown_xyz_command")
        # Either an error message or the full help listing is acceptable
        is_error = response.startswith("ERROR") or "unknown" in response.lower() or "not found" in response.lower()
        is_general_help = len(response) > 20  # long enough to be the full listing
        assert is_error or is_general_help, (
            "help with an unknown subcommand should return ERROR or full help listing"
        )

    # PROVISIONAL
    def test_help_is_idempotent(self, router):
        """Calling help multiple times returns the same response each time."""
        first = router.execute("help")
        second = router.execute("help")
        third = router.execute("help")
        assert first == second == third, (
            "help must return identical responses on repeated calls"
        )

    # PROVISIONAL
    def test_help_does_not_change_pumpkin_state(self, router, pumpkin):
        """Calling help must not alter the pumpkin's expression or playback state."""
        initial_expression = pumpkin.current_expression
        initial_recording = pumpkin.recording_session.is_recording
        initial_playback = pumpkin.timeline_playback.state.value

        router.execute("help")

        assert pumpkin.current_expression == initial_expression, (
            "help must not change the current expression"
        )
        assert pumpkin.recording_session.is_recording == initial_recording, (
            "help must not start or stop a recording"
        )
        assert pumpkin.timeline_playback.state.value == initial_playback, (
            "help must not change playback state"
        )
