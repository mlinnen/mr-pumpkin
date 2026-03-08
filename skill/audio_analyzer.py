"""
Audio analysis for Mr. Pumpkin lip-sync and beat-driven animation.

Translates audio files (speech, music, ambient sound) into structured timing data
(word segments, beats, pauses, emotion) using AI analysis. Supports pluggable
providers; defaults to Gemini multimodal audio analysis.

Usage:
    from skill.audio_analyzer import AudioAnalysis, get_provider
    provider = get_provider("gemini")
    analysis = provider.analyze_audio("my_song.mp3")
"""

import json
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


def _measure_audio_duration_ms(audio_path: str) -> int | None:
    """Measure audio file duration in milliseconds using mutagen, wave, or file-size fallback.

    Returns None if duration cannot be determined.
    """
    try:
        from mutagen import File as MutagenFile
        audio = MutagenFile(audio_path)
        if audio is not None and audio.info is not None:
            return int(audio.info.length * 1000)
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"mutagen failed for {audio_path}: {e}")

    # Fallback: wave module for .wav files
    if audio_path.lower().endswith(".wav"):
        try:
            import wave
            with wave.open(audio_path, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                if rate > 0:
                    return int(frames / rate * 1000)
        except Exception as e:
            logger.debug(f"wave fallback failed for {audio_path}: {e}")

    return None

logger = logging.getLogger(__name__)


@dataclass
class WordTiming:
    """Represents a single word in speech with phoneme classification."""
    word: str
    start_ms: int
    end_ms: int
    phoneme_group: str  # "bilabial", "open_vowel", "spread_vowel", "round_vowel", "neutral"


@dataclass
class BeatEvent:
    """Represents a detected beat in music or rhythmic audio."""
    time_ms: int
    strength: str  # "strong", "bar1", "normal"


@dataclass
class PauseSegment:
    """Represents a silence gap between speech segments."""
    start_ms: int
    end_ms: int
    duration_ms: int


@dataclass
class AudioAnalysis:
    """Complete structured analysis of an audio file."""
    speech_segments: list[WordTiming]
    beats: list[BeatEvent]
    pauses: list[PauseSegment]
    emotion: str  # "happy", "sad", "excited", "neutral", "solemn"
    duration_ms: int
    audio_path: str


class AudioAnalysisProvider(ABC):
    """Abstract base class for audio analysis backends."""

    @abstractmethod
    def analyze_audio(self, audio_path: str, prompt: str = "") -> AudioAnalysis:
        """Analyze an audio file and return structured timing data.

        Args:
            audio_path: Path to the audio file to analyze.
            prompt: Optional user guidance for the analysis (e.g., "upbeat song").

        Returns:
            AudioAnalysis dataclass with speech segments, beats, pauses, emotion, duration.
        """


class GeminiAudioProvider(AudioAnalysisProvider):
    """Audio analysis provider backed by Google Gemini multimodal API.

    Uses gemini-1.5-pro with file upload for two-pass analysis:
    - Pass 1: Extract structured timing data (speech, beats, pauses)
    - Pass 2: Determine dominant emotion

    API key is read from the GEMINI_API_KEY environment variable,
    falling back to GOOGLE_API_KEY.

    Raises:
        EnvironmentError: If no API key is found in the environment.
        ImportError: If the google-genai package is not installed.
    """

    MODEL = "gemini-2.5-flash"
    
    # MIME type mappings for audio file extensions
    _MIME_TYPES = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
        ".flac": "audio/flac",
    }

    def __init__(self, api_key: str = None, model: str = None):
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ImportError(
                "google-genai is required for GeminiAudioProvider. "
                "Install it with: pip install google-genai"
            ) from exc

        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        
        if not api_key:
            raise EnvironmentError(
                "No Gemini API key found. Set the GEMINI_API_KEY environment variable."
            )

        self._client = genai.Client(api_key=api_key)
        self._types = types
        self._model = model or self.MODEL

    def _get_mime_type(self, audio_path: str) -> str:
        """Determine MIME type from file extension."""
        ext = os.path.splitext(audio_path.lower())[1]
        mime_type = self._MIME_TYPES.get(ext, "audio/mpeg")
        return mime_type

    def _wait_for_file_active(self, file_name: str, timeout: int = 60) -> None:
        """Poll file status until it becomes ACTIVE.
        
        Gemini requires uploaded files to be in ACTIVE state before use.
        
        Args:
            file_name: The uploaded file's name field (e.g., "files/abc123")
            timeout: Maximum seconds to wait
            
        Raises:
            TimeoutError: If file doesn't become active within timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            file_info = self._client.files.get(name=file_name)
            if file_info.state == "ACTIVE":
                logger.debug(f"File {file_name} is now ACTIVE")
                return
            elif file_info.state == "FAILED":
                raise RuntimeError(f"File processing failed: {file_name}")
            
            time.sleep(2)
        
        raise TimeoutError(f"File {file_name} did not become ACTIVE within {timeout}s")

    def analyze_audio(self, audio_path: str, prompt: str = "") -> AudioAnalysis:
        """Analyze audio file using Gemini multimodal API.

        Two-pass approach:
        - Pass 1: Upload audio and extract structured timing data (speech/beats/pauses)
        - Pass 2: Determine dominant emotion using same uploaded file

        Args:
            audio_path: Path to audio file
            prompt: Optional user guidance (currently unused, reserved for future)

        Returns:
            AudioAnalysis dataclass with complete timing and emotion data

        Raises:
            ValueError: If Gemini returns malformed JSON or file doesn't exist
            FileNotFoundError: If audio_path doesn't exist
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        mime_type = self._get_mime_type(audio_path)
        logger.info(f"Uploading {audio_path} ({mime_type}) to Gemini...")

        # Upload audio file
        uploaded_file = self._client.files.upload(
            file=audio_path,
            config={"mime_type": mime_type},
        )
        
        file_name = uploaded_file.name
        file_uri = uploaded_file.uri
        logger.debug(f"Uploaded as {file_name} ({file_uri}), waiting for ACTIVE state...")

        try:
            # Wait for file to be processed
            self._wait_for_file_active(file_name)

            # Pass 1: Extract structured timing data
            timing_data = self._extract_timing_data(file_uri, mime_type)

            # Pass 2: Extract emotion using the same uploaded file
            emotion = self._extract_emotion(file_uri, mime_type)

            # Measure real duration independently — Gemini can underreport this.
            measured_ms = _measure_audio_duration_ms(audio_path)
            gemini_ms = timing_data.get("duration_ms", 0)

            if measured_ms is not None:
                if gemini_ms > 0:
                    ratio = abs(measured_ms - gemini_ms) / gemini_ms
                    if ratio > 0.10:
                        logger.warning(
                            f"Gemini reported duration {gemini_ms}ms but measured {measured_ms}ms "
                            f"({ratio:.0%} discrepancy). Using measured value."
                        )
                duration_ms = measured_ms
            else:
                logger.warning("Could not measure audio duration; falling back to Gemini's reported value.")
                duration_ms = gemini_ms

            # Build AudioAnalysis from results
            analysis = AudioAnalysis(
                speech_segments=[
                    WordTiming(**seg) for seg in timing_data.get("speech_segments", [])
                ],
                beats=[
                    BeatEvent(**beat) for beat in timing_data.get("beats", [])
                ],
                pauses=[
                    PauseSegment(**pause) for pause in timing_data.get("pauses", [])
                ],
                emotion=emotion,
                duration_ms=duration_ms,
                audio_path=audio_path,
            )

            logger.info(
                f"Analysis complete: {len(analysis.speech_segments)} words, "
                f"{len(analysis.beats)} beats, {len(analysis.pauses)} pauses, "
                f"emotion={emotion}, duration={analysis.duration_ms}ms"
            )

            return analysis

        finally:
            # Clean up uploaded file
            try:
                self._client.files.delete(name=file_name)
                logger.debug(f"Deleted uploaded file {file_name}")
            except Exception as e:
                logger.warning(f"Failed to delete uploaded file {file_name}: {e}")

    def _extract_timing_data(self, file_uri: str, mime_type: str) -> dict:
        """Pass 1: Extract structured timing data from audio.
        
        Args:
            file_uri: Full Gemini file URI (e.g., "https://generativelanguage.googleapis.com/v1beta/files/abc123")
            mime_type: MIME type of the audio file
            
        Returns:
            Dict with duration_ms, speech_segments, beats, pauses
            
        Raises:
            ValueError: If JSON parsing fails after retry
        """
        timing_prompt = """Analyze this audio file. Return ONLY valid JSON in this exact format:
{
  "duration_ms": <int>,
  "speech_segments": [
    {"word": "<word>", "start_ms": <int>, "end_ms": <int>, "phoneme_group": "<bilabial|open_vowel|spread_vowel|round_vowel|neutral>"}
  ],
  "beats": [
    {"time_ms": <int>, "strength": "<strong|bar1|normal>"}
  ],
  "pauses": [
    {"start_ms": <int>, "end_ms": <int>, "duration_ms": <int>}
  ]
}

Phoneme group rules — classify by the DOMINANT VOWEL sound in the word, not the starting consonant:
- round_vowel: words whose most prominent sound is OO or OH (e.g., "boo", "moon", "ghost", "spooky", "no", "oh", "go")
- open_vowel: words whose most prominent sound is AH, AA, or AW (e.g., "ahh", "ha", "bat", "father", "scary")
- spread_vowel: words whose most prominent sound is EE or IH (e.g., "eek", "see", "think", "it", "teeth")
- bilabial: ONLY words where lip-closure is the dominant feature — sustained humming or pure consonant sounds (e.g., "mmm", "bam", "pop"). Do NOT classify vowel-dominant words like "boo" as bilabial just because they start with B or M.
- neutral: all others (consonant clusters, unstressed syllables, unclear vowels)

Beat detection: only include beats if audio has musical rhythm. Bar 1 beats are the strongest downbeats (one per musical bar).
Pauses: include gaps between words >= 300ms."""

        response = self._client.models.generate_content(
            model=self._model,
            contents=[
                self._types.Part.from_uri(file_uri=file_uri, mime_type=mime_type),
                timing_prompt,
            ],
        )

        json_text = response.text.strip()
        
        # Try to extract JSON from markdown fences if present
        if json_text.startswith("```"):
            import re
            match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", json_text)
            if match:
                json_text = match.group(1).strip()

        try:
            data = json.loads(json_text)
            return data
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed on first attempt: {e}. Retrying with stricter prompt...")
            
            # Retry with stricter prompt
            strict_prompt = """Return ONLY a valid JSON object. No explanations, no markdown, no extra text.
The JSON must match this exact structure:
{"duration_ms": 0, "speech_segments": [], "beats": [], "pauses": []}

Analyze the audio and populate the arrays."""

            retry_response = self._client.models.generate_content(
                model=self._model,
                contents=[
                    self._types.Part.from_uri(file_uri=file_uri, mime_type=mime_type),
                    strict_prompt,
                ],
            )

            retry_text = retry_response.text.strip()
            if retry_text.startswith("```"):
                import re
                match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", retry_text)
                if match:
                    retry_text = match.group(1).strip()

            try:
                data = json.loads(retry_text)
                return data
            except json.JSONDecodeError as retry_e:
                raise ValueError(
                    f"Gemini returned malformed JSON after retry. "
                    f"Original error: {e}. Retry error: {retry_e}. "
                    f"Response:\n{retry_text}"
                ) from retry_e

    def _extract_emotion(self, file_uri: str, mime_type: str) -> str:
        """Pass 2: Extract dominant emotion from audio.
        
        Args:
            file_uri: Full Gemini file URI (e.g., "https://generativelanguage.googleapis.com/v1beta/files/abc123")
            mime_type: MIME type of the audio file
            
        Returns:
            Emotion string: "happy", "sad", "excited", "neutral", or "solemn"
        """
        emotion_prompt = """Listen to this audio. What is the dominant emotional tone?
Return ONLY one word from: happy, sad, excited, neutral, solemn"""

        response = self._client.models.generate_content(
            model=self._model,
            contents=[
                self._types.Part.from_uri(file_uri=file_uri, mime_type=mime_type),
                emotion_prompt,
            ],
        )

        emotion = response.text.strip().lower()
        
        # Validate emotion is one of the expected values
        valid_emotions = {"happy", "sad", "excited", "neutral", "solemn"}
        if emotion not in valid_emotions:
            logger.warning(f"Unexpected emotion value '{emotion}', defaulting to 'neutral'")
            emotion = "neutral"

        return emotion


class OpenAIAudioProvider(AudioAnalysisProvider):
    """Audio analysis provider backed by OpenAI (gpt-4o-audio-preview).

    Uses the OpenAI audio preview model with base64-encoded inline audio content.
    No file upload needed; audio is passed directly in the API call.

    API key is read from the OPENAI_API_KEY environment variable.

    Raises:
        EnvironmentError: If no API key is found in the environment.
        ImportError: If the openai package is not installed.
    """

    MODEL = "gpt-4o-audio-preview"
    
    # MIME type mappings for audio file extensions
    _MIME_TYPES = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
        ".flac": "audio/flac",
    }

    def __init__(self, api_key: str = None, model: str = None):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai is required for OpenAIAudioProvider. "
                "Install it with: pip install openai"
            ) from exc

        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            raise EnvironmentError(
                "No OpenAI API key found. Set the OPENAI_API_KEY environment variable."
            )

        self._client = OpenAI(api_key=api_key)
        self._model = model or self.MODEL

    def _get_audio_format(self, audio_path: str) -> str:
        """Determine audio format from file extension."""
        ext = os.path.splitext(audio_path.lower())[1]
        # OpenAI uses format names, not MIME types
        format_map = {
            ".mp3": "mp3",
            ".wav": "wav",
            ".m4a": "m4a",
            ".flac": "flac",
        }
        return format_map.get(ext, "mp3")

    def analyze_audio(self, audio_path: str, prompt: str = "") -> AudioAnalysis:
        """Analyze audio file using OpenAI audio preview API.

        Two-pass approach:
        - Pass 1: Extract structured timing data (speech/beats/pauses)
        - Pass 2: Determine dominant emotion

        Args:
            audio_path: Path to audio file
            prompt: Optional user guidance (currently unused, reserved for future)

        Returns:
            AudioAnalysis dataclass with complete timing and emotion data

        Raises:
            ValueError: If OpenAI returns malformed JSON or file doesn't exist
            FileNotFoundError: If audio_path doesn't exist
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        import base64
        
        # Read and encode audio as base64
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
        
        base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        audio_format = self._get_audio_format(audio_path)
        
        logger.info(f"Analyzing {audio_path} ({audio_format}) with OpenAI...")

        # Pass 1: Extract structured timing data
        timing_data = self._extract_timing_data(base64_audio, audio_format)

        # Pass 2: Extract emotion
        emotion = self._extract_emotion(base64_audio, audio_format)

        # Measure real duration independently
        measured_ms = _measure_audio_duration_ms(audio_path)
        openai_ms = timing_data.get("duration_ms", 0)

        if measured_ms is not None:
            if openai_ms > 0:
                ratio = abs(measured_ms - openai_ms) / openai_ms
                if ratio > 0.10:
                    logger.warning(
                        f"OpenAI reported duration {openai_ms}ms but measured {measured_ms}ms "
                        f"({ratio:.0%} discrepancy). Using measured value."
                    )
            duration_ms = measured_ms
        else:
            logger.warning("Could not measure audio duration; falling back to OpenAI's reported value.")
            duration_ms = openai_ms

        # Build AudioAnalysis from results
        analysis = AudioAnalysis(
            speech_segments=[
                WordTiming(**seg) for seg in timing_data.get("speech_segments", [])
            ],
            beats=[
                BeatEvent(**beat) for beat in timing_data.get("beats", [])
            ],
            pauses=[
                PauseSegment(**pause) for pause in timing_data.get("pauses", [])
            ],
            emotion=emotion,
            duration_ms=duration_ms,
            audio_path=audio_path,
        )

        logger.info(
            f"Analysis complete: {len(analysis.speech_segments)} words, "
            f"{len(analysis.beats)} beats, {len(analysis.pauses)} pauses, "
            f"emotion={emotion}, duration={analysis.duration_ms}ms"
        )

        return analysis

    def _extract_timing_data(self, base64_audio: str, audio_format: str) -> dict:
        """Pass 1: Extract structured timing data from audio.
        
        Args:
            base64_audio: Base64-encoded audio data
            audio_format: Audio format string (e.g., "mp3", "wav")
            
        Returns:
            Dict with duration_ms, speech_segments, beats, pauses
            
        Raises:
            ValueError: If JSON parsing fails after retry
        """
        timing_prompt = """Analyze this audio file. Return ONLY valid JSON in this exact format:
{
  "duration_ms": <int>,
  "speech_segments": [
    {"word": "<word>", "start_ms": <int>, "end_ms": <int>, "phoneme_group": "<bilabial|open_vowel|spread_vowel|round_vowel|neutral>"}
  ],
  "beats": [
    {"time_ms": <int>, "strength": "<strong|bar1|normal>"}
  ],
  "pauses": [
    {"start_ms": <int>, "end_ms": <int>, "duration_ms": <int>}
  ]
}

Phoneme group rules — classify by the DOMINANT VOWEL sound in the word, not the starting consonant:
- round_vowel: words whose most prominent sound is OO or OH (e.g., "boo", "moon", "ghost", "spooky", "no", "oh", "go")
- open_vowel: words whose most prominent sound is AH, AA, or AW (e.g., "ahh", "ha", "bat", "father", "scary")
- spread_vowel: words whose most prominent sound is EE or IH (e.g., "eek", "see", "think", "it", "teeth")
- bilabial: ONLY words where lip-closure is the dominant feature — sustained humming or pure consonant sounds (e.g., "mmm", "bam", "pop"). Do NOT classify vowel-dominant words like "boo" as bilabial just because they start with B or M.
- neutral: all others (consonant clusters, unstressed syllables, unclear vowels)

Beat detection: only include beats if audio has musical rhythm. Bar 1 beats are the strongest downbeats (one per musical bar).
Pauses: include gaps between words >= 300ms."""

        response = self._client.chat.completions.create(
            model=self._model,
            modalities=["text"],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": base64_audio,
                                "format": audio_format
                            }
                        },
                        {
                            "type": "text",
                            "text": timing_prompt
                        }
                    ]
                }
            ]
        )

        json_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from markdown fences if present
        if json_text.startswith("```"):
            import re
            match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", json_text)
            if match:
                json_text = match.group(1).strip()

        try:
            data = json.loads(json_text)
            return data
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed on first attempt: {e}. Retrying with stricter prompt...")
            
            # Retry with stricter prompt
            strict_prompt = """Return ONLY a valid JSON object. No explanations, no markdown, no extra text.
The JSON must match this exact structure:
{"duration_ms": 0, "speech_segments": [], "beats": [], "pauses": []}

Analyze the audio and populate the arrays."""

            retry_response = self._client.chat.completions.create(
                model=self._model,
                modalities=["text"],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_audio",
                                "input_audio": {
                                    "data": base64_audio,
                                    "format": audio_format
                                }
                            },
                            {
                                "type": "text",
                                "text": strict_prompt
                            }
                        ]
                    }
                ]
            )

            retry_text = retry_response.choices[0].message.content.strip()
            if retry_text.startswith("```"):
                import re
                match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", retry_text)
                if match:
                    retry_text = match.group(1).strip()

            try:
                data = json.loads(retry_text)
                return data
            except json.JSONDecodeError as retry_e:
                raise ValueError(
                    f"OpenAI returned malformed JSON after retry. "
                    f"Original error: {e}. Retry error: {retry_e}. "
                    f"Response:\n{retry_text}"
                ) from retry_e

    def _extract_emotion(self, base64_audio: str, audio_format: str) -> str:
        """Pass 2: Extract dominant emotion from audio.
        
        Args:
            base64_audio: Base64-encoded audio data
            audio_format: Audio format string (e.g., "mp3", "wav")
            
        Returns:
            Emotion string: "happy", "sad", "excited", "neutral", or "solemn"
        """
        emotion_prompt = """Listen to this audio. What is the dominant emotional tone?
Return ONLY one word from: happy, sad, excited, neutral, solemn"""

        response = self._client.chat.completions.create(
            model=self._model,
            modalities=["text"],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": base64_audio,
                                "format": audio_format
                            }
                        },
                        {
                            "type": "text",
                            "text": emotion_prompt
                        }
                    ]
                }
            ]
        )

        emotion = response.choices[0].message.content.strip().lower()
        
        # Validate emotion is one of the expected values
        valid_emotions = {"happy", "sad", "excited", "neutral", "solemn"}
        if emotion not in valid_emotions:
            logger.warning(f"Unexpected emotion value '{emotion}', defaulting to 'neutral'")
            emotion = "neutral"

        return emotion


def get_provider(name: str = "gemini", **kwargs) -> AudioAnalysisProvider:
    """Factory function to create an audio analysis provider.

    Args:
        name: Provider name. Supported: "gemini", "openai".
        **kwargs: Additional keyword arguments passed to the provider constructor.

    Returns:
        AudioAnalysisProvider instance

    Raises:
        ValueError: If provider name is unknown
    """
    if name == "gemini":
        return GeminiAudioProvider(**kwargs)
    elif name == "openai":
        return OpenAIAudioProvider(**kwargs)
    raise ValueError(f"Unknown audio analysis provider: {name}")
