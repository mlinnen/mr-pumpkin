# Skill: Audio-to-Animation Mapping

**Category:** Architecture / AI integration  
**First applied:** Issue #66 — Audio lip-sync recording tool  
**Author:** Jinx

---

## Pattern Description

Map audio features from an AI-analyzed audio file to face-motion commands in a timeline recording, producing a synchronized animation that makes a character look alive.

---

## The Pattern

Audio analysis produces structured timing data. That data maps to face-motion commands via deterministic rules. An LLM then handles the artistic layer (expression arcs, engagement choreography) using the timing data as context.

### Two-Pass Architecture

**Pass 1 — Structural analysis** (dedicated `AudioAnalysisProvider`):
- Upload audio to Gemini multimodal API
- Request JSON: word timings (start_ms, end_ms, phoneme_group), beat positions, pause segments, dominant emotion
- Output: `AudioAnalysis` dataclass

**Pass 2 — Artistic choreography** (existing `LLMProvider`):
- Build enriched prompt from `AudioAnalysis` (timed events as context)
- Existing `generate_timeline()` produces the complete timeline JSON
- LLM decides expression arcs, head turn timing, engagement patterns

### Deterministic Mapping Table

| Audio Feature | → | Face Command |
|---|---|---|
| Bilabial stop (M/B/P) | | `mouth closed` |
| Open vowel (AH/AA) | | `mouth open` |
| Spread vowel (EE/IH) | | `mouth wide` |
| Round vowel (OO/OH) | | `mouth rounded` |
| Pause ≥ 400ms | | `blink` |
| Pause ≥ 1000ms | | `blink` + `gaze` shift |
| Beat (strong) | | `eyebrow_raise` + reset |
| Beat (bar 1) | | subtle head bob (`turn_up 30` + `center_head`) |
| Silence at sentence end | | `gaze` shift (look around) |
| Idle (every ~10s) | | `blink` |
| Emotion = happy | | `set_expression happy` |
| Emotion = sad | | `set_expression sad` |
| Emotion = excited | | `set_expression surprised` |

---

## Provider Abstraction

```python
class AudioAnalysisProvider(ABC):
    @abstractmethod
    def analyze_audio(self, audio_path: str, prompt: str) -> AudioAnalysis: ...

class GeminiAudioProvider(AudioAnalysisProvider):
    MODEL = "gemini-1.5-pro"
    # Uses google-genai client.files.upload() for multimodal audio
```

Mirrors the existing `LLMProvider` ABC in `skill/generator.py`. Same pluggability pattern: default provider is Gemini, CLI flag `--audio-provider` allows swapping.

---

## Paired File Convention

Audio file and timeline JSON share a filename root:
- `my_song.mp3` — audio stored in `~/.mr-pumpkin/recordings/`
- `my_song.json` — timeline with optional `audio_file: "my_song.mp3"` metadata field

Playback engine checks `audio_file` field and starts `pygame.mixer.music` at t=0.

---

## When to Apply This Pattern

- Any time audio is the primary input and facial animation is the desired output
- Applicable to speech (dialog, story), music (singing, beat-driven), or ambient audio
- Works for any character with: viseme system, blink, gaze, expressive state machine, head movement

---

## Gotchas

- Gemini timing precision is ~50–200ms — design viseme transitions to be tolerant of this slop (fast transition speed like 0.15 works well)
- Beat detection via Gemini works best as a separate explicit request ("list beat timestamps") rather than bundled into a single combined analysis prompt
- Large audio files need chunked upload, not a single `sendall()`
- Always validate that generated timeline `duration_ms` ≥ audio file duration
