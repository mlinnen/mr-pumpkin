"""
Test suite for skill/audio_analyzer.py — Audio Analysis Provider (Issue #72)

Tests the AudioAnalysisProvider ABC and GeminiAudioProvider implementation.
Validates contract enforcement, Gemini API mocking, phoneme mapping, beat/pause
detection, error handling, and file cleanup behavior.

Author: Mylo (Tester)
Date: 2026-03-05
Issue: #72 — Build audio_analyzer module
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock, call
from abc import ABC

# Add parent directory to import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Deferred import — skill/audio_analyzer.py being implemented by Vi
try:
    from skill.audio_analyzer import (
        AudioAnalysis,
        AudioAnalysisProvider,
        GeminiAudioProvider,
        get_provider,
        WordTiming,
        BeatEvent,
        PauseSegment
    )
    SKILL_AVAILABLE = True
except ImportError:
    SKILL_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not SKILL_AVAILABLE,
    reason="skill/audio_analyzer.py not yet created — tests written from architecture spec"
)


# ============================================================================
# SAMPLE TEST DATA
# ============================================================================

SAMPLE_ANALYSIS_JSON = {
    "duration_ms": 5000,
    "speech_segments": [
        {"word": "hello", "start_ms": 100, "end_ms": 600, "phoneme_group": "open_vowel"},
        {"word": "pumpkin", "start_ms": 700, "end_ms": 1400, "phoneme_group": "bilabial"},
    ],
    "beats": [
        {"time_ms": 1000, "strength": "strong"},
        {"time_ms": 2000, "strength": "bar1"},
    ],
    "pauses": [
        {"start_ms": 600, "end_ms": 700, "duration_ms": 100},
    ]
}

SAMPLE_EMOTION = "happy"


def _make_mock_gemini_response(analysis_json, emotion):
    """Helper to create a realistic mock Gemini response."""
    mock_response = Mock()
    mock_response.text = json.dumps(analysis_json)
    
    # Mock for emotion pass (pass 2)
    mock_emotion_response = Mock()
    mock_emotion_response.text = emotion
    
    return mock_response, mock_emotion_response


# ============================================================================
# AudioAnalysis DATACLASS TESTS
# ============================================================================

class TestAudioAnalysisDataclass:
    """AudioAnalysis dataclass can be instantiated with all required fields."""

    def test_instantiate_with_all_fields(self):
        """AudioAnalysis can be instantiated with all fields."""
        analysis = AudioAnalysis(
            speech_segments=[],
            beats=[],
            pauses=[],
            emotion="happy",
            duration_ms=5000,
            audio_path="test.mp3"
        )
        
        assert isinstance(analysis.speech_segments, list)
        assert isinstance(analysis.beats, list)
        assert isinstance(analysis.pauses, list)
        assert analysis.emotion == "happy"
        assert analysis.duration_ms == 5000

    def test_speech_segments_is_list(self):
        """speech_segments field is a list."""
        analysis = AudioAnalysis(
            speech_segments=[WordTiming("hello", 0, 500, "open_vowel")],
            beats=[],
            pauses=[],
            emotion="neutral",
            duration_ms=1000,
            audio_path="test.mp3"
        )
        
        assert isinstance(analysis.speech_segments, list)
        assert len(analysis.speech_segments) == 1

    def test_beats_is_list(self):
        """beats field is a list."""
        analysis = AudioAnalysis(
            speech_segments=[],
            beats=[BeatEvent(1000, "strong")],
            pauses=[],
            emotion="neutral",
            duration_ms=2000,
            audio_path="test.mp3"
        )
        
        assert isinstance(analysis.beats, list)
        assert len(analysis.beats) == 1

    def test_pauses_is_list(self):
        """pauses field is a list."""
        analysis = AudioAnalysis(
            speech_segments=[],
            beats=[],
            pauses=[PauseSegment(500, 700, 200)],
            emotion="neutral",
            duration_ms=1000,
            audio_path="test.mp3"
        )
        
        assert isinstance(analysis.pauses, list)
        assert len(analysis.pauses) == 1

    def test_emotion_is_string(self):
        """emotion field is a string."""
        analysis = AudioAnalysis(
            speech_segments=[],
            beats=[],
            pauses=[],
            emotion="excited",
            duration_ms=1000,
            audio_path="test.mp3"
        )
        
        assert isinstance(analysis.emotion, str)

    def test_duration_ms_is_int(self):
        """duration_ms field is an int."""
        analysis = AudioAnalysis(
            speech_segments=[],
            beats=[],
            pauses=[],
            emotion="neutral",
            duration_ms=5000,
            audio_path="test.mp3"
        )
        
        assert isinstance(analysis.duration_ms, int)


# ============================================================================
# AudioAnalysisProvider ABC CONTRACT TESTS
# ============================================================================

class TestAudioAnalysisProviderABC:
    """AudioAnalysisProvider ABC enforces contract on concrete implementations."""

    def test_cannot_instantiate_directly(self):
        """AudioAnalysisProvider is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            AudioAnalysisProvider()

    def test_concrete_subclass_must_implement_analyze_audio(self):
        """Concrete subclass MUST implement analyze_audio method."""
        # Create a subclass without implementing analyze_audio
        class BrokenProvider(AudioAnalysisProvider):
            pass
        
        with pytest.raises(TypeError):
            BrokenProvider()

    def test_concrete_subclass_can_be_instantiated(self):
        """Concrete subclass with analyze_audio implemented can be instantiated."""
        class ValidProvider(AudioAnalysisProvider):
            def analyze_audio(self, audio_path: str, prompt: str) -> AudioAnalysis:
                return AudioAnalysis([], [], [], "neutral", 1000, "test.mp3")
        
        provider = ValidProvider()
        assert isinstance(provider, AudioAnalysisProvider)

    def test_analyze_audio_returns_audio_analysis(self):
        """analyze_audio method returns an AudioAnalysis instance."""
        class ValidProvider(AudioAnalysisProvider):
            def analyze_audio(self, audio_path: str, prompt: str) -> AudioAnalysis:
                return AudioAnalysis([], [], [], "neutral", 1000, "test.mp3")
        
        provider = ValidProvider()
        result = provider.analyze_audio("test.mp3", "test prompt")
        
        assert isinstance(result, AudioAnalysis)


# ============================================================================
# GeminiAudioProvider UNIT TESTS
# ============================================================================

class TestGeminiAudioProvider:
    """GeminiAudioProvider unit tests with mocked Gemini client."""

    @patch('google.genai.Client')
    def test_analyze_audio_returns_audio_analysis(self, mock_client_class, tmp_path):
        """Mock returns valid JSON → analyze_audio returns AudioAnalysis instance."""
        # Create a fake audio file
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        # Mock the client and responses
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            SAMPLE_ANALYSIS_JSON, SAMPLE_EMOTION
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        # Create provider and analyze
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        assert isinstance(result, AudioAnalysis)
        assert result.duration_ms == 5000
        assert result.emotion == "happy"

    @patch('google.genai.Client')
    def test_analyze_audio_speech_segments(self, mock_client_class, tmp_path):
        """speech_segments contain WordTiming objects with correct phoneme_group values."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            SAMPLE_ANALYSIS_JSON, SAMPLE_EMOTION
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        assert len(result.speech_segments) == 2
        assert result.speech_segments[0].word == "hello"
        assert result.speech_segments[0].start_ms == 100
        assert result.speech_segments[0].end_ms == 600
        assert result.speech_segments[0].phoneme_group == "open_vowel"
        assert result.speech_segments[1].phoneme_group == "bilabial"

    @patch('google.genai.Client')
    def test_analyze_audio_beats(self, mock_client_class, tmp_path):
        """beats contain BeatEvent with time_ms and strength."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            SAMPLE_ANALYSIS_JSON, SAMPLE_EMOTION
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        assert len(result.beats) == 2
        assert result.beats[0].time_ms == 1000
        assert result.beats[0].strength == "strong"
        assert result.beats[1].time_ms == 2000
        assert result.beats[1].strength == "bar1"

    @patch('google.genai.Client')
    def test_analyze_audio_pauses(self, mock_client_class, tmp_path):
        """pauses contain PauseSegment with duration_ms calculated correctly."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            SAMPLE_ANALYSIS_JSON, SAMPLE_EMOTION
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        assert len(result.pauses) == 1
        assert result.pauses[0].start_ms == 600
        assert result.pauses[0].end_ms == 700
        assert result.pauses[0].duration_ms == 100

    @patch('google.genai.Client')
    def test_analyze_audio_emotion(self, mock_client_class, tmp_path):
        """emotion field comes from pass 2 response."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            SAMPLE_ANALYSIS_JSON, "excited"
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        assert result.emotion == "excited"

    @patch('google.genai.Client')
    def test_analyze_audio_malformed_json_retries(self, mock_client_class, tmp_path):
        """When Gemini returns bad JSON, provider retries once."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        # First call returns bad JSON, second call returns valid JSON
        bad_response = Mock()
        bad_response.text = "not valid json {{"
        
        good_response, emotion_response = _make_mock_gemini_response(
            SAMPLE_ANALYSIS_JSON, SAMPLE_EMOTION
        )
        
        mock_client.models.generate_content.side_effect = [
            bad_response,  # First attempt fails
            good_response,  # Retry succeeds
            emotion_response  # Emotion pass
        ]
        
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        # Should succeed after retry
        assert isinstance(result, AudioAnalysis)
        assert mock_client.models.generate_content.call_count == 3  # 2 for structure + 1 for emotion

    @patch('google.genai.Client')
    def test_analyze_audio_malformed_json_raises_after_retry(self, mock_client_class, tmp_path):
        """When retry also fails, raises ValueError."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        # Both attempts return bad JSON
        bad_response = Mock()
        bad_response.text = "not valid json {{"
        
        mock_client.models.generate_content.return_value = bad_response
        
        provider = GeminiAudioProvider(api_key="test_key")
        
        with pytest.raises(ValueError):
            provider.analyze_audio(str(audio_file), "test prompt")

    @patch('google.genai.Client')
    def test_analyze_audio_uploads_file(self, mock_client_class, tmp_path):
        """client.files.upload() is called with the audio path."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            SAMPLE_ANALYSIS_JSON, SAMPLE_EMOTION
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        provider.analyze_audio(str(audio_file), "test prompt")
        
        mock_client.files.upload.assert_called_once()
        call_args = mock_client.files.upload.call_args
        assert call_args.kwargs.get("path") == str(audio_file) or str(audio_file) in str(call_args).replace("\\\\", "\\")

    @patch('google.genai.Client')
    def test_analyze_audio_deletes_file_after(self, mock_client_class, tmp_path):
        """client.files.delete() is called after analysis."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            SAMPLE_ANALYSIS_JSON, SAMPLE_EMOTION
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        provider.analyze_audio(str(audio_file), "test prompt")
        
        mock_client.files.delete.assert_called_once_with(name=mock_file.name)

    @patch('google.genai.Client')
    def test_analyze_audio_empty_audio(self, mock_client_class, tmp_path):
        """Handles audio with no speech gracefully (empty speech_segments list)."""
        audio_file = tmp_path / "silent.mp3"
        audio_file.write_bytes(b"fake silent audio")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        empty_analysis = {
            "duration_ms": 2000,
            "speech_segments": [],
            "beats": [],
            "pauses": []
        }
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            empty_analysis, "neutral"
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        assert isinstance(result, AudioAnalysis)
        assert len(result.speech_segments) == 0
        assert result.emotion == "neutral"

    @patch('google.genai.Client')
    def test_analyze_audio_no_beats(self, mock_client_class, tmp_path):
        """Handles audio with no musical content (empty beats list)."""
        audio_file = tmp_path / "speech_only.mp3"
        audio_file.write_bytes(b"fake speech audio")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        speech_only_analysis = {
            "duration_ms": 3000,
            "speech_segments": [
                {"word": "hello", "start_ms": 100, "end_ms": 600, "phoneme_group": "open_vowel"}
            ],
            "beats": [],
            "pauses": []
        }
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            speech_only_analysis, "neutral"
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        assert isinstance(result, AudioAnalysis)
        assert len(result.beats) == 0
        assert len(result.speech_segments) == 1


# ============================================================================
# PROVIDER FACTORY TESTS
# ============================================================================

class TestGetProvider:
    """get_provider() factory function tests."""

    def test_get_provider_gemini(self):
        """get_provider('gemini') returns GeminiAudioProvider."""
        provider = get_provider("gemini", api_key="test_key")
        
        assert isinstance(provider, GeminiAudioProvider)
        assert isinstance(provider, AudioAnalysisProvider)

    def test_get_provider_unknown_raises(self):
        """get_provider('unknown_xyz') raises ValueError."""
        with pytest.raises(ValueError):
            get_provider("unknown_xyz", api_key="test_key")


# ============================================================================
# PHONEME GROUP MAPPING TESTS
# ============================================================================

class TestPhonemeGroupMapping:
    """Phoneme group mapping spot-checks (pure logic tests)."""

    @patch('google.genai.Client')
    def test_bilabial_stops_mapping(self, mock_client_class, tmp_path):
        """Words with M/B/P → 'bilabial' phoneme group."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        bilabial_analysis = {
            "duration_ms": 2000,
            "speech_segments": [
                {"word": "mom", "start_ms": 0, "end_ms": 300, "phoneme_group": "bilabial"},
                {"word": "pop", "start_ms": 400, "end_ms": 700, "phoneme_group": "bilabial"},
                {"word": "baby", "start_ms": 800, "end_ms": 1200, "phoneme_group": "bilabial"},
            ],
            "beats": [],
            "pauses": []
        }
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            bilabial_analysis, "neutral"
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        for segment in result.speech_segments:
            assert segment.phoneme_group == "bilabial"

    @patch('google.genai.Client')
    def test_open_vowels_mapping(self, mock_client_class, tmp_path):
        """Words with AH/AA → 'open_vowel' phoneme group."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        open_vowel_analysis = {
            "duration_ms": 2000,
            "speech_segments": [
                {"word": "ah", "start_ms": 0, "end_ms": 300, "phoneme_group": "open_vowel"},
                {"word": "father", "start_ms": 400, "end_ms": 900, "phoneme_group": "open_vowel"},
            ],
            "beats": [],
            "pauses": []
        }
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            open_vowel_analysis, "neutral"
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        for segment in result.speech_segments:
            assert segment.phoneme_group == "open_vowel"

    @patch('google.genai.Client')
    def test_spread_vowels_mapping(self, mock_client_class, tmp_path):
        """Words with EE/IH → 'spread_vowel' phoneme group."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        spread_vowel_analysis = {
            "duration_ms": 2000,
            "speech_segments": [
                {"word": "see", "start_ms": 0, "end_ms": 300, "phoneme_group": "spread_vowel"},
                {"word": "it", "start_ms": 400, "end_ms": 600, "phoneme_group": "spread_vowel"},
            ],
            "beats": [],
            "pauses": []
        }
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            spread_vowel_analysis, "neutral"
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        for segment in result.speech_segments:
            assert segment.phoneme_group == "spread_vowel"

    @patch('google.genai.Client')
    def test_round_vowels_mapping(self, mock_client_class, tmp_path):
        """Words with OO/OH → 'round_vowel' phoneme group."""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_bytes(b"fake audio data")
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_file = Mock()
        mock_file.name = "uploaded_file"
        mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test123"
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value.state = "ACTIVE"
        
        round_vowel_analysis = {
            "duration_ms": 2000,
            "speech_segments": [
                {"word": "oo", "start_ms": 0, "end_ms": 300, "phoneme_group": "round_vowel"},
                {"word": "go", "start_ms": 400, "end_ms": 700, "phoneme_group": "round_vowel"},
            ],
            "beats": [],
            "pauses": []
        }
        
        mock_response, mock_emotion_response = _make_mock_gemini_response(
            round_vowel_analysis, "neutral"
        )
        mock_client.models.generate_content.side_effect = [mock_response, mock_emotion_response]
        
        provider = GeminiAudioProvider(api_key="test_key")
        result = provider.analyze_audio(str(audio_file), "test prompt")
        
        for segment in result.speech_segments:
            assert segment.phoneme_group == "round_vowel"
