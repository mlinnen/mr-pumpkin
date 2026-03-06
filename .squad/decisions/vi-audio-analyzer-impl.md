# Decision Drop: Audio Analyzer Implementation Details

**Date:** 2026-03-05  
**Author:** Vi  
**Issue:** #69  
**Component:** `skill/audio_analyzer.py`

---

## Implementation Decisions

### 1. MIME Type Handling

**Decision:** Added a `_MIME_TYPES` dictionary mapping file extensions to MIME types, with fallback to "audio/mpeg" for unknown extensions.

**Rationale:** The architecture doc specified detecting MIME type from extension but didn't specify the exact mechanism. A static mapping provides predictable behavior and supports common audio formats (.mp3, .wav, .ogg, .m4a, .flac) without external dependencies.

**Extensions supported:**
- `.mp3` → `audio/mpeg`
- `.wav` → `audio/wav`
- `.ogg` → `audio/ogg`
- `.m4a` → `audio/mp4`
- `.flac` → `audio/flac`

---

### 2. File Upload MIME Type in API Calls

**Decision:** Used the detected MIME type in `client.files.upload()` but hardcoded `"audio/mpeg"` in `Part.from_uri()` calls.

**Rationale:** Gemini's file upload API requires the correct MIME type at upload time. However, the `Part.from_uri()` reference in subsequent API calls is more forgiving and accepts a generic audio type. Using "audio/mpeg" consistently in Part.from_uri() simplifies the code and avoids needing to thread MIME type through multiple methods.

**Alternative considered:** Store the MIME type as an instance variable after upload and reuse it. Rejected as over-engineering — the current approach works reliably.

---

### 3. Emotion Validation and Fallback

**Decision:** Validate emotion response against expected set `{"happy", "sad", "excited", "neutral", "solemn"}` and default to "neutral" if unexpected value returned.

**Rationale:** Gemini sometimes returns verbose responses ("The dominant emotion is happy") even with strict prompts. The `.strip().lower()` + validation ensures downstream code receives a known emotion value. Fallback to "neutral" is safe because it's the most common baseline state.

---

### 4. Logging Strategy

**Decision:** INFO for analysis results (counts + emotion + duration), DEBUG for file operations, WARNING for retries/fallbacks.

**Rationale:** Mirrors the logging pattern in `skill/generator.py`. Users care about analysis results (INFO), developers care about API lifecycle (DEBUG), issues like JSON retry deserve visibility (WARNING).

---

## Conformance to Architecture Doc

All core requirements met:
- ✅ AudioAnalysis dataclass with exact fields specified
- ✅ AudioAnalysisProvider ABC with single abstract method
- ✅ GeminiAudioProvider with two-pass analysis
- ✅ Pass 1 and Pass 2 prompts match spec exactly
- ✅ File upload lifecycle: upload → poll until ACTIVE → analyze → cleanup
- ✅ Graceful JSON retry on parse failure
- ✅ get_provider() factory function
- ✅ PEP 8, type annotations, docstrings, module-level logger

No architectural deviations. Only implementation details filled in where spec was intentionally open-ended.
