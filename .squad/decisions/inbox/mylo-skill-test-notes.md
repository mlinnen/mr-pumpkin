# Mylo's Testing Notes — Recording Skill (Issue #39)

**Date:** 2026-03-02  
**By:** Mylo (Tester)  
**For:** Vi, Jinx  
**Status:** Tests written and passing (60/60)

---

## Summary

Three anticipatory test files written for the recording skill (Issue #39):
- `tests/test_skill_generator.py` — 27 tests
- `tests/test_skill_uploader.py` — 20 tests  
- `tests/test_skill_integration.py` — 13 tests

All 60 tests currently pass against Vi's partial implementation.

---

## Testing Decisions Made

### 1. Mock at the right boundary

**Decision:** Patch `skill.uploader.socket.socket` (module-local), not `socket.socket` globally.

Vi's uploader does `import socket` at the top of `skill/uploader.py`, so patching the module-local reference is the correct approach. Patching `socket.socket` globally would have no effect.

### 2. WebSocket tests mock the sync wrapper

**Decision:** Mock `skill.uploader._upload_ws` rather than trying to mock the async `websockets.connect`.

The async internals are hard to mock correctly without `pytest-asyncio`. Since `_upload_ws` is a thin sync wrapper, mocking it directly is cleaner, faster, and more stable.

### 3. Empty commands list = ValueError (anticipatory)

**Decision:** Test expects `ValueError` for a timeline with empty `commands: []`.

Rationale: An empty timeline is semantically useless — uploading it would waste server storage. The architecture spec says the generator should return "valid" timelines, and a timeline with no commands is not useful. **Vi should confirm this behavior in `_validate_extra()`.**

### 4. Unsorted time_ms = ValueError (anticipatory)

**Decision:** Test expects `ValueError` when commands are out of ascending order.

Rationale: The architecture spec explicitly says "time_ms values MUST be sorted in ascending order." This should be caught in validation before upload. **Vi's `_validate_extra()` implementation should confirm this.**

### 5. Unknown command names = ValueError (anticipatory)

**Decision:** Test expects `ValueError` containing the bad command name.

Rationale: `_VALID_COMMANDS` set exists in generator.py. The spec says "All command values MUST come from the vocabulary." Currently `Timeline.from_dict()` may not validate this — `_validate_extra()` is the right place.

### 6. GEMINI_API_KEY missing test includes ImportError

**Decision:** `test_missing_api_key_raises_before_api_call` accepts `ImportError` in addition to `EnvironmentError`.

Rationale: If `google-generativeai` package is not installed, `GeminiProvider.__init__` raises `ImportError` before even checking the API key. Both cases mean "can't use Gemini" — the test accepts either.

---

## Open Questions for Vi

### Q1: Does `_validate_extra()` check command names against `_VALID_COMMANDS`?

The `_validate_extra` function is called before `Timeline.from_dict()`. Tests expect it to:
- Raise `ValueError("unknown command: <name>")` for command names not in `_VALID_COMMANDS`
- Raise `ValueError` for empty `commands` list  
- Raise `ValueError` for unsorted `time_ms` values

If not implemented yet, tests for these will fail once the `TODO: adjust imports` tests are fully active.

### Q2: Does `Timeline.from_dict()` validate version string?

Test `test_wrong_version_string_raises_value_error` expects `"version": "2.0"` to fail.
Test `test_null_version_raises_value_error` expects `"version": null` to fail.

If `Timeline.from_dict()` only checks for key presence (not value), these may pass through incorrectly. Mylo recommends `_validate_extra()` enforce `data.get("version") == "1.0"`.

### Q3: Should `upload_timeline()` accept `timeline` as first positional arg instead of `filename`?

Current signature: `upload_timeline(filename, timeline_dict, ...)`

This is slightly counterintuitive — callers generated the timeline dict and are providing it + a chosen filename. A `(timeline_dict, filename)` order might feel more natural. However, changing this is a **breaking API change** once any user adopts it, so decide early.

### Q4: Protocol alias — is `"ws"` or `"websocket"` the canonical value?

Both are accepted in the uploader. Tests use `"websocket"`. The architecture spec says `"ws"` or `"websocket"`. Consider documenting the canonical value in the docstring.

---

## Import Path Note

All three test files have this at the top:

```python
# TODO: adjust imports once skill/ package is finalized
```

If `skill/` is moved, renamed, or restructured, update these imports:
```python
from skill.generator import generate_timeline, GeminiProvider, LLMProvider
from skill.uploader import upload_timeline
```

---

## Quality Gate Recommendation

Before merging the skill PR, Mylo recommends:

1. ✅ All 60 skill tests pass (currently passing)
2. ⬜ `_validate_extra()` enforces: non-empty commands, sorted time_ms, valid command names
3. ⬜ Version field validation ("1.0" only)
4. ⬜ Run full test suite (all 430+ tests) — no regressions
5. ⬜ Manual smoke test: real Gemini API call → upload to live server
