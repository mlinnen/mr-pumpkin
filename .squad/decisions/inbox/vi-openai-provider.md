# Decision: OpenAI Provider for Audio Analysis and Timeline Generation

**Date:** 2026-03-08  
**Decider:** Vi (Backend Dev)  
**Issue:** #81  
**PR:** #82

## Context

The lipsync pipeline exclusively used Gemini for both audio analysis (Pass 1) and timeline generation (Pass 2). When Gemini quota is exhausted, the entire pipeline fails with no fallback option.

## Decision

Add OpenAI as an alternative provider for both pipeline stages:

1. **OpenAIProvider** — Timeline generation using `gpt-4o`
2. **OpenAIAudioProvider** — Audio analysis using `gpt-4o-audio-preview`

## Implementation

### OpenAIProvider (skill/generator.py)
- Uses OpenAI chat completions API with `gpt-4o` model
- Auth via `OPENAI_API_KEY` environment variable
- Messages format: system + user messages array
- Base URL configurable (defaults to `https://api.openai.com/v1`)
- Implements same `LLMProvider` ABC as `GeminiProvider`

### OpenAIAudioProvider (skill/audio_analyzer.py)
- Uses `gpt-4o-audio-preview` model with audio preview API
- **Key difference from Gemini:** Base64-encoded inline audio content (NO file upload)
- Two-pass approach: Pass 1 extracts timing JSON, Pass 2 extracts emotion
- Audio format: `{"type": "input_audio", "input_audio": {"data": base64, "format": "mp3"}}`
- Implements same `AudioAnalysisProvider` ABC as `GeminiAudioProvider`

### CLI Integration (skill/lipsync_cli.py)
- `--provider openai` selects OpenAI for timeline generation
- `--audio-provider openai` selects OpenAI for audio analysis
- Both args can be mixed: `--audio-provider gemini --provider openai` is valid

### Dependencies (requirements.txt)
- Added `openai>=1.0.0`

## Rationale

1. **Quota exhaustion resilience** — When Gemini hits quota limits, users can switch to OpenAI without code changes
2. **Interface consistency** — Both OpenAI providers follow exact same ABC pattern as Gemini providers (LLMProvider, AudioAnalysisProvider)
3. **Simpler audio handling** — OpenAI's inline base64 approach avoids Gemini's upload-poll-delete lifecycle complexity
4. **Model quality** — `gpt-4o` has strong JSON instruction-following; `gpt-4o-audio-preview` supports multimodal audio analysis
5. **Future extensibility** — Factory pattern in `get_provider()` and lipsync_cli allows adding more providers (Whisper, Claude, etc.) with minimal changes

## Key Technical Decisions

### Base64 vs File Upload
- **Gemini approach:** Upload file, poll until ACTIVE, use file URI, delete file in finally block
- **OpenAI approach:** Read file bytes, base64 encode, send inline in single API call
- **Why OpenAI is simpler:** No async state management, no file cleanup, no polling loop

### Format Naming Inconsistency
- Gemini uses MIME types: `"audio/mpeg"`, `"audio/wav"`
- OpenAI uses format names: `"mp3"`, `"wav"`
- Handled via separate helper methods: `_get_mime_type()` vs `_get_audio_format()`

### Error Handling Parity
- Both providers implement same error patterns:
  - `EnvironmentError` for missing API key
  - `ImportError` if SDK package not installed
  - JSON retry logic with markdown fence stripping
  - Emotion validation against fixed set

## Test Coverage

- **OpenAIProvider:** 6 tests (text generation, chat format, model name, env key, missing key, custom URL)
- **OpenAIAudioProvider:** 7 tests (AudioAnalysis return, base64 encoding, model name, speech segments, JSON retry, missing key, emotion)
- All 13 tests pass

## Usage Examples

```bash
# Use OpenAI for both passes
python -m skill.lipsync_cli audio.mp3 --audio-provider openai --provider openai

# Mix providers: Gemini for audio, OpenAI for timeline
python -m skill.lipsync_cli audio.mp3 --audio-provider gemini --provider openai

# Dry-run to test without upload
python -m skill.lipsync_cli audio.mp3 --audio-provider openai --provider openai --dry-run
```

## Trade-offs

### Pros
- Quota exhaustion resilience
- Simpler audio handling (no file upload lifecycle)
- Strong JSON instruction-following from gpt-4o
- Clean interface consistency with existing Gemini providers

### Cons
- Requires `OPENAI_API_KEY` in addition to `GEMINI_API_KEY`
- OpenAI audio preview API doesn't support `.ogg` format in base64 mode
- Adds dependency on `openai>=1.0.0` package

## Alternatives Considered

1. **Retry with exponential backoff on Gemini quota errors**
   - Rejected: Doesn't solve quota limits, just delays failure

2. **Add only OpenAIProvider (timeline generation), keep Gemini for audio**
   - Rejected: Audio analysis is where quota exhaustion happens most (larger model, file upload overhead)

3. **Use Whisper API for audio analysis instead of gpt-4o-audio-preview**
   - Rejected: Whisper only does transcription, not phoneme classification or beat detection

## Future Considerations

- Add automatic fallback: try Gemini first, catch quota error, retry with OpenAI
- Add cost logging: track API usage per provider for cost comparison
- Add Anthropic Claude provider when multimodal audio support is available
- Consider OpenAI Whisper for transcription-only use cases (cheaper than gpt-4o-audio-preview)

## Notes

- Both providers use same JSON retry logic: attempt parse, strip markdown fences, strict retry, then raise
- Emotion validation critical for both: LLMs often return verbose responses ("The dominant emotion is happy") instead of single word
- Base64 encoding happens in-memory — no temp files, no file handle leaking to API
- OpenAI audio preview model is in beta — API may change (version pinned in requirements.txt to prevent breaks)
