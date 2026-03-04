# Decision: Mouth Speech State Infrastructure Added

**Date:** 2026-03-03  
**Decided by:** Vi (Backend Dev)  
**Related to:** Issue #59 — Independent mouth control for speech simulation

## Context

Implementing independent mouth control for speech animation requires orthogonal state management that works independently of the expression system. This allows visemes to override expression-driven mouth shapes during speech synthesis.

## Decision

Added mouth speech control state variables and public API methods to `PumpkinFace`:

### State Variables (lines 115-118)
```python
# Mouth/speech control state (orthogonal to expression state machine)
self.mouth_viseme = None            # Current viseme override: None or "closed"|"open"|"wide"|"rounded"
self.mouth_transition_progress = 1.0    # 0.0 → 1.0 transition to target viseme
self.mouth_transition_speed = 0.15      # Faster than expression transitions (0.05) for snappy speech
```

### Public API Methods (after line 539)
- `set_mouth_viseme(viseme)` — Sets mouth to a speech viseme, starts transition
- `reset_mouth()` — Clears speech override, returns to expression control

### Update Loop Integration (line 1107-1109)
Added mouth transition progress update between nose animation and expression transitions:
```python
if self.mouth_transition_progress < 1.0:
    self.mouth_transition_progress = min(1.0, self.mouth_transition_progress + self.mouth_transition_speed)
```

## Architecture Pattern

Follows the established **orthogonal state machine pattern** used for eyebrows and nose:
- Mouth speech control is INDEPENDENT of expression state
- Viseme overrides can layer on top of expression-driven mouth shapes
- Transition speed (0.15) is 3x faster than expression transitions (0.05) for snappy speech

## Impact

- **Ekko's next:** Integrate `mouth_viseme` and `mouth_transition_progress` into `_get_mouth_points()` and `_draw_mouth()` to blend viseme shapes with expression shapes
- **Command handler:** Vi will add commands (e.g., `mouth_viseme <viseme>`) in a separate task
- **Backward compatibility:** No breaking changes — when `mouth_viseme = None`, mouth is fully expression-driven (existing behavior)

## Files Modified

- `pumpkin_face.py` — Added state variables, methods, and update loop integration
- `.squad/agents/vi/history.md` — Documented implementation details

## Status

✅ **Complete** — State infrastructure ready for Ekko's rendering integration
