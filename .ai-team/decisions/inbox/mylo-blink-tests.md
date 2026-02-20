# Blink Animation Test Design Decisions

**By:** Mylo (Tester)  
**Date:** 2026-02-20  
**Issue:** #5 — Add a blink animation

## Test Architecture Decision

**What:** Comprehensive test suite (12 tests) covering state machine behavior, animation phases, and integration points for blink animation feature.

**Why:**
- Blink is fundamentally different from expression transitions — it's a temporary animation detour that must restore the original state
- Animation progress tracking (0.0 to 1.0) requires different testing approach than static expression states
- Non-interrupting behavior is critical: calling blink() during blink should not reset progress
- Expression restoration must be EXACT (not default to NEUTRAL) — this is user-facing correctness

## Key Design Choices

### 1. State Machine Validation Over Visual Testing
Unlike expression tests that sample pixels, blink tests validate:
- `is_blinking` flag lifecycle
- `blink_progress` advancement per update() call
- `pre_blink_expression` preservation

**Rationale:** Animation correctness is a state machine problem first, rendering problem second.

### 2. Iteration Count for Completion Tests
Tests use 40 update() calls to complete blink (blink_speed=0.03 → 34 updates theoretical, 40 for margin).

**Rationale:** Deterministic completion testing without timing dependencies. Extra margin accounts for floating point rounding.

### 3. Parametrized Test for All 7 Expressions
Single test multiplied across NEUTRAL, HAPPY, SAD, ANGRY, SURPRISED, SCARED, SLEEPING.

**Rationale:** Blink must work correctly from ANY starting expression, including SLEEPING (closed eyes → blink → closed eyes). Parametrization prevents copy-paste test sprawl.

### 4. Socket "blink" as Non-Enum Command
Test validates "blink" string triggers blink() method, NOT Expression enum parsing.

**Rationale:** Architectural distinction between:
- Expression changes (state transitions via enum)
- Animation commands (behavior triggers, not states)

This establishes pattern for future animation commands (wink, nod, etc.) without polluting Expression enum.

### 5. Speed Differential Validation
Explicit test: `blink_speed (0.03) < transition_speed (0.05)`

**Rationale:** Blink feeling natural depends on being SLOWER than expression changes. This is a UX requirement codified in tests. If speeds drift, tests catch regression.

## Test Coverage Gaps (Acknowledged)

**Not tested:**
- Exact visual rendering of eye closure phases (0.0-0.5-1.0)
- Blink during mid-expression transition (blink while transitioning HAPPY → SAD)
- Rapid blink commands (keyboard B mashing)

**Rationale for omissions:**
- Visual rendering already covered by projection mapping tests (horizontal lines for sleeping)
- Mid-transition blink interaction is edge case — implementation may choose to block or queue
- Rapid blink rate-limiting is UX polish, not core functionality

## Impact on Future Work

This test pattern establishes:
- Template for future animation commands (wink, nod, bounce)
- State machine testing over pixel-sampling for animations
- Socket command extension point (string commands beyond Expression enum)

## Risks

- Tests assume 40 iterations sufficient for all frame rates (60fps = 0.67 seconds)
- No validation of VISUAL smoothness, only state correctness
- Keyboard shortcut B may conflict with future features

## Review Notes

These tests are written BEFORE implementation lands (parallel to Ekko's work on squad/5-blink-animation branch). Minor adjustments may be needed if implementation details differ from specification.
