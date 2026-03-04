# Decisions

Last updated: 2026-03-04T02:59:22Z

---

## Issue #59 — Independent Mouth Speech Control

### Decision: Mouth Speech State Infrastructure Added

**Date:** 2026-03-03  
**Decided by:** Vi (Backend Dev)  
**Related to:** Issue #59 — Independent mouth control for speech simulation  
**Status:** ✅ Complete

#### Context

Implementing independent mouth control for speech animation requires orthogonal state management that works independently of the expression system. This allows visemes to override expression-driven mouth shapes during speech synthesis.

#### Decision

Added mouth speech control state variables and public API methods to `PumpkinFace`:

**State Variables (pumpkin_face.py, lines 115-118):**
```python
self.mouth_viseme = None            # Current viseme override: None or "closed"|"open"|"wide"|"rounded"
self.mouth_transition_progress = 1.0    # 0.0 → 1.0 transition to target viseme
self.mouth_transition_speed = 0.15      # Faster than expression transitions (0.05) for snappy speech
```

**Public API Methods (after line 539):**
- `set_mouth_viseme(viseme)` — Sets mouth to a speech viseme, starts transition
- `reset_mouth()` — Clears speech override, returns to expression control

**Update Loop Integration (line 1107-1109):**
Added mouth transition progress update between nose animation and expression transitions.

#### Architecture Pattern

Follows the established **orthogonal state machine pattern** used for eyebrows and nose:
- Mouth speech control is INDEPENDENT of expression state
- Viseme overrides can layer on top of expression-driven mouth shapes
- Transition speed (0.15) is 3x faster than expression transitions (0.05) for snappy speech

#### Impact

- Ekko's rendering: Integrate `mouth_viseme` and `mouth_transition_progress` into `_get_mouth_points()` and `_draw_mouth()`
- Command handler: Add commands (e.g., `mouth_viseme <viseme>`)
- Backward compatibility: No breaking changes — when `mouth_viseme = None`, mouth is fully expression-driven

---

### Decision: Mouth Speech Commands Added to CommandRouter

**Date:** 2026-03-03  
**Agent:** Vi (Backend Dev)  
**Issue:** #59  
**Files Modified:** command_handler.py  
**Status:** ✅ Complete

#### Summary

Added 6 mouth/speech control commands to CommandRouter.execute(). Commands enable interactive control of mouth visemes for speech simulation during animation recording and playback.

#### Commands Added

**Individual Viseme Shorthand Commands:**
- `mouth_closed` — Set mouth to closed viseme (M, B, P sounds)
- `mouth_open` — Set mouth to open viseme (AH, AA sounds)
- `mouth_wide` — Set mouth to wide viseme (EE, IH sounds)
- `mouth_rounded` — Set mouth to rounded viseme (OO, OH sounds)
- `mouth_neutral` — Release mouth to expression-driven control

**Parameterized Command:**
- `mouth <viseme>` — Set mouth to named viseme (closed/open/wide/rounded/neutral)

#### Implementation Details

**Location:** Added before `# ===== TIMELINE COMMANDS =====` section (after reset_nose)

**Pattern:** Followed established `wiggle_nose` command pattern:
1. Check if recording is active → capture command for timeline
2. Call `self.pumpkin.set_mouth_viseme(viseme)`
3. Print confirmation message
4. Return `""` (empty string)

**Validation:** Parameterized `mouth` command validates viseme name and provides helpful error message for invalid inputs.

**Help Text:** Updated with 6 new entries before `reset` command.

#### Integration Status

- ✅ State variables added
- ✅ set_mouth_viseme() method added
- ✅ Commands added
- ✅ Graphics integration (Ekko)

---

### Decision: Viseme Mouth Rendering Implementation

**Date:** 2026-03-03  
**Decider:** Ekko (Graphics Dev)  
**Context:** Issue #59 — Lip-sync / viseme mouth rendering for speech animation  
**Status:** ✅ Complete

#### Summary

Implemented visual rendering for four speech visemes (closed, open, wide, rounded) that override expression-driven mouth shapes when active. The speech override system cleanly short-circuits the rendering path without modifying the expression state machine.

#### Technical Implementation

**Files Modified:** `pumpkin_face.py`

**Changes Made:**

1. **Added `_get_viseme_points()` helper method (line 231)**
   - Generates mouth geometry for speech visemes
   - Returns 2-point lines for "closed" and "wide" visemes
   - Returns empty list for "open" and "rounded" (filled shapes)
   - Accepts pre-calculated mouth_y position for consistency

2. **Modified `_get_mouth_points()` (line 198-200)**
   - Added speech override check at TOP of method
   - When `self.mouth_viseme` is active → delegate to `_get_viseme_points()`
   - When None → fall through to existing expression logic
   - Zero changes to expression mouth rendering code

3. **Modified `_draw_mouth()` filled shapes section (line 508-515)**
   - Speech viseme filled shapes ("open", "rounded") take priority
   - Check viseme type before expression type
   - Early return after rendering viseme shape
   - Expression shapes (surprised/scared) still work when viseme inactive

4. **Modified `_draw_mouth()` line thickness (line 527)**
   - Dynamic thickness: 6 for "wide" viseme, 8 for all others
   - Wider mouths use thinner lines for visual balance
   - All expression mouths maintain thickness 8

#### Viseme Specifications

| Viseme | Shape | Dimensions | Rendering |
|--------|-------|-----------|-----------|
| `"closed"` | Line | 100px wide | `(cx-50, mouth_y)` to `(cx+50, mouth_y)`, thickness 8 |
| `"wide"` | Line | 180px wide | `(cx-90, mouth_y)` to `(cx+90, mouth_y)`, thickness 6 |
| `"open"` | Ellipse | 80×60px | Filled at `(cx-40, mouth_y-30, 80, 60)` |
| `"rounded"` | Circle | radius 25px | Filled at `(cx, mouth_y)` |

All shapes positioned at `mouth_y = center_y + 80`, white color (255,255,255) for projection mapping contrast.

#### Architecture Pattern: Speech Override

**Key Principle:** The viseme system overrides **rendering** without modifying **state**.

The speech override pattern cleanly short-circuits the rendering path:
- Speech and expression paths don't interfere
- Setting `mouth_viseme = None` instantly returns to expression control
- No state corruption — `current_expression` remains unchanged during speech
- Composable: Can switch between speech and expression seamlessly

**Pattern Application:** Reusable pattern for temporary visual overrides that don't disturb underlying animation state machines.

#### Verification

- ✅ Syntax check passes
- ✅ Four viseme shapes implemented per specification
- ✅ All expression mouths preserved (happy, sad, angry, surprised, scared, neutral, sleeping)
- ✅ No changes to eyes, eyebrows, nose, or other facial features
- ✅ Projection mapping consistency maintained (white on black, thick lines)
- ✅ Override pattern cleanly separates speech from expression logic

---

### Decision: Mouth Speech Test Suite Complete

**Date:** 2026-03-03  
**Author:** Mylo (Tester)  
**Issue:** #59  
**Status:** ✅ Complete

#### Summary

Created comprehensive test suite for mouth speech control feature: `tests/test_mouth_speech.py`

**Test Coverage:**
- 30 tests across 5 test classes
- All tests passing

#### Test Classes

1. **TestMouthStateManagement** (10 tests)
   - State initialization (mouth_viseme, transition_progress)
   - Viseme setting (closed, open, wide, rounded)
   - Neutral/None clearing behavior
   - Transition progress reset
   - reset_mouth() functionality

2. **TestMouthStateOrthogonality** (2 tests)
   - Expression changes do NOT clear viseme
   - Viseme persistence across expression transitions

3. **TestMouthCommandRouting** (8 tests)
   - All 5 named commands (mouth_closed, mouth_open, mouth_wide, mouth_rounded, mouth_neutral)
   - Parameterized command: "mouth <viseme>"
   - Invalid viseme handling (no crash)
   - Return value verification (empty string)

4. **TestMouthVisemePoints** (5 tests)
   - Closed viseme geometry: 2-point line [(cx-50, cy), (cx+50, cy)]
   - Wide viseme geometry: 2-point line [(cx-90, cy), (cx+90, cy)]
   - Open/rounded: empty list (filled shapes)
   - Viseme override in _get_mouth_points()

5. **TestMouthEdgeCases** (5 tests)
   - Multiple sequential viseme changes
   - Viseme during expression transition
   - Idempotent reset_mouth()
   - "neutral" string === None equivalence
   - Transition progress reset on each viseme change

#### Key Patterns

- **Fixture pattern:** pygame.init() → yield pumpkin → pygame.quit()
- **CommandRouter fixture:** Router created with (pumpkin, Expression) for command tests
- **State-only testing:** No rendering validation (pygame.draw calls), only state verification
- **Orthogonality validation:** Explicit tests that viseme state is independent of expression state

#### Implementation Verified

- ✅ `pumpkin_face.py`: mouth_viseme, mouth_transition_progress, mouth_transition_speed state vars
- ✅ `pumpkin_face.py`: set_mouth_viseme(), reset_mouth(), _get_viseme_points() methods
- ✅ `command_handler.py`: 5 named commands + parameterized "mouth <viseme>" command
- ✅ All 30 tests passing

---

## Previous Decisions

[Previous decision history omitted for brevity; archived decisions available in session logs]
