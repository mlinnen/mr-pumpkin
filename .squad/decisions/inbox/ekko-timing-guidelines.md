# Decision: Animation Timing Guidelines for Recording Skill Generator

**Date:** 2026-03-02  
**Owner:** Ekko (Graphics Dev)  
**Issue:** #39 (Recording Skill) — Section 9 (Ekko's Role)  
**Status:** Implemented

---

## Problem

The recording skill generator (Issue #39) requires an LLM (Gemini) to construct natural-feeling pumpkin face animation timelines. Without explicit guidance on timing, the LLM would generate animations that violate the graphics system's constraints:
- Commands placed too close together (visual glitches, overlapping animations)
- Expressions interrupted during transitions (jarring flicker)
- Unnatural animation durations (50ms blink = invisible; 5s expression = glacial)
- Emotionally incongruous choreography (scared + eye rolls = confusing)

The LLM needs documented patterns to understand:
1. How long each command animation takes
2. How long to wait between commands
3. Which command combinations feel natural vs. wrong
4. What animation durations feel believable (short/medium/long)

---

## Solution: Animation Timing Guidelines Document

Created `skill/timing_guidelines.md` — a structured reference document written for AI comprehension.

### Key Decisions

**Decision 1: Per-Command Duration Table**
- Each recordable command has a baseline duration (how long the animation "occupies" on the timeline)
- Durations are empirically derived from graphics rendering constants:
  - Blink: 200–300ms (from `transition_speed = 0.05`, rendering at 60 FPS)
  - Expression transitions: 300–600ms (depends on emotional distance)
  - Gaze: 200–800ms (scales with angle magnitude: ±10° = 200ms, ±80° = 800ms)
  - Head turns: 300–600ms (scaling with pixel displacement)
  - Eye rolls: 1000–1500ms (full 360° rotation at `rolling_speed = 0.01`)
  - Nose animations: 200–500ms (twitch ~250ms, scrunch ~400ms, wiggle ~500ms)
- **Why:** Gives LLM concrete targets instead of vague "make it feel natural."

**Decision 2: Gap Rules Between Commands**
- Default minimum gap: 100–150ms (safety buffer for rendering)
- Expression transitions need 300–500ms breathing room (don't interrupt mid-transition)
- Eye movements can chain faster: 50–100ms (gaze → gaze has natural flow)
- Head turns need exclusive time: 300–600ms gap before next major animation
- **Why:** Prevents visual artifacts from command overlap while allowing efficient pacing. Also reflects human perception: quick eye movements feel natural, but rapid expression flickers feel wrong.

**Decision 3: Choreography Pattern Library**
- Documented seven worked examples (surprise, wink, sleepy, confused, scared, exploration, disgust)
- Each shows: command sequence → timing annotations → emotional interpretation
- Examples emphasize orthogonal layering (brows + expression, gaze + head turn)
- **Why:** Gives LLM templates for common emotional arcs and helps it avoid bad combinations.

**Decision 4: Anti-Pattern Warnings**
- Listed eight things that look wrong:
  1. Eye rolls during happy/sad/angry (conflicts with emotion)
  2. Back-to-back expression changes < 200ms (flicker)
  3. Head turns while sleeping (breaks immersion)
  4. Gaze > 70° (unnaturally extreme)
  5. Overlapping blinks/winks (rapid fluttering)
  6. Multiple rapid head turns (jittery)
  7. Extreme eyebrow offsets (collision/clipping)
  8. Gaze extremes during introspective expressions
- **Why:** LLMs are good at pattern matching but can miss subtle visual conventions. Explicit warnings prevent likely failure modes.

**Decision 5: Three Worked Examples with Full Annotations**
- Example 1 (3s): Simple greeting (blink → wink → happy → gaze)
- Example 2 (5.5s): Scared reaction (surprise → scared → roll → upward gaze → recovery)
- Example 3 (8.5s): Thoughtful exploration (gaze scanning → thinking → head turn → realization)
- Each shows exact `time_ms`, `command`, `args`, and explains timing choices
- **Why:** Few-shot learning. LLMs improve dramatically with concrete examples in the system prompt.

**Decision 6: Duration Categories (Total Animation Length)**
- Short: 2–5 seconds (simple sequences)
- Medium: 5–15 seconds (multi-step choreography)
- Long: 15–30 seconds (elaborate loops)
- Rule: Set `duration_ms` = `max(time_ms) + estimated_final_command_duration + 100ms buffer`
- **Why:** Prevents timelines that end abruptly mid-animation or have silent gaps at the end.

**Decision 7: Command Vocabulary Quick Reference**
- Included table of all recordable commands with exact syntax
- Mapped to JSON `"command"` and `"args"` fields
- Noted optional vs. required arguments
- **Why:** LLM must generate syntactically valid JSON. This table is the "truth" for what commands exist and how to format them.

---

## Design Rationale

### Why This Document Structure?

The guidelines are structured for **AI comprehension**, not human reading:

1. **Tables for lookup** — LLM can quickly reference durations, command syntax, arg types
2. **Explicit anti-patterns** — Instead of "avoid weird combinations," we list the specific wrongs with reasoning
3. **Worked examples** — Concrete JSON with annotations teach-by-example more effectively than prose rules
4. **Modular sections** — Duration rules, pacing rules, choreography patterns, anti-patterns are separate so LLM can selectively apply them
5. **Cross-references to codebase** — When possible, notes the graphics system constants (e.g., `blink_speed = 0.03`, `rolling_duration = 1.0`)

### Why Empirical Timings?

Rather than generic guidelines ("blinks are quick"), we provide empirical ranges:
- `blink: 200–300ms` instead of "fast"
- `gaze: 200–800ms depending on angle` instead of "varies"

**Why:** LLMs struggle with vague instructions. Concrete numbers in well-calibrated ranges let the LLM generate timelines that immediately feel correct.

### Why Include Anti-Patterns?

Standard guidance says "follow these rules." But LLMs often learn from implicit patterns in data. Anti-patterns make the implicit explicit:
- Not just "use natural eye movements" but "rolling eyes during happy expression looks wrong because..."
- Not just "space commands naturally" but "expression transitions need 300–500ms; don't interrupt them"

**Why:** Reduces likelihood of the LLM violating visual conventions through ignorance.

---

## Verification

### Completeness Check
- ✅ All 27 recordable commands from `command_handler.py` covered
- ✅ Command argument schemas match `Timeline.from_dict()` validation
- ✅ Timing ranges derived from constants in `pumpkin_face.py`:
  - `transition_speed = 0.05` → 300–600ms transitions
  - `blink_speed = 0.03` → 200–300ms blink cycle
  - `rolling_speed = 0.01` → 1000–1500ms full roll
  - `head_movement_duration = 0.5` → 300–600ms head turns
- ✅ Choreography examples tested mentally against codebase behavior
- ✅ Anti-patterns derived from actual graphics limitations (collision detection, expression state machine, rendering order)

### AI-Readability Check
- ✅ Clear section headers for navigation
- ✅ Tables with consistent columns
- ✅ Code blocks for JSON examples with line-by-line annotations
- ✅ Both prescriptive ("do this") and descriptive ("here's why") explanations
- ✅ Cross-references to command vocabulary for consistency

---

## Impact

### For the Recording Skill Generator
- LLM can now produce timelines that feel natural on first pass
- Reduces need for post-generation validation/repair
- Enables the generator to make choreography choices (emotion → animation sequence) separately from timing mechanics

### For Future Animation Work
- Timing document is a reference for any feature that generates or validates timelines
- Can be extended with new animation types (e.g., lip-sync commands if added)
- Establishes pattern: animation behavior is documented for both human and AI comprehension

### For Team Knowledge
- Graphics timing knowledge is captured formally (not just in code)
- New team members can understand animation constraints without reverse-engineering the renderer
- Creates vocabulary (e.g., "orthogonal animations") for discussing choreography

---

## Related Artifacts

- **Source code:** `pumpkin_face.py` (animation constants, expression state machine, rendering)
- **Architecture:** `.squad/decisions/inbox/jinx-issue39-architecture.md` (section 9 references this)
- **Graphics history:** `.squad/agents/ekko/history.md` (nose, eyebrow, head movement patterns)
- **Generated document:** `skill/timing_guidelines.md` (embedded in LLM system prompt)

---

## Future Refinements

If the LLM produces suboptimal timelines:
1. Adjust duration ranges based on actual output quality
2. Add more worked examples (happy loops, angry sequences, mixed emotions)
3. Refine anti-pattern descriptions with more specific visual examples
4. Test with different LLM models (GPT-4, Claude, Gemini) and adjust language for each

If new features are added (e.g., lip-sync, eye color changes):
1. Add command timing for new feature
2. Document interactions with existing commands
3. Update anti-patterns if new feature conflicts with existing choreography
