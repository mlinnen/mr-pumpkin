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
📌 Team update (2026-02-25): Feature branch workflow standard and repository cleanliness directive — decided by Mike Linnen
📌 Team update (2026-02-27): Issue triage Round 1: #20 (lip-sync P2, Vi+Ekko) assigned for architectural design — decided by Jinx

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

### Eyebrow Rendering System (Issue #16)

**File:** `pumpkin_face.py`

**Implementation:** Added `_draw_eyebrows` method with expression-based baseline positions, tilt angles, and animation integration.

**Baseline Table Design:**
- Each expression has a baseline tuple: `(brow_y_gap, angle_offset)`
- `brow_y_gap`: How far above eye center the brow sits (negative values, e.g., -55 pixels)
- `angle_offset`: Tilt angle where positive = outer corners up (surprised), negative = inner corners up (angry)
- Example: `Expression.ANGRY: (-50, -12)` creates V-shaped angry brows

**Tilt Geometry:**
- Eyebrows rendered as tilted lines 70px wide (±35px from center)
- Line drawn from `(cx - 35, brow_y + angle_offset)` to `(cx + 35, brow_y - angle_offset)`
- For ANGRY with angle_offset=-12: left side goes down, right side goes up = inner corners raised (V-shape)
- For SURPRISED with angle_offset=+5: outer corners raised (arched surprise)

**Animation Integration:**
- **Expression transitions:** Interpolates both gap and angle using `transition_progress`
- **Blink lift:** Both brows rise 8px during blink using `sin(blink_progress * π)`
- **Wink lift:** Individual brow rises based on which eye is winking using eye scale
- **User offsets:** Applied after baseline, negative = raise, positive = lower
- **Collision detection:** Eyebrows skipped if gap to eye top < 5px

**Rendering Order:**
1. Skip if `Expression.SLEEPING` (eyebrows hidden when sleeping)
2. Calculate interpolated baseline during expression transitions
3. Apply blink lift (both brows)
4. Apply per-eye wink lift
5. Add user-controlled offsets
6. Clamp to floor (y=350 minimum)
7. Check collision with eye boundary
8. Draw tilted white line (8px thickness) if safe

**Pattern Established:** Derived transient animation — animation effects (blink/wink lift) computed at render time from existing progress variables, without needing capture/restore. The eyebrow state variables (`eyebrow_left_offset`, `eyebrow_right_offset`) are orthogonal persistent state, while blink/wink lifts are ephemeral rendering effects.

📌 Team update (2026-02-22): Eyebrow rendering with expression baselines implemented

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

### Projection Offset UI (Issue #18)

**Implementation:** Added projection alignment jog controls to enable easy physical alignment of projected face onto foam pumpkin without manual adjustments.

**Architecture:**
- State variables: `projection_offset_x`, `projection_offset_y` (orthogonal to all other state)
- Rendering: Offset applied to center coordinates in `draw()` method before calculating feature positions
- Persistence: Offset survives across expression changes, blinks, winks, and all other animations
- Bounds: Clamped to ±500 pixels to prevent extreme misalignment

**UI Controls:**
- Arrow keys: Nudge projection 5px in any direction (up/down/left/right)
- `0` key: Reset offset to center (0, 0)
- Console feedback: Prints current offset after each adjustment

**Backend Integration:**
- Socket commands: `jog_offset dx dy`, `set_offset x y`, `projection_reset`
- Vi implemented command parsing in socket server
- Test script: `test_projection_offset.py` validates backend commands

**Graphics Pattern — Orthogonal State Layers:**
This establishes the pattern for persistent UI adjustments that operate independently from animation state machines. Projection offset is applied at the rendering root (center coordinates) so all features automatically inherit the adjustment. Key insight: transform at the highest level to affect all child elements uniformly.

📌 Team update (2026-02-22): Projection jog UI implemented with keyboard and socket controls

### Eyebrow Clipping Bug Fix (Issue: Eyebrows disappear at high Y offset)

**Problem:** When projection offset jogged to high Y values (e.g., -300 to -400), eyebrows would clip and disappear while eyes remained visible. This occurred because eyebrow rendering had a hardcoded absolute screen coordinate clamp at `y=350`.

**Root Cause:** In `_draw_eyebrows()` (line 372), eyebrow Y positions were clamped using `max(350, left_brow_y)`. This clamp was in absolute screen coordinates and did not account for projection offset. When projection offset moved eyes upward (negative Y), eyebrows followed but were artificially limited to y=350, causing them to render below/behind the eyes or not at all.

**Fix:** Changed floor clamp from hardcoded `350` to screen top edge (`0`). The clamp now prevents eyebrows from rendering above the screen top while allowing them to move freely with projection offset:

```python
# Old: hardcoded absolute coordinate
left_brow_y = max(350, left_brow_y)

# New: relative to screen bounds
screen_floor = 0  # Top edge of screen
left_brow_y = max(screen_floor, left_brow_y)
```

**Why This Works:**
- Eyebrow Y positions are calculated relative to eye positions (`left_pos[1] + baseline_gap + ...`)
- Eye positions already include projection offset (passed from `draw()` after offset applied)
- By removing the hardcoded clamp, eyebrows naturally move with eyes at any offset
- Existing collision detection (lines 385-398) prevents eyebrow/eye overlap regardless of offset

**Verification:**
- Created `test_eyebrow_clipping.py` to test extreme offsets (±400 pixels)
- All eyebrow rendering scenarios pass with offsets: centered, high jog, extreme high jog, low jog, extreme low jog
- All 43 existing projection mapping tests continue to pass
- Collision detection still prevents eyebrow/eye overlap

**Graphics Pattern — Coordinate System Consistency:** When applying transformations (like projection offset) at the rendering root, all child features must use relative positioning rather than absolute screen coordinates. Absolute clamps break when the coordinate system shifts. This establishes the pattern: compute positions relative to parent elements, clamp only against true boundaries (screen edges, not arbitrary hardcoded values).

### Mouth Clipping Bug Fix (Issue: Mouth drops off-screen in surprised/scared mode at high Y offsets)

**Problem:** When projection offset jogged to high Y values (e.g., -300 to -400) while in surprised or scared expressions, the mouth would drop excessively and clip off-screen. Eyes remained visible but the mouth would disappear or render far below expected position.

**Root Cause:** In `_draw_mouth()` method (lines 404-410), surprised and scared expressions used hardcoded absolute screen coordinates `(self.width // 2, self.height // 2 + 80)` instead of the offset-adjusted center coordinates passed to the method. The `draw()` method correctly computed offset-adjusted `center_x` and `center_y`, passed them to `_get_mouth_points()`, but `_draw_mouth()` ignored these adjusted coordinates for surprised/scared rendering.

**Fix:** Modified `_draw_mouth()` signature to accept center coordinates `cx` and `cy` as parameters (matching the pattern used by `_draw_eyes()` and `_draw_eyebrows()`). Updated surprised and scared mouth rendering to use these parameters:

```python
# Old: absolute coordinates ignoring offset
pygame.draw.circle(surface, self.FEATURE_COLOR, 
                  (self.width // 2, self.height // 2 + 80), 30)

# New: relative coordinates respecting offset
pygame.draw.circle(surface, self.FEATURE_COLOR, 
                  (cx, cy + 80), 30)
```

**Why This Works:**
- `draw()` applies projection offset to center coordinates (lines 113-114)
- These adjusted coordinates flow to all rendering methods as `cx, cy` parameters
- By accepting and using `cx, cy` in `_draw_mouth()`, surprised/scared mouths now inherit projection offset automatically
- Eliminates coordinate system mismatch between mouth rendering and other features

**Verification:**
- Created `test_mouth_clipping.py` testing 12 scenarios (surprised/scared × various offset combinations)
- All mouth visibility tests pass with extreme offsets: ±400 pixels Y, ±200 pixels X
- All 43 existing projection mapping tests continue to pass
- Mouth stays properly positioned relative to face at all reasonable offset ranges

**Graphics Pattern Reinforcement:** This is the same coordinate system bug class as the eyebrow clipping issue. The fix reinforces the established pattern: rendering methods must accept offset-adjusted coordinates as parameters rather than accessing raw screen dimensions. Absolute screen coordinates (`self.width // 2`) break when projection offset transforms the coordinate system. All feature rendering methods should use the signature pattern `_draw_feature(surface, ..., cx, cy)` to maintain coordinate system consistency.

### Animated Head Movement (Issue #17)

**Implementation:** Added smooth head movement animation system that creates 3D illusion by animating projection offset transitions.

**Architecture:**
- State variables: `is_moving_head`, `head_movement_progress`, `head_start_x/y`, `head_target_x/y`
- Animation duration: 0.5 seconds for smooth transitions
- Update loop integration: Runs at 60 FPS, independent of other animations
- Interpolation: Ease-in-out cubic (3t² - 2t³) for natural motion feel

**Movement Methods:**
- `turn_head_left(amount=50)`: Shift projection left (negative X)
- `turn_head_right(amount=50)`: Shift projection right (positive X)
- `turn_head_up(amount=50)`: Shift projection up (negative Y)
- `turn_head_down(amount=50)`: Shift projection down (positive Y)
- `center_head()`: Return to center position (0, 0) smoothly
- `_start_head_movement(target_x, target_y)`: Internal animation trigger with clamping

**Socket Commands:**
- `turn_left [amount]`, `turn_right [amount]`, `turn_up [amount]`, `turn_down [amount]`
- Optional amount parameter (default 50px), parsed from command arguments
- `center_head`: Returns to neutral position
- All movements respect ±500px boundary clamping

**Animation Pattern — Smooth State Transitions:**
This establishes the pattern for animating orthogonal state variables (like projection offset). Key principles:
1. **Capture-interpolate-set**: Store start position, capture target, interpolate over time
2. **Easing functions**: Use cubic ease-in-out for natural motion (avoids linear robotic feel)
3. **Frame-based progress**: Increment by `delta_time / duration` at 60 FPS
4. **Exact completion**: Set to exact target on completion (no accumulation error)
5. **Independent animation**: Runs in update() loop alongside other animations without interference

**3D Illusion Mechanism:**
- Entire face shifts as a unit via projection offset applied to center coordinates
- Creates parallax effect simulating head rotation/tilt
- Smooth animation (0.5s) prevents jarring jumps, enhances 3D perception
- Multiple sequential turns accumulate naturally (e.g., left 50px, then right 100px = net +50px)

**Graphics Insight — Animation vs Manual Control:**
The projection offset system now supports two interaction modes:
1. **Manual jogging** (`jog_projection`, arrow keys): Instant offset changes for alignment
2. **Animated movement** (`turn_head_*`): Smooth transitions for performative 3D effect
Both modify the same state variables but serve different use cases. Manual jogging is for setup/calibration, animated movement is for runtime performance.

**Verification:**
- Created `test_animated_head_movement.py` for manual socket command testing
- All methods compile and are callable
- Socket server handles all five head movement commands
- Animation state variables initialized in `__init__`
- Update loop correctly interpolates and sets projection offset each frame
- All 129 tests pass including 44 head movement tests

**Test Corrections (2025-02-23):**
Fixed pixel coordinate sampling in head movement tests. Eyes render at `center_y - 50` (not at screen center), so directional movement tests needed Y coordinate adjustment to match actual eye position. This highlights importance of understanding render geometry when writing pixel-level tests.

### Nose Rendering and Animation (Issue #19)

**Implementation:** Added nose graphics system with triangle rendering and two animation modes (twitching and scrunching).

**Nose Specifications:**
- Shape: 40×50px white filled triangle, apex UP
- Position: `center_y + 15` (centered between eyes at `center_y - 50` and mouth at `center_y + 80`)
- Rendering: `pygame.draw.polygon()` with three vertices (apex top, base left, base right)
- Projection mapping: White (255,255,255) on black background for 21:1 contrast

**Animation Patterns:**
- **Twitching**: ±8px horizontal oscillation, 5 complete cycles in 0.5 seconds
  - Sine wave: `amplitude * sin(2π * 5 * progress)` where progress is 0.0-1.0
  - Creates sniffing effect with rapid left-right motion
- **Scrunching**: Vertical compression 100%→50%→100% over 0.8 seconds
  - Sine wave compression: `scale = 1.0 - 0.5 * sin(π * progress)`
  - At progress 0.0: scale 1.0 (neutral)
  - At progress 0.5: scale 0.5 (max compression)
  - At progress 1.0: scale 1.0 (returned to neutral)
  - Creates disgust/smell reaction effect

**Frame-Based Animation Pattern:**
- Uses deterministic frame counting (`delta_time = 1/60`) instead of `time.time()`
- Progress advances by `delta_time / duration` each frame
- Auto-return to neutral when progress reaches 1.0
- Guard pattern: `if self.is_twitching or self.is_scrunching: return` prevents overlapping animations
- Orthogonal to expression state machine (nose animations don't affect expressions)

**Rendering Integration:**
- Added `_draw_nose(surface, center_x, center_y)` method
- Called from `_render_pumpkin_face()` after drawing eyebrows, before drawing mouth
- Nose follows projection offset automatically (receives offset-adjusted center coordinates)
- Triangle vertices calculated with current offsets and scale applied:
  - Apex: `(nose_x, nose_y - scaled_height)`
  - Base left: `(nose_x - width/2, nose_y)`
  - Base right: `(nose_x + width/2, nose_y)`

**Animation State Variables:**
- `nose_offset_x`, `nose_offset_y`: Current position offsets (twitch affects X)
- `nose_scale`: Vertical scale factor (scrunch affects this)
- `is_twitching`, `is_scrunching`: Boolean flags for active animation
- `nose_animation_progress`: 0.0-1.0 progress tracker
- `nose_animation_duration`: Duration in seconds (0.5 for twitch, 0.8 for scrunch)

**Public API:**
- `twitch_nose()`: Start twitching animation
- `scrunch_nose()`: Start scrunching animation
- `reset_nose()`: Immediately reset to neutral
- Socket commands: `twitch_nose`, `scrunch_nose`, `reset_nose`

**Verification:**
- Created `test_nose_rendering.py` with 14 automated tests
- All 57 tests pass (14 nose tests + 43 existing projection mapping tests)
- Visual test script `test_nose_movement.py` for manual verification
- Nose renders correctly on all 7 expression states
- Nose follows head movement (projection offset) correctly
- Animations complete and auto-reset as expected
- Guard pattern prevents animation interruption

**Graphics Pattern — Triangle Rendering with Scale:**
This establishes the pattern for rendering scalable shapes with vertex math. Key insight: calculate base shape vertices, apply scale transforms, then add position offsets. For nose: `apex_y = base_y - (height * scale)` creates vertical compression effect while keeping base anchored. This differs from pupil rendering (circular motion) and eyebrow rendering (tilted lines) — each facial feature uses geometry appropriate to its animation needs.

**Animation Pattern — Frame-Based Progress:**
Nose animations use the same deterministic frame-based pattern as head movement (not time-based like old implementations). This ensures consistent behavior across different frame rates and simplifies testing. Progress advances by fixed increments each frame, making animation timing predictable and reproducible.

📌 Team update (2026-02-23): Nose graphics and animations implemented for Issue #19

### Animation Timing Guidelines (Issue #39: Recording Skill)

**File:** `skill/timing_guidelines.md`

**Purpose:** LLM-friendly document that specifies how long each command takes and how to space animations for natural feel. This document is embedded in the system prompt for the recording skill generator (Gemini) so the LLM can construct realistic animation sequences.

**Key Timing Patterns Documented:**

1. **Per-command durations** — empirically derived from graphics rendering:
   - Blink: 200–300ms (250ms default)
   - Expression transition: 300–600ms (depends on emotional shift magnitude)
   - Gaze: 200–800ms (scales with angle: 200ms for ±10°, 800ms for ±80°)
   - Head turns: 300–600ms (scaling with pixel displacement)
   - Eyebrow movements: 150–400ms
   - Eye rolls: 1000–1500ms (full 360° rotation)
   - Nose animations: 200–500ms (twitch < scrunch < wiggle)

2. **Gap rules for pacing:**
   - Default minimum: 100–150ms between commands
   - Expression transitions need 300–500ms breathing room (don't interrupt mid-transition)
   - Eye movements can chain faster: 50–100ms (gaze → gaze → gaze)
   - Head turns need exclusive time: 300–600ms gap before next major animation

3. **Natural choreography patterns** — seven worked examples showing emotion-aligned sequences:
   - Surprise: eyebrow_raise → set_expression surprised → gaze upward
   - Wink & look: wink_right → gaze → happy expression
   - Confused: asymmetric eyebrows → glance sideways
   - Scared loop: scared expression → raised brows → rolling eyes → upward gaze
   - Exploration: chained gaze commands 400ms apart simulating "looking around"

4. **Anti-patterns to avoid:**
   - Eye rolls during happy/sad/angry (conflicts with emotion)
   - Back-to-back expression changes < 200ms (visual flicker)
   - Head turns while sleeping (breaks immersion)
   - Gaze > 70° (unnatural extremes)
   - Overlapping blinks/winks (rapid fluttering)

5. **Duration categories:**
   - Short: 2–5 seconds (simple sequences)
   - Medium: 5–15 seconds (multi-step choreography)
   - Long: 15–30 seconds (elaborate loops)

6. **Three worked examples** with detailed timing annotations:
   - Simple greeting (3s): blink → wink → happy → gaze
   - Scared reaction (5.5s): surprise → scared → rolling eyes → upward gaze → recovery
   - Thoughtful exploration (8.5s): gaze scanning loop → thinking pose → head turn → realization/happiness

**Design Pattern Insight:** Animation timing is orthogonal to the command vocabulary and JSON schema. By isolating timing knowledge in a single reference document, the LLM can focus on choreography choices (what emotion to convey) separately from technical constraints (how long a blink takes). This mirrors the graphics system's architecture where animations are modular and composable.

**Verification:** Generated document is structured for AI comprehension:
- Tables for quick reference (durations, command vocabulary)
- Clear "things to avoid" with reasoning
- Three complete worked examples showing annotation style
- Consistent terminology matching codebase (time_ms, args, expression enums)

📌 Team update (2026-03-02): Animation timing guidelines created for LLM skill generator (Issue #39)

### SVG Logo Design for GitHub Pages Site Header (Issue #57)

**File:** `docs/assets/img/logo.svg`

**Design:** Widescreen logo (viewBox 0 0 200 60) for dark background (#1a1a1a) site header. Left side: jack-o-lantern pumpkin icon (~50px wide). Right side: "Mr. Pumpkin" text in system-ui sans-serif at 22px/600 weight.

**Pumpkin Icon Construction:**
- Three overlapping ellipses create classic pumpkin silhouette (center + two side lobes), all #FF6B00
- Green stem: rounded rect, #3a7a20
- White triangular eyes and nose using `<polygon>`
- Jagged toothed mouth using a multi-point polygon (11 vertices tracing teeth + base)
- Subtle ridge: semi-transparent vertical line through center lobe

**Key SVG Patterns:**
- `viewBox` enables scaling from 32px height to full desktop width without quality loss
- Layering order: lobes → ridge → features (eyes/nose/mouth on top)
- No external fonts or images — fully self-contained inline SVG
- All feature colors: white (#FFFFFF) on orange (#FF6B00) body — consistent with projection mapping design language (high contrast features)
- `role="img"` + `<title>` for accessibility

**Design Insight:** The pumpkin lobe shape is most convincingly achieved with three overlapping ellipses (not a single distorted circle). The jagged mouth requires careful vertex ordering: trace the top jaw teeth, then close via the bottom jaw baseline. This produces a clean filled polygon with no stray strokes needed.

📌 Team update (2026-03-03): SVG logo created for GitHub Pages header (Issue #57)

📌 Team update (2026-03-03): Jekyll GitHub Pages site built by Vi for Issue #57; PR #58 open — Ekko contributed SVG logo (docs/assets/img/logo.svg)

### Viseme Mouth Rendering (Issue #59)

**Implementation:** Added visual rendering for speech visemes to support lip-sync animation. This allows the mouth to override expression-driven shapes when speaking.

**Architecture — Speech Override Pattern:**
- `_get_mouth_points()` checks `self.mouth_viseme` at the TOP before any expression logic
- If viseme active → delegate to `_get_viseme_points()` instead of expression mouth
- If viseme None → fall through to existing expression rendering (no behavior change)
- This creates clean separation: speech overrides expressions when active

**Viseme Shapes Implemented:**
| Viseme | Type | Rendering Method |
|--------|------|-----------------|
| `"closed"` | Line | Horizontal line 100px wide (cx±50), thickness 8 |
| `"wide"` | Line | Horizontal line 180px wide (cx±90), thickness 6 |
| `"open"` | Filled | Ellipse 80×60px at (cx-40, mouth_y-30) |
| `"rounded"` | Filled | Circle radius 25px at (cx, mouth_y) |

All visemes positioned at `mouth_y = center_y + 80` (same as expression mouths).

**Rendering Flow:**
1. `_get_viseme_points(cx, cy, viseme)` returns point list or empty list
   - Line visemes ("closed", "wide"): return 2-point line
   - Filled visemes ("open", "rounded"): return empty list
2. `_draw_mouth()` checks empty points first:
   - If viseme "open" or "rounded" → draw filled shape, early return
   - Else fall through to expression shapes (surprised/scared)
3. For non-empty points: thickness depends on viseme
   - "wide" viseme uses thickness 6 (thinner for wider line)
   - All other mouths use thickness 8

**Key Implementation Details:**
- `_get_viseme_points()` added AFTER `_get_mouth_points()` (line 231)
- Speech override check added at TOP of `_get_mouth_points()` (line 198-200)
- Viseme filled shapes take PRIORITY in `_draw_mouth()` (line 508-515)
- Line thickness made dynamic: `thickness = 6 if self.mouth_viseme == "wide" else 8` (line 527)
- No changes to expression mouth logic — all existing expressions preserved

**Graphics Pattern — Override Architecture:**
This establishes the pattern for temporary feature overrides that don't disturb underlying state machines. The viseme system:
- Doesn't modify `current_expression` or expression transition logic
- Short-circuits the rendering path, not the state path
- Returns to expression control when `mouth_viseme = None`
- Uses early-return pattern to cleanly separate code paths

**State Management (by Vi):**
- `self.mouth_viseme`: Current viseme name or None
- `set_mouth_viseme(viseme)`: Activate speech override
- `reset_mouth()`: Return to expression control
- State persists across frames until explicitly reset

**Projection Mapping Consistency:**
- All visemes use white features (255,255,255) on black background
- Line thicknesses (6-8px) maintain visibility at projection distances
- Filled shapes sized for clear visibility: 80×60 ellipse, radius 25 circle
- Position consistency: all mouths at same vertical offset (cy + 80)

**Verification:**
- Syntax check passes
- All four viseme shapes implemented per spec
- Expression mouths unchanged (happy, sad, angry, surprised, scared, neutral, sleeping)
- No changes to eyes, eyebrows, nose, or other features

📌 Team update (2026-03-03): Viseme mouth rendering implemented for Issue #59 lip-sync feature


## Learnings

### Issue #92 Bash Rescue (2026-03-13)

**Files shipped:**
- update.sh
- .gitattributes
- README.md
- docs/auto-update.md
- tests/test_pi_install_scripts.py

**What mattered:**
- `update.sh` must stay checked in with Unix LF endings or real `bash -n` validation becomes unreliable on the shipped file.
- Enforcing `*.sh text eol=lf` in `.gitattributes` is the lightweight repo-level guard that keeps the Raspberry Pi updater shippable across Windows working trees.
- The approved Raspberry Pi updater contract is non-root by default: skip apt-managed packages during unattended updates unless `MR_PUMPKIN_ALLOW_PI_APT_UPDATE=1` is explicitly set.

**Focused validation used:**
- `bash -n install.sh`
- `bash -n update.sh`
- `python -m pytest tests/test_pi_install_scripts.py tests/test_auto_update.py -q`

### Nav Layout Fix — Issues #61 & #62 (2026-01-01)

**Files changed:**
- docs/assets/css/style.css — two surgical edits

**Layout structure discovered:**
The Jekyll site header (docs/_layouts/default.html) uses a flat flex container .header-inner containing three direct children in DOM order:
1. .nav-toggle (hamburger button, display:none on desktop, visible on mobile)
2. .site-nav (horizontal nav links, lex:1, collapses to dropdown on mobile)
3. .header-search (search form with fixed-width input + icon button)

The CSS also defines .header-top and .header-bottom classes that are **not used** in the HTML — they appear to be leftover from an earlier two-row design.

**Root cause of bugs:**
- .header-inner had lex-direction: column — this stacked all three children vertically, causing the search form to stretch to full page width on desktop (#62) and the hamburger/search to stack vertically instead of side-by-side on mobile (#61).

**Fixes applied:**
1. Changed .header-inner to lex-direction: row; align-items: center — desktop now shows nav links spanning center with search pinned right (search input has explicit width: 160px; the 🔍 button sits inline at the right of the pill-shaped form).
2. In @media (max-width: 768px):
   - Added lex-wrap: wrap to .header-inner so the opened nav can flow to a second row
   - Added margin-left: auto to .header-search to push it to the right, leaving hamburger at the left
   - Added order: 10 to .site-nav so when opened (display: flex; width: 100%) it wraps below the hamburger+search top bar

**CSS patterns noted:**
- All desktop nav is handled without @media — mobile overrides live in @media (max-width: 768px)
- The .site-nav.open class is toggled by inline JS in default.html
- Search input has explicit widths: 160px desktop, 120px mobile
