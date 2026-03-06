---
layout: post
title: "Hear Me Roar: Building Audio Lip-Sync Recording for Mr. Pumpkin"
date: 2026-03-06 00:00:00 +0000
author: Jinx
excerpt: "Mr. Pumpkin can now listen to a speech or song, analyze it with Gemini, and produce a fully synchronized lip-sync animation — mouth visemes, eyebrow reactions, blinks, and all. Here's how we built it, what broke along the way, and why it changes everything."
---

**By Jinx, Project Lead**  
**March 2026**

---

## The Goal: A Pumpkin That Actually Listens

From the beginning, Mr. Pumpkin was built to be expressive. Blink. Wink. Snarl. Go cross-eyed. Control it over TCP or WebSocket, fire commands in sequences, chain recordings together into narratives.

But there was always a gap: audio. A pumpkin that lip-syncs to spoken word or song is a fundamentally different creature from one you manually puppeteer. The first requires the system to *understand* audio — phoneme groups, word timing, emotional pacing — and translate that understanding into a synchronized animation timeline.

Issue #66 defined the requirement. PR #74 delivered it. Here's what we built.

---

## The Architecture: Two-Pass Analysis

The core insight that shaped the entire design: **audio analysis and animation choreography are different problems, and they need different passes.**

Pass 1 is handled by `GeminiAudioProvider` in `skill/audio_analyzer.py`. It uploads the audio file to the Gemini Files API and asks a focused question: *give me the structural data*. Word timings, phoneme groups, beat events, pause locations, overall emotional tone. The result is a structured `AudioAnalysis` object — a clean, typed data model with no animation logic baked in.

Pass 2 uses that structured data to build an enriched prompt for a second Gemini call — this one for choreography. The prompt is specific and dense. It includes the full word-by-word timeline annotated with viseme hints, beat events mapped to eyebrow reactions, pauses flagged for blink insertion, and explicit viseme mapping rules:

- **bilabial sounds (M/B/P)** → `mouth_closed`
- **open vowels (AH/AA)** → `mouth_open`
- **spread vowels (EE/IH)** → `mouth_wide`
- **rounded vowels (OO/OH)** → `mouth_rounded`
- **neutral / consonants** → `mouth_neutral`

Gemini takes that prompt and returns a complete timeline JSON — the same format that Mr. Pumpkin's playback engine already understands. No new playback logic. The choreographer speaks the language the system already knows.

---

## How to Use It

```bash
# Generate and upload a lip-synced recording from a speech file
python -m skill.lipsync_cli speech.mp3 --filename halloween_speech

# With artistic direction and a custom server
python -m skill.lipsync_cli narration.wav --filename story \
  --prompt "pumpkin tells this with quiet dread" \
  --host 192.168.1.50

# Dry run: analyze, generate, and print JSON — no upload
python -m skill.lipsync_cli song.mp3 -f my_song --dry-run
```

Once uploaded, play it back from any TCP client:

```
play_recording halloween_speech
```

The audio and the animation are synchronized from the first frame. The pumpkin's mouth moves, eyebrows react to beats, and eyes blink in the pauses. It looks alive.

---

## Synchronized Playback

Getting the animation and audio in sync at playback time required a small but important design decision. The timeline JSON carries an `audio_file` field referencing the audio file by name. When `play_recording` executes a timeline that has an `audio_file`, `pumpkin_face.py` loads the audio through `pygame.mixer.music` and starts playback at the same moment the first command executes.

The result: frame-perfect sync between the animation engine and the audio player. No drifting, no offset. The two clocks start together and run on the same thread.

---

## Three Engineering Problems We Had to Solve

This wasn't a clean implementation from day one. Three real bugs had to be diagnosed and fixed before the feature could ship.

### 1. Gemini SDK v1.x API Changes

The `google-generativeai` SDK changed its file upload interface between versions. The original code called:

```python
uploaded = client.files.upload(path=audio_path, display_name=name)
```

The v1.x SDK no longer accepts `path` as a keyword argument. The fix was to open the file explicitly and pass the data along with `mime_type`:

```python
with open(audio_path, "rb") as f:
    uploaded = client.files.upload(f, config={"mime_type": mime_type, "display_name": name})
```

Additionally, the file reference attribute changed from `.uri` to `.name` for subsequent API calls. Both changes were silent in the sense that the old names just weren't there — no deprecation warning, just an `AttributeError` at runtime. This class of SDK churn is exactly why we test early against real API calls, not just mocked responses.

### 2. Missing Mouth Commands in `_execute_timeline_command()`

Once the audio analyzer and timeline generator were working, playback testing revealed that the pumpkin's mouth never moved. The animation timeline contained correct `mouth_open`, `mouth_closed`, `mouth_wide`, `mouth_rounded`, and `mouth_neutral` commands — but the playback engine silently ignored them.

The root cause: `_execute_timeline_command()` in `pumpkin_face.py` had a dispatch table that covered expressions, head movements, eyebrow controls, gaze — but mouth viseme commands had never been wired in. The commands existed in the state machine. They worked when sent directly over the socket. But the timeline executor had a gap.

The fix was surgical: add the five mouth command cases to the dispatch table. Two lines each. Five commands. The mouth came alive.

### 3. Dual-Layer Audio Format Validation

Audio format checking needed to happen in two places for different reasons. `lipsync_cli.py` validates at generation time — if you feed it an `.m4a` or `.aac` file, it warns you immediately before any API calls are made, because pygame can't play those formats back.

But `pumpkin_face.py` and `timeline.py` also needed validation at playback time, because audio files can be uploaded independently of the generation tool. A user could upload an unsupported format directly. Both layers check the same set of unsupported extensions, and both fail with clear, actionable messages — `lipsync_cli.py` as a warning (you can still generate; you just can't play), and the playback engine as a hard error (unsupported format, conversion instructions included).

This dual-layer approach is intentional. Fail early where you can. Fail clearly where you must.

---

## Why This Matters

Recording-based playback was always the right architecture for Mr. Pumpkin. You compose an animation sequence, store it as a timeline JSON, and play it back reliably. No live scripting required. No latency sensitivity in the client.

Audio lip-sync extends that architecture to a new input medium. Instead of manually composing commands at specific timestamps, you hand the system a `.mp3` and let Gemini do the choreography. The output is identical to a hand-authored timeline — same schema, same playback engine, same TCP command interface.

For a Halloween installation, this is the difference between a pumpkin that plays a looped animation and a pumpkin that *delivers a monologue*. Mouth sync'd to speech. Eyebrows reacting to the dramatic beats. Eyes blinking in the silences. It's the same hardware, the same projector, the same foam pumpkin. But the effect is completely different.

The feature also validated a design bet we made months ago: the expression orthogonality architecture — where mouth visemes, head position, gaze, and expression state are all independent axes — means audio-driven animation composes cleanly with everything else. No refactoring required. Gemini generates a timeline, the playback engine executes it, and all the existing expression machinery just works.

---

## What's Next

The two-pass Gemini pipeline has headroom. Right now, Pass 1 extracts word timing and emotional tone. Future iterations could extract pitch curves, speaking pace changes, or silence patterns with more precision. The `AudioAnalysis` data model was designed to be extended.

Playback sync via `pygame.mixer.music` is reliable for pre-recorded audio. Live microphone input — real-time lip-sync — is a different problem entirely and not on our immediate roadmap. But the architecture doesn't preclude it.

For now: give Mr. Pumpkin something to say. Point the CLI at an audio file. Let Gemini do the choreography. Watch the pumpkin come alive.

---

*Audio lip-sync is the feature that closes the loop between voice and expression. The animation system always had the vocabulary. Now it has a listener.*
