# Design Review Ceremony — Issue #16: Eyebrow Animation
**Date:** 2026-02-22  
**Facilitator:** Jinx (Lead)  
**Participants:** Ekko (Graphics), Vi (Backend), Mylo (Tester)  
**Status:** Complete

---

## Requirements Summary
- Add eyebrows to the projection and implement their movement to enhance emotional range
- Eyebrows should change in different modes (angry, surprised, etc.)
- Should be able to rise or lower eyebrows together and independently
- When winking, blinking, or closing eyes, eyebrows should move as well

---

## 1. Key Architecture Decisions

### Orthogonal State Design
**Decision:** Eyebrow offsets are stored independently from expression state machine, following the same pattern as gaze and rolling animations.

**Rationale:** Satisfies orthogonal-animation-state pattern — user can raise/lower eyebrows independently of expression changes, and expression changes don't reset eyebrow offsets.

**Implementation:**
```python
self.eyebrow_left_offset = 0.0   # persistent user control, pixels
self.eyebrow_right_offset = 0.0  # range: [-50, +50]
```

### Derived Transient Animation (No Capture Required)
**Decision:** Blink/wink eyebrow movement is computed at render time from existing `blink_progress` and `wink_progress` — NOT stored in state variables.

**Rationale:** Satisfies Capture-Animate-Restore pattern without adding new capture fields. Since the transient lift is purely a function of animation progress (already captured), base eyebrow state is never mutated during animations — therefore it's automatically "restored" when animation ends.

**Implementation:**
```python
# Computed in _draw_eyebrows (not stored):
blink_lift = 8.0 * sin(blink_progress * π)  # both brows during blink
wink_lift = 8.0 * (1.0 - eye_scale)         # winking eye's brow only
```

### Expression-Driven Baseline
**Decision:** Each expression defines a baseline eyebrow Y-position and angle/tilt. User offsets and animation deltas stack additively on top of this baseline.

**Rationale:** Separates expression design concerns (Ekko's domain) from state management (Vi's domain). Expression transitions can smoothly interpolate the baseline while user offsets remain untouched.

### Projection-First Rendering
**Decision:** Eyebrows rendered as thick white lines (thickness 8, width 70px), tilted via angle_offset. No curves, no anti-aliasing.

**Rationale:** Matches existing constraint: pure white (255,255,255) on pure black (0,0,0). Straight lines render crisply on projector with no intermediate colors.

---

## 2. Data Model

### State Variables (Backend — Vi's Responsibility)
```python
# New persistent fields in PumpkinFace.__init__:
self.eyebrow_left_offset = 0.0   # pixels, clamped [-50, +50]
self.eyebrow_right_offset = 0.0  # pixels, clamped [-50, +50]
                                 # Sign convention: NEGATIVE = raise, POSITIVE = lower (screen Y coords)

# No new animation loop fields needed — blink/wink eyebrow lift derived from existing:
# - is_blinking, blink_progress
# - is_winking, winking_eye, left_eye_scale, right_eye_scale
```

### Rendering Parameters (Graphics — Ekko's Responsibility)
| Expression | brow_y_gap (above eye center) | angle_offset (tilt) | Notes |
|---|---|---|---|
| NEUTRAL | -55 | 0 | Flat, centered |
| HAPPY | -50 | +3 | Slightly raised outer corners, relaxed |
| SAD | -60 | -8 | Inner corners raised — "worried" slope |
| ANGRY | -50 | -12 | Inner corners sharply lowered — classic V-shape |
| SURPRISED | -70 | +5 | Eyebrows high and arched slightly |
| SCARED | -65 | -5 | High but with inner-up droop |
| SLEEPING | hidden | — | No brows drawn (eyes are lines) |

**Rendering formula:**
```python
final_brow_y = expression_baseline_y(current_expression)
             + eyebrow_offset                # persistent user control
             + blink_lift_delta(blink_progress)  # transient, computed
             + wink_lift_delta(wink_progress, winking_eye)  # transient, computed
```

**Tilt (angle_offset):** Positive = outer corners up (surprised), Negative = inner corners up (angry/sad). Drawn as line from `(cx-35, y+offset)` to `(cx+35, y-offset)`.

---

## 3. Interface Contracts

### Vi → Ekko (Backend exposes to Graphics)
```python
# Persistent user control:
face.eyebrow_left_offset: float   # [-50, +50]
face.eyebrow_right_offset: float  # [-50, +50]

# Expression state (already exists):
face.current_expression: Expression
face.target_expression: Expression
face.transition_progress: float   # [0, 1] — Ekko MUST interpolate eyebrow baseline during transitions

# Animation state (already exists):
face.is_blinking: bool
face.blink_progress: float        # [0, 1]
face.is_winking: bool
face.winking_eye: str | None      # 'left' or 'right'
face.left_eye_scale: float        # [0, 1] — Ekko uses for wink lift
face.right_eye_scale: float       # [0, 1]
```

### Ekko → Vi (Graphics needs from Backend)
- **Clarification of sign convention:** CONFIRMED negative offset = raise, positive = lower (screen Y increases down)
- **Clamping:** Vi clamps at set-time to [-50, +50]. Ekko applies final bounds-checking at render to prevent off-screen positions (especially SURPRISED + max raise)
- **SLEEPING behavior:** Vi confirms `current_expression == SLEEPING` → Ekko skips brow rendering entirely

---

## 4. Commands and Controls

### Socket Commands (Vi implements in `_run_socket_server`)
| Command | Action | Example |
|---|---|---|
| `eyebrow_raise` | Raise both by 10px | `eyebrow_raise` |
| `eyebrow_lower` | Lower both by 10px | `eyebrow_lower` |
| `eyebrow_raise_left` | Raise left by 10px | `eyebrow_raise_left` |
| `eyebrow_lower_left` | Lower left by 10px | `eyebrow_lower_left` |
| `eyebrow_raise_right` | Raise right by 10px | `eyebrow_raise_right` |
| `eyebrow_lower_right` | Lower right by 10px | `eyebrow_lower_right` |
| `eyebrow <val>` | Set both to absolute offset | `eyebrow -20` (raises both 20px) |
| `eyebrow_left <val>` | Set left to absolute offset | `eyebrow_left 10` |
| `eyebrow_right <val>` | Set right to absolute offset | `eyebrow_right -15` |
| `eyebrow_reset` | Reset both offsets to 0.0 | `eyebrow_reset` |

**Step size:** 10.0 pixels  
**Clamping:** [-50, +50] enforced at set-time

### Keyboard Shortcuts (Vi implements in `_handle_keyboard_input`)
| Key | Action |
|---|---|
| `U` | Raise both eyebrows |
| `J` | Lower both eyebrows |
| `[` | Raise left eyebrow |
| `]` | Raise right eyebrow |
| `Shift+[` (`{`) | Lower left eyebrow |
| `Shift+]` (`}`) | Lower right eyebrow |

**Rationale:** U/J are vertical neighbors (up/down). `[`/`]` are natural left/right mnemonics. No conflicts with existing `1-7, B, L, R, C, X, ESC`.

---

## 5. Expression-Specific Eyebrow Shapes

See **Section 2 — Rendering Parameters** table above.

**Critical behaviors:**
- **ANGRY:** Inner corners sharply down (`angle_offset = -12`), creating aggressive V-shape
- **SURPRISED:** High and arched (`y_gap = -70`, `angle_offset = +5`)
- **SAD:** Inner corners raised (`angle_offset = -8`), "worried" slope opposite to ANGRY outer corners
- **SLEEPING:** Eyebrows hidden entirely (eyes are lines, brows would clutter)

**All other expressions:** Subtle variations in height and tilt to support emotional range without overplaying.

---

## 6. Animation Behavior During Blink/Wink/Sleeping

### Blink
- **Both eyebrows rise 8px** during the close phase (peak at `blink_progress = 0.5`), return during open phase
- Formula: `blink_lift = 8 * sin(blink_progress * π)`
- Additive on top of `eyebrow_offset` — user-set offsets are NOT mutated
- Natural mimicry of squint-and-relax

### Wink
- **Only the winking eye's eyebrow lifts**, derived from `left_eye_scale` / `right_eye_scale`
- Formula: `wink_lift = 8 * (1.0 - eye_scale)` for the winking side only
- Other eyebrow remains at base position
- Additive, not stored — same pattern as blink

### Sleeping
- **Eyebrows not rendered** when `current_expression == SLEEPING`
- Rationale: Eyes are flat lines (not circles), brows would float disconnectedly above nothing visible
- Cleaner projection aesthetic

### Expression Transition
- **Eyebrow baseline interpolates** using `transition_progress` between `current_expression` and `target_expression`
- User offsets (`eyebrow_left_offset`, `eyebrow_right_offset`) remain constant across transitions
- Ekko must lerp the baseline Y and angle, not snap

---

## 7. Risks and Mitigations

### Risk: Eyebrows clip off-screen (SURPRISED + max raise)
**Mitigation:** Ekko applies final bounds-check at render time. Worst case: `cy - 20 (SURPRISED eye) - 70 (brow gap) - 50 (max raise) = cy - 140`. At `cy = 540`, that's `y = 400` — safe. Ekko will clamp to `y >= 350` as hard floor.

### Risk: Eyebrows overlap eyes when lowered
**Mitigation:** Vi clamps to `+50` max lower. Ekko enforces minimum 5px gap between brow bottom edge and eye top edge. If gap < 5px, skip rendering brow (prevents white blob on projector).

### Risk: Expression change mid-blink leaves eyebrows out-of-sync
**Mitigation:** Eyebrow offset is orthogonal — not tied to `pre_blink_expression`. When blink completes and restores `current_expression`, eyebrow offsets are unchanged (they were never written during blink). No restoration logic needed.

### Risk: "Move during blink/wink" is ambiguous in requirements
**Mitigation:** CLARIFIED — 8px rise during blink (both), 8px rise during wink (winking side only). Formula and phase defined above. Mylo will test at `blink_progress = 0.5` for peak lift.

### Risk: Independent control vs. expression override (offset vs. absolute)
**Mitigation:** CLARIFIED — eyebrow offsets are additive on expression baseline, following the same pattern as gaze. `set_expression()` never touches `eyebrow_offset` fields. User can raise brows, switch to ANGRY, and the raise stacks on ANGRY's baseline.

---

## 8. Action Items

### Ekko (Graphics Developer)
- [ ] Implement `_draw_eyebrows(surface, left_pos, right_pos, current_expression, transition_progress)`
- [ ] Add per-expression baseline lookup table (Y-gap, angle_offset)
- [ ] Compute blink lift as `8 * sin(blink_progress * π)` when `is_blinking`
- [ ] Compute wink lift as `8 * (1.0 - eye_scale)` for winking eye only
- [ ] Interpolate baseline during `transition_progress < 1.0`
- [ ] Skip rendering when `current_expression == SLEEPING`
- [ ] Apply final bounds-check: `y >= 350`, skip if gap to eye < 5px
- [ ] Call `_draw_eyebrows` from main render loop after `_draw_eyes`

### Vi (Backend Developer)
- [ ] Add state variables: `self.eyebrow_left_offset = 0.0`, `self.eyebrow_right_offset = 0.0`
- [ ] Implement socket commands: `eyebrow_raise`, `eyebrow_lower`, `eyebrow_raise_left`, `eyebrow_lower_left`, `eyebrow_raise_right`, `eyebrow_lower_right`, `eyebrow <val>`, `eyebrow_left <val>`, `eyebrow_right <val>`, `eyebrow_reset`
- [ ] Implement keyboard handlers: `U`, `J`, `[`, `]`, `{`, `}`
- [ ] Clamp offsets to [-50, +50] at set-time
- [ ] Verify `set_expression()` does NOT touch eyebrow offsets (orthogonality check)
- [ ] Add docstring comments clarifying sign convention and blink/wink behavior

### Mylo (Tester)
- [ ] Write per-expression static position tests (verify baseline Y and angle for all 7 expressions)
- [ ] Write independent control tests (raise left → right unchanged, raise both → symmetric)
- [ ] Write blink integration test (assert brows at +8px at `blink_progress = 0.5`, restored at 1.0)
- [ ] Write wink integration test (assert winking brow lifts, other unchanged)
- [ ] Write expression transition test (baseline interpolates, offsets unchanged)
- [ ] Write edge case tests: max raise during SURPRISED (no clip), max lower (no overlap with eyes), SLEEPING (brows hidden)
- [ ] Pixel-sampling validation for projection colors (white brows on black background)
- [ ] Test all socket commands and keyboard shortcuts are wired correctly

---

## Ceremony Notes

**Ekko's insight:** Using pure line rendering (no curves) matches Projection-First constraint perfectly. Tilt via angle_offset (not rotation matrices) keeps math simple.

**Vi's insight:** Derived transient animation (blink/wink lift computed at draw time) satisfies Capture-Animate-Restore with zero new state fields. Cleanest possible implementation.

**Mylo's insight:** Expression change mid-blink is the hairiest edge case. Orthogonal offset design prevents the bug by never mutating base state during animations.

**Consensus:** Architecture is sound. Implementation can proceed in parallel (Ekko graphics, Vi backend, Mylo tests). No blocking dependencies identified.

---

**Next Steps:** Ekko and Vi implement in parallel. Mylo writes test cases upfront (TDD). Regroup for code review once Ekko's `_draw_eyebrows` is functional.
