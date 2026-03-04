# Mouth Commands Documentation

**By:** Jinx (Lead)  
**Date:** 2026-03-03  
**Status:** Complete

## Summary

Updated `docs/timeline-schema.md` to document the 6 mouth viseme commands introduced in Issue #59 implementation (Li-sync speech control).

## What Changed

Added a new `### Mouth` section to the **Command Vocabulary** in `timeline-schema.md`, positioned after the Nose section. The documentation covers:

1. **Five shorthand commands** (no arguments required):
   - `mouth_closed` — Lips together (M, B, P sounds)
   - `mouth_open` — Open jaw (AH, AA sounds)
   - `mouth_wide` — Wide spread lips (EE, IH sounds)
   - `mouth_rounded` — Rounded lips (OO, OH sounds)
   - `mouth_neutral` — Release mouth to expression-driven control

2. **One compact syntax command** (parameterized):
   - `mouth` — Set by viseme name: `closed|open|wide|rounded|neutral`

3. **Usage note:** "Use mouth commands to synchronize facial animation with speech synthesis. Viseme-based mouth shapes support natural lip-sync during dialogue."

## Why

Issue #59 implemented mouth speech control in the backend (command_handler.py, pumpkin_face.py). The timeline schema is the canonical command reference for end users and developers. Without documentation, the feature remained undiscoverable to anyone writing timeline JSON or using the LLM skill (Issue #39) to generate animations.

## Style Compliance

The new Mouth section follows the **exact formatting pattern** of existing sections (Eyebrows, Nose):
- Standard markdown table with Command | Args | Description columns
- Horizontal rule separator (`---`) before and after
- No-arg commands marked with `—` in Args column
- Parameterized commands show arg name, type, and allowed values using pipe notation
- Contextual note below the table with use-case guidance

## Verification

- ✅ File edited successfully: `docs/timeline-schema.md`
- ✅ Section placed logically (after Nose, before Chaining)
- ✅ All 6 commands documented with accurate descriptions from command_handler.py
- ✅ Markdown formatting matches Eyebrows and Nose sections exactly
- ✅ Usage note provided for clarity

## Impact

Closes documentation gap for Issue #59 feature. Users can now reference the timeline schema to:
- Understand the 5 viseme shapes and their phoneme associations
- Choose between shorthand (5 commands) or compact (1 parameterized command) syntax
- Understand when to use mouth viseme state (speech synchronization)

---

**Related Issues:** #59 (Mouth Speech Control), #39 (LLM Recording Skill — will use this documentation)
