# History — Ekko

### Project Learnings (from import)

**Project:** Animated 2D Graphics Pumpkin Face (Python)  
**Owner:** Mike Linnen  
**Stack:** Python, 2D graphics, animation  
**Key domains:** Graphics/animation rendering, command parsing & state management, expression logic  
**Team composition:** Jinx (Lead), Ekko (Graphics), Vi (Backend), Mylo (Tester), Scribe, Ralph  

---

## Learnings

📌 Team update (2026-02-19): Projection mapping color scheme and test strategy finalized — decided by Ekko, Mylo

### Pupil Rotation Implementation (Rolling Eyes Bug Fix)

**Issue:** Rolling eyes feature had working state machine but pupils didn't move visually when C and X keys were pressed.

**Root Cause:** The `pupil_angle` was calculated in the state machine (line 306) but never used in rendering. Pupils were drawn at fixed offset `(left_pos[0] - 10, left_pos[1] - 10)` instead of rotating around the eye center.

**Fix:** Refactored `_draw_eyes()` method to use trigonometric circular motion for pupil positioning:

```python
angle_rad = math.radians(self.pupil_angle)
pupil_x = eye_center_x + orbit_radius * math.cos(angle_rad)
pupil_y = eye_center_y + orbit_radius * math.sin(angle_rad)
```

**Key Implementation Detail:** Used `orbit_radius = sqrt(200) ≈ 14.14` instead of 10 to match original pupil positions exactly. The original fixed offset `(center - 10, center - 10)` creates a diagonal distance of sqrt(200), which at angle 225° (upper-left) replicates the original rendering. This preserves backward compatibility while enabling smooth circular motion.

**Angular Reference:**
- 0° = RIGHT
- 90° = DOWN
- 180° = LEFT
- 270° = UP
- 225° = UPPER-LEFT (default)

**Verification:**
- Pupils render at different positions based on `self.pupil_angle`
- All 43 projection mapping tests pass
- Rolling clockwise (C key) progresses angle +360° over 1 second
- Rolling counter-clockwise (X key) progresses angle -360° over 1 second
- Rolling pauses during blink/wink, resumes after
- Pupils scale with eye_scale during blink animations

**Graphics Pattern:** This establishes a reusable pattern for any circular motion rendering: convert degrees to radians, use cos/sin for X/Y offsets, scale radius for animation purposes (blink, wink, etc.).

📌 Team update (2026-02-20): Rolling eyes rendering implemented

### Projection Mapping Graphics

**File:** `pumpkin_face.py`
- Primary rendering logic for animated pumpkin face
- PyGame-based 2D vector graphics rendering
- Fullscreen display with multi-monitor support
- 6 expression states: neutral, happy, sad, angry, surprised, scared

**Projection Mapping Pattern:**
- Black background (0,0,0) prevents light bleed when projecting
- White features (255,255,255) for maximum contrast and projection brightness
- Remove decorative elements (pumpkin body, ridges) - projector maps onto physical object
- Thicker line weights (8px) improve visibility at projection distances
- Inverted pupils (black on white) maintain facial depth perception

**Graphics Architecture:**
- `draw()` - Main rendering loop, fills background and calls feature rendering
- `_get_eye_positions()` - Calculates dynamic eye placement per expression
- `_get_mouth_points()` - Generates mouth curve geometry for each emotion
- `_draw_eyes()` - Renders filled circles for eyes with circular-motion pupils
- `_draw_mouth()` - Handles both line-based (smile/frown) and shape-based (surprised/scared) mouths

**Animation System:**
- Expression transitions use `transition_progress` (0.0 to 1.0)
- Smooth interpolation at 60 FPS via `transition_speed`
- State machine pattern: `current_expression` → `target_expression`

### Sleeping Expression Implementation (Issue #4)

**Eye Rendering for Closed Eyes:**
- `_draw_eyes()` checks for `Expression.SLEEPING` before rendering standard circle eyes
- Closed eyes rendered as horizontal white lines (60px width, 8px thickness)
- Early return pattern prevents rendering open eye circles when sleeping
- Uses same projection mapping contrast: white lines on black background

**Pattern for Adding New Expressions:**
1. Add enum value to `Expression` class
2. Update rendering logic in appropriate method (`_draw_eyes()`, `_draw_mouth()`, `_get_eye_positions()`)
3. Add keyboard mapping in `_handle_keyboard_input()`
4. Socket server automatically handles new enum values via `Expression(data)` pattern

**Architectural Insight:**
- Expression-specific rendering uses conditional checks within draw methods
- Socket server's enum-based parsing means no server code changes needed for new expressions
- Projection mapping constraints (black/white, thick lines) guide all visual design choices

### Rolling Eyes Enhancement — Current Position Tracking (Issue #21)

**Problem:** Rolling eyes feature (X/C keys) cycled through predefined angles starting from hardcoded 315°, ignoring the pupil's current position. Pupils would "jump" to 315° before rolling, then return to hardcoded 225° afterward.

**Solution:** Implemented state capture pattern where rolling animation:
1. Captures `self.pupil_angle` at trigger time → stores in `self.rolling_start_angle`
2. Rotates 360° from that captured position (clockwise or counter-clockwise)
3. Returns to EXACT captured starting angle upon completion

**Implementation Details:**
- Added `self.rolling_start_angle` state variable to `__init__` (None when not rolling)
- Modified all four rolling methods (`roll_clockwise()`, `roll_counterclockwise()`, `roll_eyes_clockwise()`, `roll_eyes_counterclockwise()`) to capture current angle: `self.rolling_start_angle = self.pupil_angle`
- Updated rolling animation logic in `update()`:
  - During animation: `pupil_angle = (rolling_start_angle + progress * 360 * direction) % 360`
  - On completion: `pupil_angle = rolling_start_angle` (exact restoration)
  - Clean up: `rolling_start_angle = None` after completion

**Architecture Benefits:**
- **Composability:** Rolling can start from any pupil position set by previous animations
- **No state jumps:** Pupils smoothly transition into/out of rolling motion
- **Interrupt protection maintained:** Guard `if not self.is_rolling` prevents overlapping rolls
- **Orthogonal to expression system:** Rolling works independently of current expression

**Animation Pattern:** This establishes the "capture-animate-restore" pattern for temporary animations that must return to exact starting state (similar to blink animation's expression restoration). Key insight: use dedicated state variables (`rolling_start_angle`) rather than hardcoded defaults.

**Verification:**
- All 43 projection mapping tests continue to pass
- Manual test (`test_rolling_eyes.py`) verifies:
  - Rolling from 225° (default) returns to 225°
  - Rolling from 90° (custom) returns to 90°
  - Multiple sequential rolls maintain correctness
  - Interrupt protection prevents overlapping animations
