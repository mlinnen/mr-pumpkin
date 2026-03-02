"""
Test suite for skill/generator.py — Prompt-to-Timeline Generator (Issue #39)

Tests the generate_timeline() function using mocked LLM providers.
Validates happy paths, repair heuristics, code fence stripping, and error cases.

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

# Deferred import — skill/ package not yet created
try:
    from skill.generator import generate_timeline, GeminiProvider, LLMProvider
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
    """Canonical valid timeline JSON dict (matches timeline.py schema)."""
    return {
        "version": "1.0",
        "duration_ms": 3000,
        "commands": [
            {"time_ms": 0, "command": "set_expression", "args": {"expression": "neutral"}},
            {"time_ms": 500, "command": "blink"},
            {"time_ms": 1000, "command": "set_expression", "args": {"expression": "happy"}},
            {"time_ms": 2000, "command": "gaze", "args": {"x": 45.0, "y": 0.0}},
            {"time_ms": 3000, "command": "set_expression", "args": {"expression": "neutral"}},
        ]
    }


@pytest.fixture
def mock_provider(valid_timeline_dict):
    """Mock LLMProvider that returns valid timeline JSON."""
    provider = Mock()
    provider.generate.return_value = json.dumps(valid_timeline_dict)
    return provider


# ============================================================================
# HAPPY PATH TESTS
# ============================================================================

class TestHappyPath:
    """Generator returns validated dict when LLM output is well-formed."""

    def test_valid_json_returns_dict(self, mock_provider, valid_timeline_dict):
        """Mock LLM returns valid JSON → generator returns validated dict."""
        result = generate_timeline("make the pumpkin blink and smile", provider=mock_provider)

        assert isinstance(result, dict)
        assert result["version"] == "1.0"
        assert "commands" in result
        assert "duration_ms" in result

    def test_provider_is_called_with_prompt(self, mock_provider):
        """Provider.generate() is called and receives the user prompt."""
        prompt = "pumpkin looks surprised then blinks"
        generate_timeline(prompt, provider=mock_provider)

        mock_provider.generate.assert_called_once()
        call_args = mock_provider.generate.call_args
        # Prompt must appear somewhere in what is sent to the provider
        assert any(prompt in str(arg) for arg in call_args.args + tuple(call_args.kwargs.values()))

    def test_returned_dict_has_required_fields(self, mock_provider):
        """Returned dict always includes version, duration_ms, and commands."""
        result = generate_timeline("blink twice", provider=mock_provider)

        assert "version" in result
        assert "duration_ms" in result
        assert "commands" in result

    def test_returned_commands_are_list(self, mock_provider):
        """commands field is a list of dicts."""
        result = generate_timeline("neutral face", provider=mock_provider)

        assert isinstance(result["commands"], list)
        for cmd in result["commands"]:
            assert isinstance(cmd, dict)
            assert "time_ms" in cmd
            assert "command" in cmd


# ============================================================================
# REPAIR HEURISTIC TESTS
# ============================================================================

class TestRepairHeuristics:
    """Generator repairs known LLM output mistakes before validation."""

    def test_timestamp_ms_repaired_to_time_ms(self, valid_timeline_dict):
        """LLM uses timestamp_ms (wrong) → generator repairs to time_ms."""
        broken = dict(valid_timeline_dict)
        broken["commands"] = [
            {"timestamp_ms": 0, "command": "blink"},
            {"timestamp_ms": 500, "command": "set_expression", "args": {"expression": "happy"}},
        ]
        broken["duration_ms"] = 500

        provider = Mock()
        provider.generate.return_value = json.dumps(broken)

        result = generate_timeline("blink and smile", provider=provider)

        assert result is not None
        for cmd in result["commands"]:
            assert "time_ms" in cmd
            assert "timestamp_ms" not in cmd

    def test_repair_preserves_all_command_data(self, valid_timeline_dict):
        """Repair heuristic preserves command name and args during key rename."""
        broken = dict(valid_timeline_dict)
        broken["commands"] = [
            {"timestamp_ms": 100, "command": "gaze", "args": {"x": 30.0, "y": 15.0}},
        ]
        broken["duration_ms"] = 100

        provider = Mock()
        provider.generate.return_value = json.dumps(broken)

        result = generate_timeline("look left", provider=provider)

        cmd = result["commands"][0]
        assert cmd["time_ms"] == 100
        assert cmd["command"] == "gaze"
        assert cmd["args"]["x"] == 30.0
        assert cmd["args"]["y"] == 15.0


# ============================================================================
# CODE FENCE STRIPPING TESTS
# ============================================================================

class TestCodeFenceStripping:
    """Generator strips markdown code fences from LLM output."""

    def test_json_code_fence_stripped_and_parsed(self, valid_timeline_dict):
        """LLM wraps JSON in ```json ... ``` → generator strips and parses."""
        fenced = f"```json\n{json.dumps(valid_timeline_dict)}\n```"

        provider = Mock()
        provider.generate.return_value = fenced

        result = generate_timeline("happy pumpkin", provider=provider)

        assert result["version"] == "1.0"
        assert len(result["commands"]) > 0

    def test_plain_code_fence_stripped_and_parsed(self, valid_timeline_dict):
        """LLM wraps JSON in ``` ... ``` (no language tag) → stripped correctly."""
        fenced = f"```\n{json.dumps(valid_timeline_dict)}\n```"

        provider = Mock()
        provider.generate.return_value = fenced

        result = generate_timeline("neutral face", provider=provider)

        assert result["version"] == "1.0"

    def test_leading_trailing_whitespace_stripped(self, valid_timeline_dict):
        """Extra whitespace around JSON is stripped before parsing."""
        padded = f"\n\n   {json.dumps(valid_timeline_dict)}   \n\n"

        provider = Mock()
        provider.generate.return_value = padded

        result = generate_timeline("blink", provider=provider)

        assert result["version"] == "1.0"

    def test_explanatory_text_before_json_handled(self, valid_timeline_dict):
        """LLM adds prose before the JSON block → generator extracts JSON block."""
        with_prose = f"Here is the timeline:\n```json\n{json.dumps(valid_timeline_dict)}\n```"

        provider = Mock()
        provider.generate.return_value = with_prose

        result = generate_timeline("describe and blink", provider=provider)

        assert result["version"] == "1.0"


# ============================================================================
# INVALID COMMAND NAME TESTS
# ============================================================================

class TestInvalidCommandNames:
    """Generator raises ValueError when LLM produces unknown command names."""

    def test_unknown_command_raises_value_error(self):
        """LLM generates unknown command → ValueError raised with clear message."""
        bad_timeline = {
            "version": "1.0",
            "duration_ms": 500,
            "commands": [
                {"time_ms": 0, "command": "do_a_barrel_roll"},
            ]
        }

        provider = Mock()
        provider.generate.return_value = json.dumps(bad_timeline)

        with pytest.raises(ValueError, match=r"do_a_barrel_roll"):
            generate_timeline("barrel roll", provider=provider)

    def test_error_message_names_the_bad_command(self):
        """ValueError message identifies which command is invalid."""
        bad_timeline = {
            "version": "1.0",
            "duration_ms": 500,
            "commands": [
                {"time_ms": 0, "command": "fly_away"},
            ]
        }

        provider = Mock()
        provider.generate.return_value = json.dumps(bad_timeline)

        with pytest.raises(ValueError) as exc_info:
            generate_timeline("fly away", provider=provider)

        assert "fly_away" in str(exc_info.value)

    def test_valid_commands_do_not_raise(self, mock_provider, valid_timeline_dict):
        """All commands in the known vocabulary pass validation without error."""
        # Should not raise — all commands in valid_timeline_dict are known
        result = generate_timeline("wave and blink", provider=mock_provider)
        assert result is not None


# ============================================================================
# MISSING VERSION FIELD TESTS
# ============================================================================

class TestMissingVersionField:
    """Generator raises ValueError when LLM omits the version field."""

    def test_missing_version_raises_value_error(self):
        """LLM omits version field → ValueError raised."""
        no_version = {
            "duration_ms": 1000,
            "commands": [
                {"time_ms": 0, "command": "blink"},
            ]
        }

        provider = Mock()
        provider.generate.return_value = json.dumps(no_version)

        with pytest.raises(ValueError):
            generate_timeline("blink", provider=provider)

    def test_wrong_version_string_raises_value_error(self):
        """Version field set to unsupported value → ValueError raised."""
        wrong_version = {
            "version": "2.0",
            "duration_ms": 1000,
            "commands": [
                {"time_ms": 0, "command": "blink"},
            ]
        }

        provider = Mock()
        provider.generate.return_value = json.dumps(wrong_version)

        with pytest.raises(ValueError):
            generate_timeline("blink", provider=provider)

    def test_null_version_raises_value_error(self):
        """Version field is null → ValueError raised."""
        null_version = {
            "version": None,
            "duration_ms": 500,
            "commands": [{"time_ms": 0, "command": "blink"}]
        }

        provider = Mock()
        provider.generate.return_value = json.dumps(null_version)

        with pytest.raises(ValueError):
            generate_timeline("blink", provider=provider)


# ============================================================================
# EMPTY COMMANDS LIST TESTS
# ============================================================================

class TestEmptyCommandsList:
    """Generator behavior when LLM returns empty commands list."""

    def test_empty_commands_raises_value_error(self):
        """Valid structure but empty commands → ValueError (useless timeline)."""
        empty_cmds = {
            "version": "1.0",
            "duration_ms": 0,
            "commands": []
        }

        provider = Mock()
        provider.generate.return_value = json.dumps(empty_cmds)

        with pytest.raises(ValueError, match=r"[Ee]mpty|[Nn]o commands|[Cc]ommands"):
            generate_timeline("do nothing", provider=provider)


# ============================================================================
# UNSORTED TIME_MS TESTS
# ============================================================================

class TestUnsortedTimeMs:
    """Generator catches commands not in ascending time_ms order."""

    def test_unsorted_commands_raise_value_error(self):
        """Commands not in ascending time_ms order → ValueError raised."""
        unsorted = {
            "version": "1.0",
            "duration_ms": 2000,
            "commands": [
                {"time_ms": 1000, "command": "blink"},
                {"time_ms": 0, "command": "set_expression", "args": {"expression": "happy"}},
                {"time_ms": 500, "command": "wink_left"},
            ]
        }

        provider = Mock()
        provider.generate.return_value = json.dumps(unsorted)

        with pytest.raises(ValueError):
            generate_timeline("out of order", provider=provider)

    def test_sorted_commands_pass_validation(self, mock_provider):
        """Commands in ascending time_ms order pass validation."""
        result = generate_timeline("sorted animation", provider=mock_provider)
        times = [cmd["time_ms"] for cmd in result["commands"]]
        assert times == sorted(times)


# ============================================================================
# LLM PROVIDER INTERFACE TESTS
# ============================================================================

class TestLLMProviderInterface:
    """Custom providers are accepted and called correctly."""

    def test_custom_provider_is_called(self, valid_timeline_dict):
        """A custom mock provider (implementing LLMProvider) is called once."""
        custom_provider = Mock(spec=LLMProvider)
        custom_provider.generate.return_value = json.dumps(valid_timeline_dict)

        generate_timeline("test prompt", provider=custom_provider)

        custom_provider.generate.assert_called_once()

    def test_custom_provider_return_value_used(self, valid_timeline_dict):
        """Return value from custom provider is parsed as the timeline."""
        custom_provider = Mock(spec=LLMProvider)
        custom_provider.generate.return_value = json.dumps(valid_timeline_dict)

        result = generate_timeline("test prompt", provider=custom_provider)

        assert result["version"] == valid_timeline_dict["version"]
        assert len(result["commands"]) == len(valid_timeline_dict["commands"])

    def test_provider_exception_propagates(self):
        """If provider.generate() raises, the exception propagates to caller."""
        failing_provider = Mock()
        failing_provider.generate.side_effect = RuntimeError("LLM call failed")

        with pytest.raises(RuntimeError, match="LLM call failed"):
            generate_timeline("broken prompt", provider=failing_provider)

    def test_llmprovider_is_abstract_interface(self):
        """LLMProvider has a generate() method (interface contract)."""
        assert hasattr(LLMProvider, "generate"), "LLMProvider must define generate()"


# ============================================================================
# DEFAULT PROVIDER TESTS
# ============================================================================

class TestDefaultProvider:
    """When no provider is supplied, GeminiProvider is used."""

    def test_no_provider_uses_gemini(self):
        """Calling without provider= argument triggers GeminiProvider instantiation."""
        with patch("skill.generator.GeminiProvider") as MockGemini:
            instance = Mock()
            instance.generate.return_value = json.dumps({
                "version": "1.0",
                "duration_ms": 500,
                "commands": [{"time_ms": 0, "command": "blink"}]
            })
            MockGemini.return_value = instance

            with patch.dict(os.environ, {"GEMINI_API_KEY": "fake-key"}):
                generate_timeline("test")

            MockGemini.assert_called_once()

    def test_gemini_provider_instantiated_with_api_key(self):
        """GeminiProvider reads GEMINI_API_KEY from environment when instantiated."""
        # GeminiProvider takes no constructor args — reads from env internally.
        # When the key is present, it should not raise EnvironmentError.
        with patch("skill.generator.GeminiProvider") as MockGemini:
            instance = Mock()
            instance.generate.return_value = json.dumps({
                "version": "1.0",
                "duration_ms": 300,
                "commands": [{"time_ms": 0, "command": "blink"}]
            })
            MockGemini.return_value = instance

            with patch.dict(os.environ, {"GEMINI_API_KEY": "my-test-key"}):
                generate_timeline("test")

            MockGemini.assert_called_once()
            # GeminiProvider reads key from env, not from constructor args
            call_args = MockGemini.call_args
            assert call_args is not None  # was instantiated


# ============================================================================
# API KEY MISSING TESTS
# ============================================================================

class TestApiKeyMissing:
    """Clear error raised when GEMINI_API_KEY is not set."""

    def test_missing_api_key_raises_before_api_call(self):
        """GEMINI_API_KEY not set → error raised before making any API call."""
        # Remove key from environment
        env = {k: v for k, v in os.environ.items() if k not in ("GEMINI_API_KEY", "GOOGLE_API_KEY")}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises((ValueError, EnvironmentError, KeyError, RuntimeError, ImportError)):
                generate_timeline("test without key")

    def test_missing_api_key_error_message_is_descriptive(self):
        """Error message for missing API key mentions the key name or is actionable."""
        env = {k: v for k, v in os.environ.items() if k not in ("GEMINI_API_KEY", "GOOGLE_API_KEY")}
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(Exception) as exc_info:
                generate_timeline("test without key")

            error_str = str(exc_info.value)
            # Either mentions the key name, or mentions the package (ImportError case)
            assert (
                "GEMINI_API_KEY" in error_str
                or "api_key" in error_str.lower()
                or "google-generativeai" in error_str
                or "generativeai" in error_str
            )
