# Decision: Lip-sync mouth-close timing fix

**Date:** 2025-07-28  
**Author:** Vi (Backend Dev)  
**Status:** Implemented

## Problem

When a song contained repeated words with gaps (e.g., "Spooks, Spooks, Spooks, Spooks"), the pumpkin's mouth stayed open between words instead of closing during silence. Root causes were two-fold:

1. `_SYSTEM_PROMPT` in `skill/generator.py` had no example demonstrating the open→close→silence→open mouth pattern.
2. `build_lipsync_prompt` in `skill/lipsync_cli.py` only told the LLM *when* a mouth viseme opened; it never emitted an explicit `mouth_closed` event at `end_ms`.

## Decision

### Fix 1 — Add lip-sync example to `_SYSTEM_PROMPT` (`skill/generator.py`)

Added **Example 3 — lip-synced words with gaps** to `_SYSTEM_PROMPT` immediately before the "Now generate..." line. The example shows:
- `mouth_rounded` at word start → `mouth_closed` at word end
- Silence gap with mouth closed
- Second word opens again
- `mouth_neutral` after final word to return mouth to expression-driven control

Rationale: LLMs follow concrete examples more reliably than abstract instructions alone.

### Fix 2 — Explicit close events in `build_lipsync_prompt` (`skill/lipsync_cli.py`)

Changed per-word timing lines from:
```
  - 0ms-500ms: "Spooks" [round_vowel → mouth rounded]
```
to an explicit two-line format:
```
  - 0ms: mouth_rounded → "Spooks" (round_vowel)
  - 500ms: mouth_closed  ← word ends, return to closed
```

Added two new numbered instructions:
- **7.** After EVERY word's end_ms, immediately emit `mouth_closed` to prevent the mouth hanging open between words.
- **8.** After the final word ends, emit `mouth_neutral` to return mouth to expression-driven control.

Added `_phoneme_to_viseme_cmd()` helper returning the exact command name (e.g., `mouth_rounded`) for use in the new prompt format.

## Files Changed

- `skill/generator.py` — added Example 3 to `_SYSTEM_PROMPT`
- `skill/lipsync_cli.py` — rewrote word-timing prompt format, added instructions 7 & 8, added `_phoneme_to_viseme_cmd()`

## Verification

All 60 existing tests in `test_skill_generator.py` and `test_lipsync_cli.py` pass with no regressions.
