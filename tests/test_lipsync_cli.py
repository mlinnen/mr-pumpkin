"""
Test suite for skill/lipsync_cli.py — Lip-Sync CLI (Issue #73)

Tests the build_lipsync_prompt() function and main() CLI entry point.
Validates prompt enrichment, argument parsing, dry-run behavior, upload
calls, and audio file injection into timeline.

Author: Mylo (Tester)
Date: 2026-03-05
Issue: #73 — Write end-to-end tests for lipsync_cli.py
"""

import json
import os
import sys
import pytest
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from skill.audio_analyzer import AudioAnalysis, WordTiming, BeatEvent, PauseSegment
from skill.lipsync_cli import build_lipsync_prompt, _build_parser, main


# ============================================================================
# HELPERS
# ============================================================================

def _make_analysis(
    speech_segments=None,
    beats=None,
    pauses=None,
    emotion="happy",
    duration_ms=5000,
    audio_path="test.mp3",
):
    return AudioAnalysis(
        speech_segments=speech_segments or [],
        beats=beats or [],
        pauses=pauses or [],
        emotion=emotion,
        duration_ms=duration_ms,
        audio_path=audio_path,
    )


def _make_word(word="hello", start_ms=100, end_ms=600, phoneme_group="open_vowel"):
    return WordTiming(word=word, start_ms=start_ms, end_ms=end_ms, phoneme_group=phoneme_group)


def _make_beat(time_ms=1000, strength="strong"):
    return BeatEvent(time_ms=time_ms, strength=strength)


def _make_pause(start_ms=600, end_ms=1100, duration_ms=500):
    return PauseSegment(start_ms=start_ms, end_ms=end_ms, duration_ms=duration_ms)


SAMPLE_TIMELINE = {
    "events": [{"time_ms": 0, "command": "set_expression happy"}]
}


# ============================================================================
# TestBuildLipsyncPrompt
# ============================================================================

class TestBuildLipsyncPrompt:
    """Unit tests for build_lipsync_prompt()."""

    def test_includes_word_timings(self):
        """Word timings from speech_segments appear in enriched prompt."""
        analysis = _make_analysis(speech_segments=[_make_word("hello", 100, 600)])
        result = build_lipsync_prompt(analysis, "test prompt")
        assert "hello" in result
        assert "100" in result
        assert "600" in result

    def test_includes_beat_events(self):
        """Beat events appear in the enriched prompt."""
        analysis = _make_analysis(beats=[_make_beat(time_ms=1000, strength="strong")])
        result = build_lipsync_prompt(analysis, "")
        assert "1000" in result
        assert "strong" in result

    def test_includes_pause_segments(self):
        """Pause segments appear in the enriched prompt."""
        analysis = _make_analysis(pauses=[_make_pause(start_ms=600, end_ms=1100, duration_ms=500)])
        result = build_lipsync_prompt(analysis, "")
        assert "600" in result
        assert "1100" in result
        assert "500" in result

    def test_includes_original_prompt(self):
        """User's original prompt is preserved in the enriched output."""
        analysis = _make_analysis()
        user_prompt = "pumpkin sings this joyfully"
        result = build_lipsync_prompt(analysis, user_prompt)
        assert user_prompt in result

    def test_handles_empty_analysis(self):
        """Works with empty word/beat/pause lists — no exceptions raised."""
        analysis = _make_analysis(speech_segments=[], beats=[], pauses=[])
        result = build_lipsync_prompt(analysis, "")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_includes_emotion(self):
        """Emotion from analysis is included in the enriched prompt."""
        analysis = _make_analysis(emotion="excited")
        result = build_lipsync_prompt(analysis, "")
        assert "excited" in result

    def test_includes_duration(self):
        """Audio duration (in seconds) is reflected in the prompt."""
        analysis = _make_analysis(duration_ms=7500)
        result = build_lipsync_prompt(analysis, "")
        assert "7.5" in result

    def test_phoneme_group_appears(self):
        """Phoneme group of each word segment appears in prompt."""
        analysis = _make_analysis(speech_segments=[_make_word(phoneme_group="bilabial")])
        result = build_lipsync_prompt(analysis, "")
        assert "bilabial" in result

    def test_bar1_beat_reaction(self):
        """bar1 beat strength triggers 'turn_up' reaction hint."""
        analysis = _make_analysis(beats=[_make_beat(time_ms=500, strength="bar1")])
        result = build_lipsync_prompt(analysis, "")
        assert "turn_up" in result

    def test_long_pause_gets_blink_note(self):
        """Pauses ≥400ms receive a '→ blink' annotation."""
        analysis = _make_analysis(pauses=[_make_pause(duration_ms=400)])
        result = build_lipsync_prompt(analysis, "")
        assert "blink" in result

    def test_short_pause_no_blink(self):
        """Pauses <400ms receive a 'no blink' annotation."""
        analysis = _make_analysis(pauses=[_make_pause(duration_ms=200)])
        result = build_lipsync_prompt(analysis, "")
        assert "no blink" in result

    def test_empty_user_prompt_omitted(self):
        """Artistic direction line is omitted when user_prompt is empty string."""
        analysis = _make_analysis()
        result = build_lipsync_prompt(analysis, "")
        assert "Artistic direction" not in result


# ============================================================================
# TestLipSyncCLIMain
# ============================================================================

class TestLipSyncCLIMain:
    """Integration tests for main() with mocked external dependencies."""

    def _run_main(self, extra_args=None, audio_exists=True, timeline=None):
        """Helper to run main() with standard mocks."""
        timeline = timeline or dict(SAMPLE_TIMELINE)
        argv = ["test.mp3"] + (extra_args or [])

        mock_analysis = _make_analysis(
            speech_segments=[_make_word()],
            beats=[_make_beat()],
            pauses=[_make_pause()],
        )
        mock_provider = MagicMock()
        mock_provider.analyze_audio.return_value = mock_analysis

        with patch("skill.lipsync_cli.Path") as mock_path_cls, \
             patch("skill.lipsync_cli.get_audio_provider", return_value=mock_provider) as mock_get_prov, \
             patch("skill.lipsync_cli.GeminiProvider") as mock_gemini_cls, \
             patch("skill.lipsync_cli.generate_timeline", return_value=dict(timeline)) as mock_gen, \
             patch("skill.lipsync_cli.upload_audio") as mock_upload_audio, \
             patch("skill.lipsync_cli.upload_timeline") as mock_upload_timeline:

            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = audio_exists
            mock_path_instance.stem = "test"
            mock_path_instance.suffix = ".mp3"
            mock_path_instance.name = "test.mp3"
            mock_path_instance.__str__ = lambda self: "test.mp3"
            mock_path_instance.read_bytes.return_value = b"audio data"
            mock_path_cls.return_value = mock_path_instance

            rc = main(argv)

        return rc, mock_provider, mock_gen, mock_upload_audio, mock_upload_timeline

    def test_dry_run_no_upload(self):
        """With --dry-run, upload functions are NOT called."""
        rc, _, _, mock_upload_audio, mock_upload_timeline = self._run_main(["--dry-run"])
        assert rc == 0
        mock_upload_audio.assert_not_called()
        mock_upload_timeline.assert_not_called()

    def test_calls_analyze_audio(self):
        """analyze_audio() is called with the audio file path."""
        rc, mock_provider, _, _, _ = self._run_main(["--dry-run"])
        assert rc == 0
        mock_provider.analyze_audio.assert_called_once()
        call_args = mock_provider.analyze_audio.call_args
        assert "test.mp3" in str(call_args)

    def test_calls_generate_timeline(self):
        """generate_timeline() is called with an enriched prompt."""
        rc, _, mock_gen, _, _ = self._run_main(["--dry-run"])
        assert rc == 0
        mock_gen.assert_called_once()
        prompt_arg = mock_gen.call_args[0][0]
        assert isinstance(prompt_arg, str)
        assert len(prompt_arg) > 0

    def test_uploads_when_server_live(self):
        """Without --dry-run, upload_audio and upload_timeline are called."""
        rc, _, _, mock_upload_audio, mock_upload_timeline = self._run_main()
        assert rc == 0
        mock_upload_audio.assert_called_once()
        mock_upload_timeline.assert_called_once()

    def test_audio_file_set_in_timeline(self):
        """timeline['audio_file'] is set to the audio filename."""
        captured = {}

        def capture_timeline(name, tl, **kwargs):
            captured["tl"] = tl

        argv = ["test.mp3"]
        mock_analysis = _make_analysis()
        mock_provider = MagicMock()
        mock_provider.analyze_audio.return_value = mock_analysis

        with patch("skill.lipsync_cli.Path") as mock_path_cls, \
             patch("skill.lipsync_cli.get_audio_provider", return_value=mock_provider), \
             patch("skill.lipsync_cli.GeminiProvider"), \
             patch("skill.lipsync_cli.generate_timeline", return_value=dict(SAMPLE_TIMELINE)), \
             patch("skill.lipsync_cli.upload_audio"), \
             patch("skill.lipsync_cli.upload_timeline", side_effect=capture_timeline):

            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.stem = "test"
            mock_path_instance.suffix = ".mp3"
            mock_path_instance.name = "test.mp3"
            mock_path_instance.__str__ = lambda self: "test.mp3"
            mock_path_instance.read_bytes.return_value = b"audio"
            mock_path_cls.return_value = mock_path_instance

            rc = main(argv)

        assert rc == 0
        assert "audio_file" in captured["tl"]
        assert captured["tl"]["audio_file"] == "test.mp3"

    def test_missing_audio_file_returns_error(self):
        """Returns exit code 1 when audio file does not exist."""
        rc, _, _, _, _ = self._run_main(audio_exists=False)
        assert rc == 1

    def test_enriched_prompt_contains_user_prompt(self):
        """The prompt passed to generate_timeline contains the user's --prompt text."""
        user_directive = "sing with great joy"
        argv = ["test.mp3", "--prompt", user_directive, "--dry-run"]
        mock_analysis = _make_analysis()
        mock_provider = MagicMock()
        mock_provider.analyze_audio.return_value = mock_analysis
        captured_prompt = {}

        def capture(prompt, **kwargs):
            captured_prompt["val"] = prompt
            return dict(SAMPLE_TIMELINE)

        with patch("skill.lipsync_cli.Path") as mock_path_cls, \
             patch("skill.lipsync_cli.get_audio_provider", return_value=mock_provider), \
             patch("skill.lipsync_cli.GeminiProvider"), \
             patch("skill.lipsync_cli.generate_timeline", side_effect=capture):

            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.stem = "test"
            mock_path_instance.suffix = ".mp3"
            mock_path_instance.name = "test.mp3"
            mock_path_instance.__str__ = lambda self: "test.mp3"
            mock_path_cls.return_value = mock_path_instance

            rc = main(argv)

        assert rc == 0
        assert user_directive in captured_prompt["val"]

    def test_upload_called_with_host_and_ports(self):
        """upload_audio is called with the configured host and port values."""
        argv = ["test.mp3", "--host", "192.168.1.10", "--tcp-port", "6000"]
        mock_analysis = _make_analysis()
        mock_provider = MagicMock()
        mock_provider.analyze_audio.return_value = mock_analysis

        with patch("skill.lipsync_cli.Path") as mock_path_cls, \
             patch("skill.lipsync_cli.get_audio_provider", return_value=mock_provider), \
             patch("skill.lipsync_cli.GeminiProvider"), \
             patch("skill.lipsync_cli.generate_timeline", return_value=dict(SAMPLE_TIMELINE)), \
             patch("skill.lipsync_cli.upload_audio") as mock_ua, \
             patch("skill.lipsync_cli.upload_timeline"):

            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.stem = "test"
            mock_path_instance.suffix = ".mp3"
            mock_path_instance.name = "test.mp3"
            mock_path_instance.__str__ = lambda self: "test.mp3"
            mock_path_instance.read_bytes.return_value = b"audio"
            mock_path_cls.return_value = mock_path_instance

            rc = main(argv)

        assert rc == 0
        call_kwargs = mock_ua.call_args[1]
        assert call_kwargs["host"] == "192.168.1.10"
        assert call_kwargs["tcp_port"] == 6000


# ============================================================================
# TestCLIArgParsing
# ============================================================================

class TestCLIArgParsing:
    """Tests for _build_parser() argument parsing."""

    def test_required_args_audio_file(self):
        """audio_file positional argument is required."""
        parser = _build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_audio_file_parsed(self):
        """audio_file is correctly parsed as a positional argument."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3"])
        assert args.audio_file == "song.mp3"

    def test_dry_run_flag(self):
        """--dry-run sets dry_run to True."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3", "--dry-run"])
        assert args.dry_run is True

    def test_dry_run_default_false(self):
        """dry_run defaults to False when flag not provided."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3"])
        assert args.dry_run is False

    def test_default_server_host(self):
        """--host defaults to 'localhost'."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3"])
        assert args.host == "localhost"

    def test_default_tcp_port(self):
        """--tcp-port defaults to 5000."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3"])
        assert args.tcp_port == 5000

    def test_default_ws_port(self):
        """--ws-port defaults to 5001."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3"])
        assert args.ws_port == 5001

    def test_custom_host(self):
        """--host accepts a custom hostname."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3", "--host", "192.168.1.5"])
        assert args.host == "192.168.1.5"

    def test_prompt_default_empty(self):
        """--prompt defaults to empty string."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3"])
        assert args.prompt == ""

    def test_prompt_value(self):
        """--prompt captures user-provided artistic direction."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3", "--prompt", "joyful celebration"])
        assert args.prompt == "joyful celebration"

    def test_filename_flag(self):
        """-f / --filename sets the recording name."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3", "-f", "my_recording"])
        assert args.filename == "my_recording"

    def test_protocol_default_tcp(self):
        """--protocol defaults to 'tcp'."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3"])
        assert args.protocol == "tcp"

    def test_protocol_ws(self):
        """--protocol accepts 'ws' for WebSocket."""
        parser = _build_parser()
        args = parser.parse_args(["song.mp3", "--protocol", "ws"])
        assert args.protocol == "ws"
