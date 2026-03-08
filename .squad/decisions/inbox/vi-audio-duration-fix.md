# Decision: Always Measure Audio Duration Independently

**Author:** Vi  
**Date:** 2025-07-27  
**Status:** Accepted  

## Context

`GeminiAudioProvider.analyze_audio()` was consuming `duration_ms` directly from Gemini's JSON response. `gemini-flash-latest` was observed returning ~35 s for a 152 s audio file, causing the entire generated lipsync animation to be truncated at the wrong length.

## Decision

Audio file duration **must always be measured independently** using a dedicated library (`mutagen`, falling back to the `wave` stdlib module for .wav). The measured value always overrides whatever the AI API reports. If the discrepancy between the measured value and the AI-reported value is >10%, a `WARNING` is logged.

## Rationale

AI models process media and can hallucinate or truncate metadata fields like `duration_ms`. Measuring duration from the actual file bytes is deterministic, free, and takes <1 ms — there is no reason to trust the AI's self-report over a direct measurement.

## Implementation

- `_measure_audio_duration_ms(audio_path)` added to `skill/audio_analyzer.py`
- Called in `GeminiAudioProvider.analyze_audio()` immediately after both Gemini passes complete
- `mutagen>=1.45.0` added to `requirements.txt`

## Scope

Applies to all current and future `AudioAnalysisProvider` implementations. Any provider that accepts an `audio_path` should apply the same measured-duration override pattern.
