# Design Review — Issue #22: Eye Direction Control
**Facilitator:** Jinx  
**Date:** 2026-02-22  
**Participants:** Ekko (Graphics Dev), Vi (Backend Dev)

## Issue Summary

Users can control eye direction via X/Y degrees (0° = straight ahead). X degrees = left/right deviation, Y degrees = up/down deviation. Pupils move together OR independently (supporting weird/uncanny eye movements).

## Key Decisions

1. **Data Model:** Per-eye state variables `left_eye_x`, `left_eye_y`, `right_eye_x`, `right_eye_y` (4 floats, range ±90°)
2. **Coordinate System:** 0° = straight ahead, +X = right, −X = left, +Y = up, −Y = down (±90° range)
3. **Command Interface:** Single `gaze` command with arity-based parsing:
   - `gaze <x> <y>` → both eyes (shorthand)
   - `gaze <left_x> <left_y> <right_x> <right_y>` → independent eyes
4. **Animation Interaction:** Gaze persists across expression changes, pauses during rolling animation, survives blinks
5. **Validation:** Server-side validation (reject out-of-range angles), graphics-side clamping as safety net

## Data Model

**State variables added to `PumpkinFace.__init__`:**
```python
self.left_eye_x = 0.0   # ±90°, left/right
self.left_eye_y = 0.0   # ±90°, up/down
self.right_eye_x = 0.0
self.right_eye_y = 0.0
```

**Coordinate convention:**
- X axis: −90° = max left, 0° = center, +90° = max right
- Y axis: −90° = max down, 0° = center, +90° = max up
- 0° on both axes = straight ahead (neutral gaze)

**Separation from rolling animation:** Current `pupil_angle` (circular 0-360°) remains for rolling. Gaze uses orthogonal X/Y linear angles.

## Rendering Interface

**How Ekko accesses eye positions:**

Graphics layer converts angles to pupil pixel positions via:
```python
def _compute_pupil_position(eye_center, eye_x_deg, eye_y_deg, eye_scale=1.0):
    # Clamp to ±90°
    x_clamped = max(-90, min(90, eye_x_deg))
    y_clamped = max(-90, min(90, eye_y_deg))
    
    # Map to pupil orbit radius (~14px)
    orbit_radius = math.sqrt(200) * eye_scale  # Maintains rolling behavior
    pupil_offset_x = orbit_radius * math.sin(math.radians(x_clamped))
    pupil_offset_y = orbit_radius * math.sin(math.radians(y_clamped))
    
    return (
        int(eye_center[0] + pupil_offset_x),
        int(eye_center[1] + pupil_offset_y)
    )
```

**Edge cases handled:**
- Pupils at ±90° reach max orbit but stay within white eye circle (orbit_radius 14.14 + pupil_radius 15 = 29.14 < eye_radius 40 → 10.86px safety margin)
- Blink + gaze: Eye scale shrinks orbit → pupils converge correctly
- Hard clamp at ±90° prevents escape

**Projection mapping compliance:** Pupils remain pure black (0,0,0) on white (255,255,255) background. Rendering order: white eye circle first, then black pupil offset by angles.

## Command Parsing

**Socket command format:**
```
gaze <x> <y>                               # Both eyes together
gaze <left_x> <left_y> <right_x> <right_y>  # Independent eyes
```

**Parsing logic (Vi):**
```python
if data.startswith("gaze"):
    parts = data.split()
    try:
        if len(parts) == 3:      # gaze x y
            x, y = float(parts[1]), float(parts[2])
            if abs(x) > 90 or abs(y) > 90:
                raise ValueError("Angles must be in range [-90, 90]")
            self.set_gaze(x, y, x, y)  # Both eyes
        elif len(parts) == 5:    # gaze left_x left_y right_x right_y
            left_x, left_y = float(parts[1]), float(parts[2])
            right_x, right_y = float(parts[3]), float(parts[4])
            for angle in [left_x, left_y, right_x, right_y]:
                if abs(angle) > 90:
                    raise ValueError(f"Angle {angle} out of range [-90, 90]")
            self.set_gaze(left_x, left_y, right_x, right_y)
        else:
            raise ValueError(f"Expected 2 or 4 angle values, got {len(parts)-1}")
    except (ValueError, IndexError) as e:
        print(f"Invalid gaze command: {e}")
```

**State management method:**
```python
def set_gaze(self, left_x, left_y, right_x, right_y):
    if self.is_rolling:
        print("Cannot change gaze during rolling animation.")
        return
    self.left_eye_x = left_x
    self.left_eye_y = left_y
    self.right_eye_x = right_x
    self.right_eye_y = right_y
```

**Keyboard shortcuts (testing):**
- Arrow keys: Adjust gaze in 5° increments (both eyes together)
- `0` key: Reset gaze to center (0°, 0°)

## Interaction with Existing Features

| Feature | Interaction | Behavior |
|---------|-------------|----------|
| **Expression changes** | Orthogonal | Gaze persists across expressions (e.g., happy with eyes looking left) |
| **Rolling animation** | Conflict | `gaze` command rejected during active roll; gaze resumes after roll completes |
| **Blink/Wink** | Compatible | Gaze state held; eyes return to set angles after animation |
| **Wink** | Per-eye compatible | Winking eye uses its gaze angles; other eye maintains position |

**Rationale:** Gaze is intentional user input—should persist like expression state. Rolling is a temporary animation that temporarily overrides gaze.

## Risks & Concerns

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **Coordinate convention mismatch** (Ekko/Vi disagree on +X/+Y direction) | High | ✅ Aligned in review: +X = right, +Y = up |
| **Pupils escape white eye boundary** | High | ✅ Math validated: 10.86px safety margin at ±90° |
| **Rolling animation interference** | Medium | ✅ Reject gaze during roll (server-side guard) |
| **Float parsing bugs** (whitespace, negative angles) | Medium | ✅ Use `float()` + try/except; validate ±90° range |
| **Hard clamp feels artificial at ±90°** | Low | Accept for MVP; future enhancement: ease-out near boundaries |
| **No persistence across sessions** | Low | Design choice: gaze is transient (reset on app restart) |

## Action Items

| Owner | Action |
|-------|--------|
| **Ekko** | Implement `_compute_pupil_position()` method with X/Y angle support; update `_draw_eyes()` to call this method; add unit tests for angle-to-pixel math (0°, ±45°, ±90° cases) |
| **Vi** | Add `gaze` command parser to socket server; implement `set_gaze()` method with validation; add keyboard shortcuts for testing (arrow keys, 0 key); update README with command documentation |
| **Mylo** | Write test suite covering: both-eyes gaze, independent-eye gaze, boundary angles (±90°), interaction with rolling (rejection), gaze persistence across expressions |
| **Jinx** | Review PRs for coordinate system consistency and projection mapping compliance; validate rolling animation interaction |

---

**Next Steps:** Ekko and Vi work in parallel. Target completion: 1 sprint (4-6 hours). No blockers identified.
