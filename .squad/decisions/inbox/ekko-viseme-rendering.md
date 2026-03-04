# Decision: Viseme Mouth Rendering Implementation

**Date:** 2026-03-03  
**Decider:** Ekko (Graphics Dev)  
**Context:** Issue #59 — Lip-sync / viseme mouth rendering for speech animation  
**Status:** ✅ Implemented

---

## Summary

Implemented visual rendering for four speech visemes (closed, open, wide, rounded) that override expression-driven mouth shapes when active. The speech override system cleanly short-circuits the rendering path without modifying the expression state machine.

---

## Technical Implementation

### Files Modified
- `pumpkin_face.py`

### Changes Made

**1. Added `_get_viseme_points()` helper method (line 231)**
- Generates mouth geometry for speech visemes
- Returns 2-point lines for "closed" and "wide" visemes
- Returns empty list for "open" and "rounded" (filled shapes)
- Accepts pre-calculated mouth_y position for consistency

**2. Modified `_get_mouth_points()` (line 198-200)**
- Added speech override check at TOP of method
- When `self.mouth_viseme` is active → delegate to `_get_viseme_points()`
- When None → fall through to existing expression logic
- Zero changes to expression mouth rendering code

**3. Modified `_draw_mouth()` filled shapes section (line 508-515)**
- Speech viseme filled shapes ("open", "rounded") take priority
- Check viseme type before expression type
- Early return after rendering viseme shape
- Expression shapes (surprised/scared) still work when viseme inactive

**4. Modified `_draw_mouth()` line thickness (line 527)**
- Dynamic thickness: 6 for "wide" viseme, 8 for all others
- Wider mouths use thinner lines for visual balance
- All expression mouths maintain thickness 8

---

## Viseme Specifications

| Viseme | Shape | Dimensions | Rendering |
|--------|-------|-----------|-----------|
| `"closed"` | Line | 100px wide | `(cx-50, mouth_y)` to `(cx+50, mouth_y)`, thickness 8 |
| `"wide"` | Line | 180px wide | `(cx-90, mouth_y)` to `(cx+90, mouth_y)`, thickness 6 |
| `"open"` | Ellipse | 80×60px | Filled at `(cx-40, mouth_y-30, 80, 60)` |
| `"rounded"` | Circle | radius 25px | Filled at `(cx, mouth_y)` |

- All shapes positioned at `mouth_y = center_y + 80`
- All use white color (255,255,255) for projection mapping contrast
- Dimensions chosen for clear visibility at projection distances

---

## Architecture Pattern: Speech Override

**Key Principle:** The viseme system overrides **rendering** without modifying **state**.

```python
# In _get_mouth_points():
if self.mouth_viseme is not None:
    return self._get_viseme_points(cx, mouth_y, self.mouth_viseme)  # Short-circuit

# Expression logic continues unchanged below...
```

**Benefits:**
1. **Clean separation:** Speech and expression paths don't interfere
2. **Easy return:** Setting `mouth_viseme = None` instantly returns to expression control
3. **No state corruption:** `current_expression` remains unchanged during speech
4. **Composability:** Can switch between speech and expression seamlessly

**Pattern Application:** This establishes a reusable pattern for temporary visual overrides that don't disturb underlying animation state machines.

---

## State Management Integration

**State Variables (added by Vi):**
- `self.mouth_viseme`: Current viseme name or None
- `self.mouth_transition_progress`: Transition animation progress
- `self.mouth_transition_speed`: Transition speed

**Public Methods (added by Vi):**
- `set_mouth_viseme(viseme)`: Activate speech override
- `reset_mouth()`: Return to expression-driven control

**Rendering Methods (added by Ekko):**
- `_get_viseme_points(cx, cy, viseme)`: Generate viseme geometry
- Updates to `_get_mouth_points()` and `_draw_mouth()`: Handle override

---

## Verification

✅ Syntax check passes  
✅ Four viseme shapes implemented per specification  
✅ All expression mouths preserved (happy, sad, angry, surprised, scared, neutral, sleeping)  
✅ No changes to eyes, eyebrows, nose, or other facial features  
✅ Projection mapping consistency maintained (white on black, thick lines)  
✅ Override pattern cleanly separates speech from expression logic

---

## Next Steps (for Vi/Jinx)

- Socket command integration: `set_mouth_viseme <viseme>`
- Transition animation implementation (smooth blend between visemes)
- Phoneme-to-viseme mapping for text-to-speech integration
- Testing with actual speech audio or TTS system

---

**Confirmed by:** Ekko  
**Ready for:** Integration testing with speech commands
