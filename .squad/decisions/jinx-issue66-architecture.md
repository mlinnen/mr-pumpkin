# Architecture Decision: Issue #66 — Audio-to-Lip-Sync Recording Tool

**Date:** 2026-03-05  
**Author:** Jinx (Lead)  
**Status:** Proposed — implementation assigned to Vi  
**Issue:** [#66](https://github.com/mlinnen/mr-pumpkin/issues/66)

---

## Problem Statement

Mr. Pumpkin needs a pre-processing tool that accepts an audio file (speech, song, or story), analyzes it with an AI model (defaulting to Gemini), and produces a synchronized recording — a timeline JSON paired with the audio file — that makes Mr. Pumpkin look alive: lip-syncing speech, reacting to music beats, blinking naturally, and turning his head with intent.

---

## Existing Infrastructure Audit

| Component | What Exists |
|---|---|
| Timeline format | JSON `version 1.0` with `commands[]` — each has `time_ms`, `command`, optional `args` |
| Viseme system | 4 shapes: `closed`, `open`, `wide`, `rounded` + `neutral` (Issue #59) |
| All face commands | Expressions, blink/wink, gaze, eyebrows, head turns, nose — full vocabulary |
| `skill/` package | `generator.py` (LLM→timeline), `cli.py` (CLI), `uploader.py` (TCP/WS upload) |
| LLM abstraction | `LLMProvider` ABC + `GeminiProvider` — already pluggable |
| Audio upload | **Does not exist** |
| Audio playback | **Does not exist** |
| Gemini audio API | `google-genai` already in `requirements.txt` — multimodal audio supported |

The viseme infrastructure from Issue #59 is the critical enabler: the lip-sync command vocabulary is complete and ready to be driven programmatically. Zero new face-motion commands needed.

---

## Architecture Decision

### Overall Tool Design

New modules added to the existing `skill/` package:

```
skill/
  audio_analyzer.py     # AudioAnalysisProvider ABC + GeminiAudioProvider
  lipsync_cli.py        # CLI orchestrator: audio_file + prompt → analysis → timeline → upload
```

CLI usage:
```
python -m skill.lipsync_cli audio.mp3 --filename my_song [--prompt "pumpkin sings this joyfully"]
```

This slots cleanly alongside `skill/cli.py` (text-only tool) and reuses all existing infrastructure.

---

### Input → Output Pipeline

```
[audio.mp3]  +  [optional prompt]
      │
      ▼
AudioAnalysisProvider.analyze_audio()
      │  Returns: AudioAnalysis (timed phoneme groups, beats, pauses, emotion, duration_ms)
      ▼
LipsyncTimelineBuilder.build(analysis, prompt)
      │  Maps: phonemes→visemes, beats→eyebrows/head, pauses→blinks, emotion→expressions
      ▼
Timeline JSON (validated via existing Timeline.from_dict())
      │
      ├─► upload_audio("my_song", audio.mp3)   → server stores my_song.mp3
      └─► upload_timeline("my_song", timeline) → server stores my_song.json
```

Audio file and timeline share the same filename root. The server pairs them by convention.

---

### Timeline Format Extension

Add an **optional** `audio_file` top-level field to the timeline JSON:

```json
{
  "version": "1.0",
  "audio_file": "my_song.mp3",
  "duration_ms": 45000,
  "commands": [ ... ]
}
```

**Backward-compatible:** existing timelines without `audio_file` play exactly as before.  
When `audio_file` is present, the playback engine starts audio at t=0 in sync with the timeline via `pygame.mixer.music`.

**No new command added to the vocabulary** — audio is recording metadata, not a face-motion command.

---

### Gemini Audio Analysis Approach

Gemini `gemini-1.5-pro` (or `gemini-2.0-flash`) supports multimodal audio via the `google-genai` library already in `requirements.txt`. Strategy: **two-pass analysis**.

**Pass 1 — Audio structure** (Gemini multimodal):
- Upload raw audio file bytes via `client.files.upload()`
- Request structured JSON: word timings with start/end ms, beat positions, pause segments, dominant emotion
- Output: `AudioAnalysis` dataclass with `speech_segments`, `beats`, `pauses`, `emotion`, `duration_ms`

**Pass 2 — Artistic choreography** (Gemini text, reuses existing `generate_timeline()`):
- Build enriched prompt from `AudioAnalysis` + user prompt: `"At 0ms: 'Hello' [open viseme 200ms]. At 500ms: beat. Emotion: happy. Make Mr. Pumpkin look engaged and alive."`
- Pass to existing `LLMProvider.generate()` which returns complete timeline JSON
- LLM handles artistic judgment: head turn cadence, expression arcs, engagement patterns

Two-pass separates **structural analysis** (timing data) from **artistic choreography** (expression/gaze decisions) — maps cleanly onto two provider abstractions.

---

### Model-Agnostic Design

Two new ABCs following the exact pattern of the existing `LLMProvider`:

```python
class AudioAnalysisProvider(ABC):
    @abstractmethod
    def analyze_audio(self, audio_path: str, prompt: str) -> AudioAnalysis: ...

class GeminiAudioProvider(AudioAnalysisProvider):
    # Uses google-genai multimodal file upload
    MODEL = "gemini-1.5-pro"
```

CLI accepts `--provider` (for timeline generation) and `--audio-provider` (for audio analysis) flags independently. Allows mix-and-match: use Gemini for audio analysis, use any future text LLM for choreography.

---

### Audio-to-Face-Motion Mapping

| Audio Feature | Detection Method | Face Commands |
|---|---|---|
| Bilabial stop (M, B, P) | Gemini phoneme group | `mouth closed` |
| Open vowel (AH, AA, AW) | Gemini phoneme group | `mouth open` |
| Spread vowel (EE, IH) | Gemini phoneme group | `mouth wide` |
| Round vowel (OO, OH) | Gemini phoneme group | `mouth rounded` |
| Silence / pause ≥ 400ms | Timing gap | `blink` |
| Silence / pause ≥ 1000ms | Timing gap | `blink` + `gaze` shift |
| Beat (strong) | Gemini beat detection | `eyebrow_raise` + reset 200ms later |
| Beat (bar 1 / very strong) | Gemini beat detection | subtle head bob: `turn_up 30` + `center_head` |
| Emotion = happy/upbeat | Gemini tone analysis | `set_expression happy` |
| Emotion = sad/solemn | Gemini tone analysis | `set_expression sad` |
| Emotion = excited/tense | Gemini tone analysis | `set_expression surprised` |
| Sentence end | Pause + timing context | `gaze` shift (look around naturally) |
| Every ~8–15 seconds | Idle policy | `blink` (natural idle maintenance) |

---

### Audio File Upload (Server Changes)

Two additions to the server (both scoped to Vi):

1. **New upload command:** `upload_audio <filename>` — same multi-step TCP handshake as `upload_timeline`. Stores raw audio bytes as `<filename>.mp3` (or `.wav`) in `~/.mr-pumpkin/recordings/`.

2. **Playback integration:** When `Playback.start()` encounters a timeline with `audio_file` present, invoke `pygame.mixer.music.load()` + `.play()` at t=0. `Playback.stop()` also calls `pygame.mixer.music.stop()`.

---

### New Face-Motion Commands Needed

**None.** The entire face-motion vocabulary needed for lip-sync, beat reaction, and liveliness already exists from Issue #59 and earlier work. The only server-side addition is `upload_audio` (file storage, not a face animation command).

---

## Sub-Issue Breakdown

| Title | Owner | Notes |
|---|---|---|
| Add audio file upload endpoint to server | Vi | `upload_audio` TCP/WS command, store in recordings dir |
| Add audio playback to timeline engine | Vi | `pygame.mixer` in `Playback`, `audio_file` field in `Timeline.from_dict()` |
| Build `skill/audio_analyzer.py` | Vi | `AudioAnalysisProvider` ABC, `GeminiAudioProvider`, `AudioAnalysis` dataclass |
| Build `skill/lipsync_cli.py` | Vi | CLI orchestrator: analysis → timeline → dual upload |
| Tests: audio_analyzer module | Mylo | Mock Gemini responses, assert correct phoneme/beat/pause extraction |
| Tests: lipsync_cli end-to-end | Mylo | Mock AudioAnalysisProvider + mock uploader, assert timeline structure |
| Update timeline-schema.md for `audio_file` field | Jinx | Documentation — after Vi's implementation is merged |

---

## Risk Notes

- **Gemini timing precision:** Word-timing output granularity is ~50–200ms. The 0.15 viseme transition speed handles ±100ms slop gracefully — acceptable.
- **Beat detection reliability:** Gemini is not a DAW. For rhythmic content, a dedicated "list beat timestamps as JSON" prompt (Pass 1B) is more reliable than a combined single-pass request.
- **Audio codec support:** `pygame.mixer` supports MP3, OGG, WAV. The CLI and uploader documentation should specify accepted formats.
- **Large file uploads:** Long clips (>3 min) can be large. The `upload_audio` handler should use chunked sending, not a single `sendall()`.

---

## Implementation Sequencing

1. Vi: Timeline format extension (`audio_file` field) + `pygame.mixer` playback integration
2. Vi: Audio upload endpoint (parallel with #1 once schema locked)
3. Vi: `skill/audio_analyzer.py` — Gemini multimodal audio analysis
4. Vi: `skill/lipsync_cli.py` — CLI orchestrator (depends on 1–3)
5. Mylo: Tests (stubs early; fill in once Vi's modules exist)
6. Jinx: `timeline-schema.md` doc update (last)
