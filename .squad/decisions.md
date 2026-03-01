# Team Decisions — Mr. Pumpkin

*This file is the authoritative record of all architectural, scope, and process decisions made by the squad.*

---

### 2026-02-16: Team initialized

**By:** Squad (Coordinator)  
**What:** Squad team established with 4 AI agents (Jinx, Ekko, Vi, Mylo), Scribe, and Ralph. Universe: Arcane.  
**Why:** Project kickoff — assembled team to deliver animated pumpkin face project.

---

### 2026-02-19: Projection Mapping Implementation (consolidated)

**By:** Ekko, Mylo  
**What:** Defined projection mapping color scheme and test strategy. Black background (0,0,0) with white features (255,255,255) as standard. Comprehensive test suite covers colors, contrast (15:1 minimum), all expression states, and edge cases.  
**Why:** Projection mapping requires maximum contrast — black prevents projector light bleed, white features at maximum brightness ensure clear illumination. Proactive testing enables parallel development and ensures all six expressions work reliably in projection mode.

---

### 2026-02-19: Projection-First Rendering Architecture

**By:** Jinx (Lead)

**What:** Established projection mapping as the core rendering constraint, not an optional mode. All graphics use pure black background (RGB 0,0,0) and pure white features (RGB 255,255,255), with zero intermediate colors.

**Why:** 
- **Physical surface requirements**: Projection onto 3D curved geometry at oblique angles causes falloff—intermediate colors (grays) disappear while pure white remains visible at extreme angles and pure black stays black regardless of angle.
- **Single pipeline over feature flags**: Avoid branching logic (projection_mode on/off) that creates untested code paths. Instead, make projection the baseline. Every future expression is automatically projection-ready.
- **21:1 contrast ratio safety**: Pure black-to-white contrast yields 21:1 ratio, 40% above our 15:1 minimum threshold, providing margin for real-world conditions (stage lighting, angle variation, ambient light).
- **Enables parallel team velocity**: With constraints established architecturally, Ekko (Graphics) and Mylo (Testing) can work in parallel—Ekko designs six expressions within black/white palette, Mylo writes tests validating the contract before implementation finishes.

**Implications:**
- No color gradients, shadows, or anti-aliasing in core features
- All future expression work inherits projection safety by design
- Testing can be specificity-focused: "pixel at coordinate X is exactly (255,255,255)" rather than vague "colors look right"

---

### 2026-02-20: Python Versioning via VERSION File

**By:** Jinx

**What:** Replaced Node.js tooling in all three GitHub Actions workflows with Python equivalents; versioning via a flat `VERSION` file at repo root.

**Why:** This is a Python project — workflows were scaffolded for Node.js by default. `actions/setup-node`, `node --test`, and `package.json` version reads have no place here. `actions/setup-python` + `python -m pytest` + `cat VERSION` is the correct stack. The `VERSION` file is the simplest possible versioning mechanism for shell-friendly CI scripts.

---

### 2026-02-20: Sleeping Expression Closed-Eye Design

**By:** Ekko (Graphics Dev)

**Issue:** #4 — Add a sleeping expression

**What:** Implemented sleeping expression with closed eyes rendered as horizontal white lines for optimal projection mapping.

**Design Choice:** Closed eyes are rendered as **horizontal white lines** (60px width, 8px thickness) rather than curved or arc shapes.

**Rationale:**
1. **Projection Mapping Contrast:** Straight horizontal lines maintain maximum white surface area on black background, ensuring 15:1+ contrast ratio
2. **Visual Simplicity:** Universal symbol for closed eyes in 2D animation/emoji design
3. **Rendering Consistency:** Uses same 8px line thickness as mouth curves for visual cohesion
4. **Performance:** Simple line rendering vs complex arc/curve calculations

**Implementation Pattern:**
- Early return in `_draw_eyes()` when `Expression.SLEEPING` detected
- Prevents rendering standard open eye circles
- Pattern reusable for future expression-specific eye states (winking, squinting, etc.)

**Socket Server Compatibility:** Socket server automatically supports new expression via enum parsing — no backend changes required.

---

### 2026-02-20: Triage Decisions — Issues #4 and #5

**By:** Jinx (Lead)

**Issue #4: Add a sleeping expression**
- **Assigned squads:** squad:ekko (primary), squad:vi, squad:mylo
- **Scope:**
  1. Add `SLEEPING = "sleeping"` to `Expression` enum
  2. Implement closed eye shape in `_draw_eyes()` (horizontal white line for maximum projection contrast)
  3. Add keyboard shortcut (key 7 for sleeping)
  4. Socket server automatically handles new enum value
  5. Add test class `TestSleepingExpression` to validation suite
- **Complexity:** Low (1-2 hours)
- **Dependencies:** None

**Issue #5: Add a blink animation**
- **Assigned squads:** squad:ekko (primary), squad:mylo
- **Scope:**
  1. Add `blink()` method to `PumpkinFace` class
  2. Implement temporary state change: current expression → closed → same expression (not NEUTRAL)
  3. Slower transition speed than normal expressions (0.03 vs 0.05)
  4. Add `"blink"` command handler to socket server (NOT an Expression enum value, it's an animation command)
  5. Handle edge cases: blink during expression transition, rapid blink commands
- **Architectural challenge:** Current transition system is expression-to-expression. Blink is a temporary detour that must return to the original state. **Solution:** Add `is_blinking` flag + `blink_progress` counter orthogonal to expression transitions.
- **Animation phases:**
  1. Eyes open → closing (progress 0.0 to 0.5)
  2. Eyes fully closed (brief hold, ~100ms)
  3. Eyes opening → open (progress 0.5 to 1.0)
  4. Return to exact original expression
- **Complexity:** Medium (3-4 hours)
- **Dependencies:** Should implement after #4 (reuses closed-eye rendering)

---

### 2026-02-20: Release Package Plan — Issue #3

**By:** Jinx (Lead)

**Issue:** #3 — create a release package

**What:** ZIP archive distribution strategy with cross-platform install scripts, not pip package.

**Scope:**
- **Include:** pumpkin_face.py, client_example.py, README.md, requirements.txt, VERSION, test_projection_mapping.py
- **Exclude:** `.squad/`, `.github/`, `.git/`, `__pycache__/`, `.copilot/`, `docs/`
- **Cross-platform:** All code is platform-agnostic, pygame handles SDL2 abstraction
- **Raspberry Pi:** Requires SDL2 system libraries (`apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev`)

**Package Structure:**
```
mr-pumpkin-v0.1.0/
├── pumpkin_face.py
├── client_example.py
├── requirements.txt
├── README.md
├── VERSION
├── test_projection_mapping.py
├── install.sh          (Linux/macOS setup script)
└── install.ps1         (Windows setup script)
```

**Implementation Plan (Option A — Automated):**
1. Create `scripts/package_release.py` to automate ZIP creation
2. Update `.github/workflows/squad-release.yml` to attach ZIP to GitHub Release
3. Create install scripts: `install.sh` (Linux/macOS) and `install.ps1` (Windows)
4. Update README with "Installation from Release" section

**Dependency Pinning:**
```
pygame>=2.0.0,<3.0.0
pytest>=7.0.0,<9.0.0
```

**Complexity:** Medium (4-6 hours)  
**Owner:** Vi (Backend/Scripts)  
**Reviewer:** Jinx (Architecture)  
**Dependencies:** None

---

## Blink Animation Implementation — Ekko

**Date:** 2026-02-20  
**By:** Ekko (Graphics Dev)  
**Issue:** #5 — Add a blink animation  
**PR:** #7

Blink animation is implemented as an orthogonal animation system separate from the expression state machine, using `is_blinking` flag + `blink_progress` counter rather than as an Expression enum value.

The existing animation system uses Expression enum values with `current_expression` → `target_expression` transitions. A blink is fundamentally different: it's a temporary overlay that must return to the EXACT same expression afterward, not transition to a new state.

**Alternatives Considered:**
1. **Add BLINKING as Expression enum value** — Rejected because it would require complex state tracking to remember which expression to return to, and wouldn't compose well with expression transitions
2. **Interrupt expression transitions** — Rejected because it would create jarring visual glitches
3. **Orthogonal state system** — Chosen for clean separation of concerns

**State Variables (added to `__init__`):**
```python
self.is_blinking = False
self.blink_progress = 0.0
self.blink_speed = 0.03  # Slower than transition_speed (0.05)
self.pre_blink_expression = None
```

**Animation Phases:**
- **Closing:** progress 0.0 → 0.5, eye_scale 1.0 → 0.0
- **Hold closed:** progress 0.5 → 0.55 (~100ms hold at 60 FPS)
- **Opening:** progress 0.55 → 1.0, eye_scale 0.0 → 1.0

**Rendering Strategy:**
- Eyes render as vertically-scaled ellipses during partial blink (eye_scale < 1.0)
- When fully closed (eye_scale == 0.0), reuse sleeping expression's horizontal white lines
- Pupils scale proportionally to maintain visual coherence
- All states use pure black/white for projection mapping compliance

**Command Handling:**
- Socket server checks `data == "blink"` BEFORE `Expression(data)` parsing
- Keyboard `B` key triggers blink
- Guard prevents interrupting ongoing blink: `if not self.is_blinking`

**Benefits:**
1. **Composability:** Blink can overlay any expression without disrupting the expression state machine
2. **Clean separation:** Expression logic and blink logic don't interfere with each other
3. **Reusability:** Closed-eye rendering pattern from sleeping expression is reused
4. **Extensibility:** Future animations (wink, eye dart) can follow same orthogonal pattern

**Trade-offs:**
- Slightly more complex state management (two parallel systems)
- Must ensure both systems use compatible rendering (maintained via eye_scale abstraction)

**Validation:**
- Manual testing confirmed smooth blink animation at 60 FPS
- Socket command `"blink"` triggers animation successfully
- Keyboard `B` shortcut works as expected
- Returns to original expression after completion
- Pure black/white rendering maintained throughout animation

---

## Blink Test Architecture — Mylo

**By:** Mylo (Tester)  
**Date:** 2026-02-20  
**Issue:** #5 — Add a blink animation

Comprehensive test suite (12 tests) covering state machine behavior, animation phases, and integration points for blink animation feature.

**Why:**
- Blink is fundamentally different from expression transitions — it's a temporary animation detour that must restore the original state
- Animation progress tracking (0.0 to 1.0) requires different testing approach than static expression states
- Non-interrupting behavior is critical: calling blink() during blink should not reset progress
- Expression restoration must be EXACT (not default to NEUTRAL) — this is user-facing correctness

**Key Design Choices:**

1. **State Machine Validation Over Visual Testing** — Unlike expression tests that sample pixels, blink tests validate `is_blinking` flag lifecycle, `blink_progress` advancement per update() call, and `pre_blink_expression` preservation. Animation correctness is a state machine problem first, rendering problem second.

2. **Iteration Count for Completion Tests** — Tests use 40 update() calls to complete blink (blink_speed=0.03 → 34 updates theoretical, 40 for margin). Deterministic completion testing without timing dependencies.

3. **Parametrized Test for All 7 Expressions** — Single test multiplied across NEUTRAL, HAPPY, SAD, ANGRY, SURPRISED, SCARED, SLEEPING. Blink must work correctly from ANY starting expression. Parametrization prevents copy-paste test sprawl.

4. **Socket "blink" as Non-Enum Command** — Test validates "blink" string triggers blink() method, NOT Expression enum parsing. Establishes pattern for future animation commands (wink, nod, etc.) without polluting Expression enum.

5. **Speed Differential Validation** — Explicit test: `blink_speed (0.03) < transition_speed (0.05)`. Blink feeling natural depends on being SLOWER than expression changes. This is a UX requirement codified in tests.

**Test Coverage Gaps (Acknowledged):**
- Exact visual rendering of eye closure phases not tested (covered by projection mapping tests)
- Blink during mid-expression transition is edge case — implementation may choose to block or queue
- Rapid blink rate-limiting is UX polish, not core functionality

**Impact on Future Work:** This test pattern establishes a template for future animation commands (wink, nod, bounce), state machine testing over pixel-sampling for animations, and the socket command extension point (string commands beyond Expression enum).

**Risks:**
- Tests assume 40 iterations sufficient for all frame rates (60fps = 0.67 seconds)
- No validation of VISUAL smoothness, only state correctness
- Keyboard shortcut B may conflict with future features

These tests were written BEFORE implementation landed (parallel to Ekko's work on squad/5-blink-animation branch).

---

### 2026-02-20: .squad/ tracking policy

**By:** Jinx

**What:** .squad/ and .squad-templates/ are tracked on dev but NOT on preview or main. These directories are in .gitignore on preview and main. When merging dev→preview, untrack them with `git rm -r --cached .squad/ .squad-templates/` before committing the merge.

**Why:** .squad/ is squad internal state — it should not ship with the product.

---

### 2026-02-20: Release Package Implementation — ZIP with Cross-Platform Install Scripts

**By:** Vi (Backend Dev)

**Issue:** #3 — create a release package

**What:** Implemented ZIP-based distribution system with shell install scripts for cross-platform deployment.

**Implementation:**

1. **Package Builder** (`scripts/package_release.py`):
   - Python script using zipfile module
   - Reads VERSION file dynamically
   - Creates `mr-pumpkin-v{VERSION}.zip` with nested folder structure
   - Includes: source files, docs/, LICENSE, requirements.txt, install scripts
   - Excludes: .squad/, .github/, .git/, __pycache__/, .copilot/

2. **Install Scripts**:
   - `install.sh` (Linux/macOS/Raspberry Pi):
     - Detects OS via `$OSTYPE` and `/proc/device-tree/model`
     - On Raspberry Pi/Debian/Ubuntu: installs SDL2 system libs via apt-get
     - Runs `pip install -r requirements.txt` (global, not venv)
   - `install.ps1` (Windows):
     - PowerShell with error handling
     - Runs pip install with colored output

3. **CI/CD Integration** (`.github/workflows/squad-release.yml`):
   - After tests pass: `python scripts/package_release.py`
   - Attaches ZIP to GitHub Release: `gh release create ... {zipfile}`

4. **Dependency Pinning** (`requirements.txt`):
   - Changed from unpinned (`pygame`, `pytest`) to range constraints
   - `pygame>=2.0.0,<3.0.0` and `pytest>=7.0.0,<9.0.0`
   - Allows patch/minor updates, blocks breaking major versions

5. **Documentation** (`README.md`):
   - Added "Option 1: Download Release Package" section at top of Installation
   - Shows how to unzip and run install scripts
   - Kept "Option 2: Install from Source" below
   - Added SDL2 dependency note for Raspberry Pi/Linux

**Why:**

- **Raspberry Pi target:** Requires SDL2 system libraries before pygame installs. Shell script automates this.
- **Simple distribution:** ZIP archive is simpler than PyPI packaging for this use case (no wheel building, no setup.py complexity).
- **Cross-platform:** Python packaging script works on all platforms; shell scripts are idiomatic for their target OS.
- **Version management:** Single VERSION file at repo root is simpler than package.json or git-based versioning.
- **User experience:** "Download ZIP, unzip, run install script" is the simplest possible workflow for non-Python users.
- **CI/CD automation:** Building ZIP in GitHub Actions ensures every release is consistent and reproducible.

**Raspberry Pi SDL2 dependencies:** Required for Pi 3, 4, and 5:
```
libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

**Owner override:** Initial decision excluded docs/ folder. Owner explicitly requested inclusion of docs/ in release package.

---

### 2026-02-22: Eye Direction Control Design — Issue #22

**By:** Jinx (Lead), Ekko (Graphics), Vi (Backend)

**Date:** 2026-02-22

**Issue:** #22 — Eyes able to look left, right, up and down

**What:** Implemented eye direction control via X/Y degree angles (±90° range) with per-eye independent positioning. Users control gaze via `gaze` socket command supporting both synchronized and asymmetric eye movements.

**Data Model:**
- Per-eye state variables: `pupil_angle_left` and `pupil_angle_right` (stored as tuples with X/Y angles)
- Coordinate system: X axis (−90° = left, 0° = center, +90° = right), Y axis (−90° = down, 0° = center, +90° = up)
- Default position: (−45°, 45°) for both eyes, maintaining backward compatibility with 43 existing projection tests

**Rendering Contract:**
- Graphics converts angles to pupil pixel offsets via `sin()` function for natural acceleration curve
- Orbit radius (~14px) + pupil radius (15px) = 29.14px < eye radius (40px) ensures 10.86px safety margin
- Projection mapping compliant: pure black pupils on white eyes, no anti-aliasing

**Socket Command Format:**
- `gaze <x> <y>` — Both eyes synchronized
- `gaze <left_x> <left_y> <right_x> <right_y>` — Independent eye control
- Server-side clamping to ±90° range (silent clamp, not rejection)
- Keyboard shortcuts: arrow keys adjust gaze in 5° increments, `0` key resets to (0°, 0°)

**Animation Interaction:**
- **Expression changes:** Gaze persists (orthogonal systems)
- **Rolling animation:** Gaze paused during roll via capture-restore pattern; rejected if attempted during roll
- **Blink/Wink:** Gaze state preserved; eyes return to set angles after animation
- **Eye scale (blink):** Orbit radius scales with eye → pupils converge correctly

**Why This Design:**
1. Per-eye state enables asymmetric gaze (weird eye movements requirement)
2. X/Y angles are intuitive for users vs polar coordinates (left/right + up/down)
3. Arity-based parsing (`gaze 45 30` for both eyes, 4 args for independent)
4. Server-side validation + render-side clamping provides defense in depth
5. Persistence across expressions reduces command spam

**Trade-offs:**
- **Pros:** Orthogonal state independent from expressions, capture-restore for animations, per-eye control enables asymmetric effects, ±90° prevents escape
- **Cons:** More state variables (4 floats per eye), gaze "pauses" during rolling animation, instant changes (no easing yet)

---

### 2026-02-22: Release Process Workflow

**By:** Copilot (User Directive)

**Date:** 2026-02-22

**What:** Established release workflow: stage dev branch to preview for team review, then merge preview to main only after approval. Never merge dev directly to main.

**Process:**
1. Update VERSION file only (no automatic tags)
2. Create PR: dev → preview (for review)
3. Merge to preview once approved
4. squad-release workflow handles tagging and package creation automatically

**Why:** Separates concerns (manual version bump → automated release), ensures release quality, provides team visibility, prevents missed/double-tagging.

---

### 2026-02-22: Eyebrow Animation Architecture — Issue #16

**By:** Jinx (Lead), Ekko (Graphics), Vi (Backend), Mylo (Tester)

**Date:** 2026-02-22

**Status:** Design approved, implementation in progress (PR #24)

**Context:** Issue #16 — Eyebrow Animation. Design review ceremony with Jinx, Ekko, Vi, Mylo. Architectural decisions for orthogonal eyebrow state, expression-driven baselines, and projection-compliant rendering.

---

## Eyebrow Architecture Decisions

### Decision 1: Orthogonal Eyebrow State

**Decision:** Eyebrow offsets are stored independently from the expression state machine.

**Details:**
- Two persistent fields: `eyebrow_left_offset` and `eyebrow_right_offset` (floats, clamped [-50, +50])
- Expression changes via `set_expression()` do NOT reset or modify these offsets
- User can raise/lower eyebrows independently of expression, offset stacks additively on baseline

**Rationale:**
- Satisfies orthogonal-animation-state pattern (established for blink, wink, rolling)
- Allows independent control (raise/lower together and independently)
- Mirrors gaze system architecture: persistent user state + expression-driven baseline

**Implications:**
- `set_expression()` must not touch eyebrow offset state
- Expression transitions interpolate baseline; user offsets remain constant
- Final position = expression_baseline + user_offset + transient_animation_delta

---

### Decision 2: Derived Transient Animation (Blink/Wink Eyebrow Movement)

**Decision:** Eyebrow movement during blink/wink is computed at render time, NOT stored in state.

**Details:**
- Blink lift: `8 * sin(blink_progress * π)` — both eyebrows rise during close, return during open
- Wink lift: `8 * (1.0 - eye_scale)` — winking eye's eyebrow lifts proportional to eye closure
- No new capture fields needed (`pre_blink_eyebrow_offset`, etc.)

**Rationale:**
- Satisfies Capture-Animate-Restore pattern without adding state variables
- Base eyebrow state is never mutated during animations — automatically "restored" when animation ends
- Minimizes state complexity; mirrors how pupils are positioned during rolling

**Implications:**
- Eyebrow draw logic reads existing animation progress variables
- No restoration logic needed in update()
- Blink/wink eyebrow behavior visually coupled to eye animation

---

### Decision 3: Expression-Driven Baseline with Additive User Offset

**Decision:** Each expression defines baseline eyebrow Y-position and tilt angle. User offsets and animation deltas stack additively.

**Details:**
- Baseline table (EYEBROW_BASELINES):
  - NEUTRAL: y_gap = -55, angle = 0 (flat)
  - HAPPY: y_gap = -50, angle = +3 (relaxed)
  - SAD: y_gap = -60, angle = -8 (worried)
  - ANGRY: y_gap = -50, angle = -12 (aggressive V)
  - SURPRISED: y_gap = -70, angle = +5 (high arched)
  - SCARED: y_gap = -65, angle = -5 (raised drooped)
  - SLEEPING: hidden (no rendering)

- Final position formula: `brow_y = expression_baseline_y + eyebrow_offset + blink_lift + wink_lift`

**Rationale:**
- Separates expression design (graphics domain) from state management (backend domain)
- Enables smooth expression transitions while preserving user control
- Additive model is intuitive

**Implications:**
- Expression transitions interpolate baseline Y and angle
- Graphics renderer owns baseline table; backend owns offsets
- Clear interface boundary

---

### Decision 4: Projection-First Rendering — Straight Lines Only

**Decision:** Eyebrows rendered as thick white straight lines (thickness 8, width 70px), tilted via angle_offset.

**Details:**
- Shape: `pygame.draw.line(surface, (255,255,255), start_point, end_point, thickness=8)`
- Width: 70px (slightly wider than eye radius of 40)
- Tilt: angle_offset shifts endpoints vertically — positive = outer up (surprised), negative = inner up (angry/sad)

**Rationale:**
- Satisfies Projection-First Architecture: pure white on pure black
- Straight lines render crisply with no intermediate colors or anti-aliasing
- Simple geometry — no Bezier curves, no rotation matrices

**Implications:**
- Thickness matches mouth line thickness (8) for visual consistency
- Tilt range must be bounded to prevent unnatural shapes
- ANGRY inner-corner-down uses negative angle_offset

---

### Decision 5: Command Vocabulary and Control Mapping

**Decision:** Socket commands and keyboard shortcuts follow established pattern: step-based increment/decrement and absolute set.

**Details:**

**Socket commands (step = 10px):**
- `eyebrow_raise`, `eyebrow_lower` — both together
- `eyebrow_raise_left`, `eyebrow_lower_left` — left independently
- `eyebrow_raise_right`, `eyebrow_lower_right` — right independently
- `eyebrow <val>`, `eyebrow_left <val>`, `eyebrow_right <val>` — absolute set
- `eyebrow_reset` — both to 0.0

**Keyboard shortcuts:**
- `U` / `J` — raise/lower both (vertical neighbors)
- `[` / `]` — raise left/right (natural mnemonics)
- `{` / `}` (Shift+[/]) — lower left/right

**Rationale:**
- Mirrors existing command structure (blink, wink_left, gaze)
- Keyboard layout intuitive: U/J for up/down, brackets for left/right
- No conflicts with existing shortcuts

**Implications:**
- Socket parser handles multi-word commands and single-arg commands
- Keyboard handler distinguishes `[` from `{` (requires Shift detection)
- Client examples and documentation updated

---

### Decision 6: SLEEPING Expression — Eyebrows Hidden

**Decision:** When `current_expression == SLEEPING`, eyebrows are not rendered.

**Details:**
- SLEEPING eyes rendered as horizontal white lines (not circles)
- Eyebrows drawn above would float disconnectedly
- Cleaner projection aesthetic: sleeping face = minimal features

**Rationale:**
- Visual clarity: avoid disconnected white elements
- Simplifies rendering logic
- Natural behavior: sleeping faces have less prominent brows

**Implications:**
- Graphics renderer checks `current_expression == SLEEPING` before drawing
- User offset state preserved during SLEEPING — reappears when expression changes
- Test cases verify absence and reappearance

---

### Decision 7: Sign Convention — Negative = Raise, Positive = Lower

**Decision:** Eyebrow offset sign follows screen Y-coordinates: negative = raise (up), positive = lower (down).

**Details:**
- `eyebrow_left_offset = -20` means 20px higher than baseline
- `eyebrow_right_offset = 10` means 10px lower than baseline
- Clamped range: [-50, +50]

**Rationale:**
- Matches screen coordinate system (Y increases downward)
- Consistent with eye Y-offset logic
- Avoids double-negatives in render math

**Implications:**
- Socket `eyebrow_raise` decrements offset, `eyebrow_lower` increments
- Keyboard `U` key decrements, `J` key increments
- Documentation clarifies convention

---

### Decision 8: Edge Case Handling — Clamping and Overlap Prevention

**Decision:** Multi-layer clamping to prevent off-screen positioning and eye overlap.

**Details:**
- Set-time clamping: offsets clamped to [-50, +50] when user sets
- Render-time clamping: final Y position clamped to `y >= 350` (1080p canvas at cy = 540)
- Overlap prevention: if gap between brow bottom and eye top < 5px, skip rendering

**Rationale:**
- Set-time clamping prevents absurd input
- Render-time clamping accounts for additive stacking
- Overlap prevention maintains pure black/white separation

**Implications:**
- Graphics renderer computes gap between brow and eye
- Worst-case: SURPRISED (cy - 20) + max raise (-50) + blink lift (-8) = safe
- Test cases validate boundary conditions

---

## Implementation Summary

### Vi — Backend State & Commands

**Contribution:** Eyebrow state variables, helper methods, socket commands, keyboard shortcuts

**Changes to pumpkin_face.py:**
- 2 state variables: `eyebrow_left_offset`, `eyebrow_right_offset` (range [-50, +50])
- 8 helper methods for control
- 10 socket commands for remote control
- 6 keyboard shortcuts
- Orthogonal to expression state machine

**Validation:** All 43 existing tests pass. No breaking changes.

### Ekko — Graphics Rendering

**Contribution:** Eyebrow rendering with baseline table and animation integration

**Changes to pumpkin_face.py:**
- `EYEBROW_BASELINES` dictionary with expression-specific baselines
- `_get_eyebrow_baseline(expression)` method for interpolation
- `_draw_eyebrows()` method with:
  - Baseline position lookup
  - User offset application
  - Blink/wink lift integration
  - Collision detection
  - SLEEPING expression handling

### Mylo — Test Suite

**Contribution:** 37 tests across 6 test classes (test_eyebrow_animation.py)

**Coverage:**
- State Variables (8 tests)
- Orthogonality (11 tests)
- Commands (6 tests)
- Rendering (5 tests, skipped pending graphics)
- Animation Integration (4 tests)
- Edge Cases (4 tests)

**Results:** 29 passed, 8 skipped

---

## Approval

✅ Design approved for implementation  
✅ Parallel development ready (Ekko graphics, Vi backend, Mylo testing)


---

## Session Checkpoint — 2026-02-24 20:30:48

### 2026-02-22: Eyebrow Clipping Fixed - Removed Hardcoded Coordinate Clamp

**By:** Ekko  
**What:** Fixed eyebrow disappearance at high projection offsets by replacing hardcoded `y=350` clamp with screen-edge-relative clamp (`y=0`)  
**Why:** The hardcoded absolute coordinate clamp broke when projection offset shifted the coordinate system. Eyebrows are positioned relative to eyes (which include offset), so clamping must be relative to actual screen bounds, not arbitrary fixed values. This ensures eyebrows remain visible across the full ±500 pixel projection offset range.

**Impact:**
- Eyebrows now render correctly at all projection offset values
- Maintains existing collision detection to prevent eyebrow/eye overlap
- All 43 projection mapping tests continue to pass
- Pattern established: avoid absolute coordinate clamps when coordinate system can shift

**Files changed:**
- `pumpkin_face.py`: Line 371-373 (eyebrow floor clamp logic)
- `test_eyebrow_clipping.py`: New test file for extreme offset scenarios

---

### 2026-02-24: Animated Head Movement via Smooth Projection Offset Transitions

**By:** Ekko (Graphics Dev)

**What:** Implemented smooth animated head movement system that creates 3D illusion by interpolating projection offset over time. Head turns left, right, up, and down with ease-in-out animation spanning 0.5 seconds.

**Why:** 
- Issue #17 requested 3D head movement illusion with smooth transitions
- Manual projection jogging (arrow keys) provided instant offset changes but no animation
- Smooth animation enhances perceived 3D effect and provides performative capabilities
- Separates alignment/calibration use case (instant jog) from runtime performance (animated turns)

**Technical Approach:**
- Animation state: `is_moving_head`, progress tracker, start/target positions
- Ease-in-out cubic interpolation: `3t² - 2t³` for natural motion
- Duration: 0.5 seconds at 60 FPS (30 frames per turn)
- Update loop integration: Runs independently alongside blink/wink/roll animations
- Boundary clamping: ±500px limits enforced at animation start

**Pattern Established:**
This creates the "smooth state transition" animation pattern for orthogonal state variables:
1. Capture current state as start position
2. Set target state with boundary enforcement
3. Interpolate with easing function over fixed duration
4. Update state variable each frame in update() loop
5. Set exact target value on completion (prevents drift)

Similar to rolling eyes (rotates 360° from current angle, returns to exact start), but applied to spatial offset instead of angular motion.

**Socket Commands Added:**
- `turn_left [amount]`, `turn_right [amount]`, `turn_up [amount]`, `turn_down [amount]`
- `center_head` (returns to 0, 0)
- Default amount: 50px
- Supports custom amounts: `turn_left 100` shifts 100px left

**Alternative Considered:**
Could have extended manual jog system with animation flag, but decided separate methods provide clearer API:
- `jog_projection()`: Instant offset for calibration
- `turn_head_*()`: Animated movement for performance
Both share underlying projection offset state, serve different use cases.

**Impact:**
- Graphics rendering unchanged (projection offset already implemented)
- New animation runs in update() loop without interfering with expression transitions
- Socket server extended with 5 new commands
- Test script (`test_animated_head_movement.py`) validates smooth movement

**Future Considerations:**
- Could add animation speed parameter (currently fixed at 0.5s)
- Could support compound movements (diagonal turns with single command)
- Could add easing presets (linear, ease-in, ease-out, bounce)

---

### 2026-02-22: Mouth rendering signature updated to accept offset-adjusted coordinates

**By:** Ekko

**What:** Modified `_draw_mouth()` method signature to accept `cx` and `cy` parameters, matching the pattern used by other rendering methods. Updated surprised and scared mouth rendering to use these coordinates instead of hardcoded absolute screen positions.

**Why:** Fixed mouth clipping bug where surprised/scared expressions would render mouths at absolute screen coordinates, ignoring projection offset. This caused mouths to drop off-screen when projection was jogged to high Y offsets. By accepting offset-adjusted coordinates as parameters, mouth rendering now maintains consistency with the projection offset system, ensuring all facial features move together as a unit when projection alignment is adjusted.

**Impact:** Surprised and scared expressions now work correctly at all projection offsets. Reinforces the coordinate system consistency pattern where rendering methods accept transformed coordinates rather than accessing raw screen dimensions.

---

### 2026-02-22: Projection Offset Applied at Rendering Root

**By:** Ekko  
**What:** Projection offset for alignment jog is applied to center coordinates in `draw()` method, before any feature position calculations.  
**Why:** Applying transformation at the highest level ensures all rendered features (eyes, eyebrows, mouth) automatically inherit the offset uniformly. This avoids having to modify each individual drawing method and maintains consistency across all visual elements. The offset is orthogonal to expression state and animation state, persisting across all transitions and animations.

**Implementation Details:**
- State: `projection_offset_x`, `projection_offset_y` (integers, clamped ±500px)
- Rendering: `center_x = (width // 2) + projection_offset_x` in `draw()` method
- UI: Arrow keys nudge 5px, `0` key resets to (0, 0)
- Backend: Socket commands (`jog_offset`, `set_offset`, `projection_reset`) for programmatic control

---

### 2026-02-22: Head Movement Test Strategy — Projection Offset Validation

**By:** Mylo (Tester)

**What:** Created comprehensive test suite (71 tests) for 3D head movement illusion (Issue #17) using projection offset system. Tests cover state management, directional movement validation, animation orthogonality, transition smoothness, projection mapping compliance, edge cases, and performance.

**Why:** 
- **Proactive parallel development**: Tests written while Ekko implements the projection offset shifting feature, enabling immediate validation once implementation lands
- **3D illusion correctness**: Head movement creates parallax effect by shifting entire face rendering — requires pixel-level validation that features move cohesively as a unit
- **Projection mapping safety**: Offset shifts must not introduce gray pixels or break contrast ratio at extreme positions (±500px boundaries)
- **Edge case prevention**: Extreme offsets may clip features off-screen, but must not crash or corrupt rendering state
- **Performance gates**: 60fps smooth animation requires frame time <50ms even with continuous offset updates

**Test Architecture:**
1. **State Variables**: Validates jog (relative) vs set (absolute) semantics, cumulative behavior, boundary clamping (±500px), reset to origin
2. **Directional Movement**: Pixel sampling validates left/right/up/down/diagonal shifts — white features appear at new position, old position becomes black
3. **Orthogonality**: Projection offset persists across expression changes, blink/wink, gaze, eyebrow adjustments (independent state system)
4. **Smoothness**: Multiple small jogs simulate 60fps animation, rapid direction changes validate stability
5. **Projection Compliance**: Binary color validation (pure black/white), contrast ratio ≥15:1 at all offsets, all 7 expressions tested
6. **Edge Cases**: Extreme positions, corner positions, combined extreme states, rapid reset cycles, zero offset equivalence
7. **Performance**: Frame time measurement, 60fps sustained updates for 1 second

**Key patterns established:**
- **Pixel-level movement validation**: Sample before/after to verify feature displacement
- **Sparse 50px grid sampling**: Efficient projection compliance checks across entire 1920x1080 canvas
- **Cumulative jog testing**: Validates that small incremental movements accumulate correctly for smooth animation
- **Parametrized expression testing**: Single test multiplied across all 7 expressions to ensure universal offset support

**Expected implementation contract:**
- `projection_offset_x`, `projection_offset_y` state variables (integers, ±500px range)
- `jog_projection_offset(dx, dy)` — relative movement (accumulates)
- `set_projection_offset(x, y)` — absolute positioning (replaces)
- `reset_projection_offset()` — return to (0, 0)
- Offsets applied to center_x/center_y in draw() method before feature rendering

**Test file**: `test_head_movement.py` — 71 tests, 7 classes organized by concern

**Impact**: Establishes quality gates for head movement animation, ensures projection mapping safety at extreme positions, validates orthogonal state system, catches clipping/performance issues before release.

---

### 2026-02-22: Projection Offset as Global Rendering Transform

**By:** Vi (Backend Dev)

**What:** Implemented projection offset adjustment as a global transform applied to the center point in `draw()`, affecting all rendered features uniformly.

**Why:**
1. **Single source of truth:** Applying offset at center point (`center_x`, `center_y`) ensures all features (eyes, eyebrows, mouth) move together consistently
2. **Orthogonal to all other state:** Projection offset is independent of expression transitions, gaze, eyebrows, blink, wink, rolling eyes — it's purely a rendering concern
3. **Clamped to ±500px:** Prevents extreme offsets while allowing significant adjustment for physical projection alignment on foam pumpkins
4. **Dual control modes:** Both relative (`jog_offset`) and absolute (`set_offset`) commands provide flexibility for UI controls and calibration scripts

**Pattern established:** Projection offset follows same orthogonal state pattern as gaze control and eyebrow control — state persists across expression changes and is managed independently of expression state machine.

**Interface contract:** Backend provides three methods (`jog_projection`, `set_projection_offset`, `reset_projection_offset`) with clear signatures. Graphics layer (Ekko) can call these directly or via socket commands.

---

### 2026-02-25: PR Base Branch Enforcement — Always dev, Never main

**By:** Mike (via Copilot)

**What:** All feature branch PRs must target `dev` branch, not `main`. Enforce at agent spawn level by adding `--base dev` to every `gh pr create` command and adding a safety warning block to agent prompts.

**Why:** Prevent accidental main merges (happened multiple times). Agents will default to dev, with explicit warning about main-targeting branches.

---

### 2026-02-25: Feature Branch Workflow Standard (consolidated)

**By:** Mike Linnen (via Copilot)

**What:** All code changes must be made on feature branches, never directly on main/master. Always create a feature branch before starting work on any modification. Keep the repository clean — commit all outstanding changes before starting new work.

**Why:** User directive captured for team memory. Feature branches ensure clean history, enable parallel work, and allow for proper code review before merging. Repository cleanliness prevents state conflicts and enables other team members to start work confidently.

**Team standards:**
- Create feature branch for every change before writing code
- Main/master branch remains clean and ready for releases
- Commit all outstanding changes before starting new work
- No uncommitted (WIP) changes left in working directory between sessions

---

### 2026-02-24: Test Suite Reorganization Verified

**By:** Mylo

**What:** Verified all 189 tests work correctly after relocation to tests/ directory during Issue #32 repository reorganization.

**Why:** Ensure test infrastructure remains fully functional after repository restructuring. Validate that pytest discovery, imports, fixtures, and execution work correctly from new location.

**Test Results:**
- ✅ All 189 tests pass (100% success rate)
- ✅ No import errors or path issues
- ✅ pytest discovers tests from repo root with 	ests/ argument
- ✅ Execution time: 181.93 seconds (~3 minutes)

**Test Coverage Confirmed:**
- Eyebrow animation: 39 tests
- Head movement: 88 tests
- Nose movement: 45 tests
- Projection mapping: 44 tests
- Clipping/visibility: 3 tests
- Command parsing: 2 tests
- Animated movement: 1 test

**Infrastructure Validated:**
- 	ests/conftest.py provides shared fixtures correctly
- All pygame initialization working properly
- No broken imports in any test module

---


---

# Timeline Testing Strategy

**By:** Mylo (Tester)  
**Date:** 2026-02-25  
**Context:** Issue #34 — Record and playback timeline feature  
**Related Work:** Vi (WI-1, WI-2 timeline implementation)

---

## Decision

Established comprehensive test-first approach for timeline playback feature with 60+ test cases across 6 categories, covering all aspects of timeline loading, seeking, state management, timing precision, and edge cases.

## Rationale

**Proactive testing enables parallel development:**
- Vi can build Timeline and TimelinePlayback classes (WI-1, WI-2) while tests define the contract
- Tests serve as executable specification documenting expected behavior
- Reduces integration risk by catching API design issues early
- Enables immediate validation when implementation lands

**Frame-based timing precision:**
- 60 FPS = 16.67ms per frame is the timing foundation
- Tolerance of ±2ms per frame accounts for system variance
- Tests validate both incremental updates (small dt) and jump updates (large dt)
- Ensures commands execute at correct timestamps within one frame accuracy

**Edge case coverage:**
- Empty timelines, single-command timelines, zero-duration timelines
- Bounds checking (negative seeks, beyond-duration seeks)
- Rapid state changes (pause/resume cycles)
- Invalid command handling (graceful degradation)
- Auto-stop behavior at timeline end

## Test Structure

### 6 Test Classes (60+ tests):

1. **TestTimelineLoading** (9 tests) — File I/O, JSON validation, structure validation
2. **TestTimelineSeeking** (9 tests) — Seek operations, bounds clamping, state preservation
3. **TestPlaybackStateMachine** (8 tests) — STOPPED/PLAYING/PAUSED transitions
4. **TestPlaybackTiming** (8 tests) — 60 FPS frame-based execution, command ordering
5. **TestPlaybackStatus** (8 tests) — Status queries (position, duration, progress)
6. **TestEdgeCases** (10 tests) — Corner cases, error handling, boundary conditions

### Testing Patterns:

- **Fixtures**: Sample timeline data (simple, empty, single-command, complex)
- **Temporary files**: JSON files with automatic cleanup
- **Constants**: FRAME_MS = 16.67, FRAME_TOLERANCE_MS = 2.0
- **Assertions**: State enum checks, command execution tracking, timing verification

## Timing Precision Standards

```python
FRAME_MS = 16.67  # 60 FPS frame duration
FRAME_TOLERANCE_MS = 2.0  # System variance allowance

# Examples:
# - 60 frames * 16.67ms = ~1000ms (±2ms)
# - Command at t=1000ms executes when position >= 1000ms
# - Frame boundary: ±1 frame tolerance for multi-frame sequences
```

## Assumptions for Vi's Implementation

1. **Module location**: `timeline.py` or `src/timeline.py`
2. **Core classes**: `Timeline`, `TimelinePlayback`, `PlaybackState` (enum)
3. **Public API**:
   - `Timeline.load(path)` → Timeline instance
   - `Timeline.save(path)` → void
   - `TimelinePlayback(timeline)` → playback controller
   - Playback methods: `play()`, `pause()`, `stop()`, `seek(ms)`, `update(dt_ms)`
   - Status methods: `get_status()`, `get_progress()`, `is_playing()`
4. **State tracking**: `executed_commands` list for test assertions
5. **Error handling**: ValueError for invalid JSON/structure, FileNotFoundError for missing files

## Collaboration Workflow

1. Tests written proactively (complete before implementation)
2. All tests currently use `pass` placeholders (inactive)
3. Tests activate when Vi's implementation lands
4. May require minor API adjustments based on actual design
5. **No commits until implementation ready** — tests validate first, then commit together

## Success Metrics

- ✅ 60+ test cases covering all requirements from ISSUE_34_PLAN.md
- ✅ Frame-based timing precision documented and testable
- ✅ Edge cases discovered and documented in test suite
- ✅ Tests serve as executable specification for Vi
- ⏳ 80%+ code coverage target (measure after implementation)
- ⏳ All tests pass when Vi's implementation completes

---

**Status:** Tests written, awaiting Vi's Timeline implementation  
**Next Step:** Vi implements WI-1 & WI-2, then activate tests for validation
# Timeline Design & Playback Architecture (Issue #34)

**By:** Vi (Backend Dev)  
**Date:** 2026-02-14  
**Status:** Implemented (WI-1, WI-2)

---

## Decision: Frame-Based Playback with Millisecond Timestamps

**What:** Timeline playback uses frame-based execution integrated with the 60 FPS game loop, with commands timestamped in milliseconds.

**Why:**
1. **No new threads:** Integrates cleanly with existing `pygame.time.Clock` loop — avoids race conditions and state synchronization complexity
2. **Precise enough:** 60 FPS provides ~16.67ms granularity, which matches human perception for animations
3. **Simple state machine:** Playback state (STOPPED/PLAYING/PAUSED) is synchronous with rendering — no async coordination needed
4. **Testable:** Frame-based updates can be driven manually in tests without mocking threads or timers

**How it works:**
- Each frame calls `playback.update(dt_ms)` with delta time since last frame
- Playback advances `current_position_ms += dt_ms`
- Commands execute when `cmd.time_ms <= current_position_ms`
- Invalid commands stop playback immediately (fail-fast)

**Alternative considered:** Thread-based playback with `time.sleep()` between commands
- **Rejected because:** Requires thread synchronization with main loop, complicates pause/resume, harder to test

---

## Decision: JSON Timeline Format with Nested Playback Support

**What:** Timelines are stored as JSON files with versioned schema, supporting nested playback (one timeline triggers another).

**Schema:**
```json
{
  "version": "1.0",
  "duration_ms": 5000,
  "commands": [
    {"time_ms": 0, "command": "set_expression", "args": {"expression": "happy"}},
    {"time_ms": 3000, "command": "play_timeline", "args": {"filename": "other.json"}}
  ]
}
```

**Why JSON:**
1. **Human-readable:** Users can hand-edit timelines, debug command sequences
2. **Forward-compatible:** `version` field allows future schema evolution
3. **Nested playback:** Commands can reference other timeline files for composition
4. **Standard tooling:** Every language/platform can parse JSON

**Alternative considered:** CSV (flat list of timestamp,command pairs)
- **Rejected because:** Cannot represent nested arguments, no schema versioning, harder to nest timelines

---

## Decision: Flat File Naming in `~/.mr-pumpkin/recordings/`

**What:** All recordings stored in single directory with unique filenames (no subdirectories).

**Why:**
1. **Simplicity:** Easier to list, rename, delete — no directory traversal logic
2. **Filesystem enforces uniqueness:** Rename operations fail atomically if collision detected
3. **Cross-platform:** `pathlib.Path.home()` resolves `~` correctly on Windows/Linux/macOS
4. **User-accessible:** Hidden `.mr-pumpkin` directory follows Unix conventions, users can browse/backup easily

**Alternative considered:** Support subdirectories for organization
- **Rejected because:** Adds complexity for file management commands, not needed for MVP

---

## Decision: Callback Pattern for Command Execution

**What:** Playback engine accepts `set_command_callback(fn)` to decouple from PumpkinFace internals.

**Why:**
1. **Testability:** Tests can inject mock callbacks to verify command execution without running full app
2. **Separation of concerns:** Timeline module knows nothing about PumpkinFace — can be reused/tested in isolation
3. **Error handling:** Callback exceptions are caught, logged, and stop playback gracefully

**Pattern:**
```python
def execute_command(command: str, args: dict):
    # PumpkinFace implementation
    ...

playback = Playback()
playback.set_command_callback(execute_command)
playback.play("sequence.json")
```

---

## Decision: Invalid Commands Stop Playback Immediately

**What:** If a command execution raises an exception during playback, playback stops and returns error message.

**Why:**
1. **Fail-fast prevents cascading failures:** Bad command at 1s shouldn't corrupt state for commands at 2s
2. **Clear error messages:** Playback engine returns list of errors from `update()` for logging/debugging
3. **User control:** Stopped state allows user to fix timeline file and restart cleanly

**Alternative considered:** Skip invalid commands, continue playback
- **Rejected because:** Silent failures are harder to debug, may leave app in unexpected state

---

## Implications for Future Work

1. **Mylo (Testing):** Can write unit tests for timeline module without mocking pygame or PumpkinFace
2. **Ekko (Graphics):** Timeline commands can trigger any expression/animation — no graphics layer changes needed
3. **Jinx (Lead):** WI-3 (socket commands) and WI-4+ can build on this foundation without changing core design
4. **Performance:** Large timelines (10K+ commands) should benchmark well — linear scan is O(n) but frame budget is 16ms

---

## Open Questions for Future Iterations

1. **Playback speed control:** Should we support 2x, 0.5x speed? (Not in MVP)
2. **Record filtering:** Should users selectively record commands? (Not in MVP)
3. **Undo recording:** Should `record_cancel` exist to discard without saving? (Not in MVP)
4. **File size limits:** Should we cap timeline file size or command count? (Not in MVP)
# Decision: Timeline Testing Strategy & API Expectations

**Date:** 2026-02-25  
**Author:** Mylo (Tester)  
**Status:** Proposed  
**Affects:** Vi (Backend), timeline.py implementation

---

## Context

Extended test suite for Issue #34 (WI-3 through WI-6) uncovered important API design decisions and testing patterns for timeline recording and file management functionality.

---

## Testing Insights

### 1. Frame-Seeking Precision at Command Boundaries

**Issue:** When seek(1000) lands exactly on a command at t=1000, should it execute?

**Recommendation:** Use **inclusive** comparison (position >= timestamp)
- Matches intuitive playback behavior
- Consistent with "play from this point" mental model
- Test case: `test_seek_to_exact_command_boundary()` validates this

**Alternative:** Exclusive comparison (position > timestamp) would require fractional advance to trigger.

---

### 2. Recording API Design Requirements

Tests assume the following API for recording:

```python
class TimelineRecorder:
    def record_start(self) -> None
    def record_command(self, timestamp_ms: int, command: str) -> None
    def record_stop(self, filename: str | None = None, directory: str = "./recordings") -> str
    def is_recording(self) -> bool
```

**Key behaviors:**
- `record_stop(None)` auto-generates timestamp-based filename
- `record_stop()` validates at least one command recorded (raises ValueError if empty)
- Duplicate filename raises FileExistsError
- Invalid filename characters raise ValueError

---

### 3. File Management API Design Requirements

Tests assume the following API for file operations:

```python
class TimelineFileManager:
    def __init__(self, directory: str)
    def list_recordings(self) -> list[str]
    def upload_timeline(self, name: str, data: dict) -> None
    def download_timeline(self, name: str) -> dict
    def delete_timeline(self, name: str) -> None
    def rename_timeline(self, old_name: str, new_name: str) -> None
```

**Key behaviors:**
- All operations scoped to configured directory (path safety)
- upload_timeline() validates JSON structure before accepting
- Appropriate exceptions: FileNotFoundError, FileExistsError, ValueError
- list_recordings() returns filenames only (not full paths)

---

### 4. get_status() Return Structure

Tests expect this exact structure:

```python
{
    "file": str | None,           # Current timeline filename or None
    "position_ms": int,            # Current playback position
    "duration_ms": int,            # Total timeline duration
    "is_playing": bool,            # True if PLAYING state
    "state": str                   # "STOPPED" | "PLAYING" | "PAUSED"
}
```

---

### 5. Exception Hierarchy

Use Python built-in exceptions (no custom exception classes needed):
- `FileNotFoundError` — nonexistent file operations
- `FileExistsError` — duplicate filename conflicts
- `ValueError` — invalid data (JSON, filenames, empty recordings)
- `RuntimeError` — invalid state transitions (e.g., record_start() while already recording)

---

## File I/O Testing Patterns Established

1. **Use pytest's tmp_path fixture** — isolated directories per test, auto-cleanup
2. **Test actual file I/O** — prefer real files over mocks for integration confidence
3. **Round-trip validation** — write → read → assert equality
4. **Exception testing** — pytest.raises() with match="" for error message validation
5. **Explicit file creation** — Path.write_text() or json.dump() in test setup

---

## Edge Cases to Handle

1. **Concurrent recording protection:** record_start() while already recording → RuntimeError
2. **Filename sanitization:** Reject platform-specific invalid characters (Windows: `<>:"|?*\/`, Unix: `/`)
3. **Timestamp collision avoidance:** Auto-generated filenames need microsecond precision or UUID
4. **Atomic rename:** rename_timeline() should use OS-level move (not copy+delete)
5. **Empty recording validation:** record_stop() with zero commands → ValueError
6. **Rapid seek stability:** Multiple consecutive seeks maintain consistent state (last wins)

---

## Recommendation for Vi

**Before implementing:**
1. Review test_timeline.py test expectations (72 tests, all currently placeholders)
2. Confirm API structure matches test assumptions (or adjust tests)
3. Decide on seek boundary behavior (inclusive >= recommended)

**During implementation:**
1. Activate tests incrementally as classes are built
2. Run `pytest tests/test_timeline.py -v` to verify expectations

**After implementation:**
1. Mylo will validate all 72 tests pass
2. Coordinate commit with passing test suite

---

## Open Questions

1. **Directory structure:** Where should recordings default to? (`./recordings/`? `./data/timelines/`?)
2. **File format versioning:** Should FileManager validate timeline version field?
3. **Nested playback:** Tests include `test_nested_playback_reference_accessible()` — is nested playback in scope for Issue #34?

---

## Impact

- **Vi:** API expectations documented; implementation can proceed confidently
- **Mylo:** Testing patterns established for future file I/O features
- **Project:** Clear error handling and edge case expectations

---

## Status: Awaiting Vi's Implementation

Tests written and ready. No commit until implementation lands and tests pass.

# Package Release Review — jinx

**Date:** 2026-02-26  
**Reviewer:** Jinx (Lead)  
**Subject:** Review of `scripts/package_release.py` for distribution completeness  
**Requested by:** Mike Linnen

---

## Executive Summary

The `package_release.py` script is **nearly complete** but has **one critical omission**: **`timeline.py` is missing from the include list**. This module is essential for the application's recording/playback functionality and is documented in the README.

The script correctly includes all other required files for a functional distribution package. With the addition of `timeline.py`, the script will be **ready for production releases**.

---

## Checklist Assessment

### ✅ Core Functionality Files

**Included:**
- `pumpkin_face.py` — Main application with rendering and socket server
- `client_example.py` — Example client for testing commands

**Missing:**
- ❌ **`timeline.py`** — CRITICAL. This module is the recording/playback engine referenced throughout:
  - README documents recording commands (`record start`, `play <filename>`, etc.)
  - README shows command structure with `time_ms` and `command` fields
  - `pumpkin_face.py` imports and uses `Timeline`, `Playback`, `RecordingSession`, `FileManager` from this module
  - Users cannot use recording/playback features without this file

---

### ✅ Dependencies

**Included:**
- `requirements.txt` — Correctly specified with `pygame>=2.0.0,<3.0.0` (semi-pinned per team decision)

**Assessment:** Complete for production. Users can run `pip install -r requirements.txt` immediately after extraction.

---

### ✅ Installation Scripts

**Included:**
- `install.sh` — Linux/macOS/Raspberry Pi support with SDL2 system dependency detection
- `install.ps1` — Windows PowerShell support

**Assessment:** Complete. Cross-platform support as architected.

---

### ✅ Documentation

**Included:**
- `README.md` — Comprehensive (7 sections: Features, Installation, Usage, Commands, Recording Storage, Keyboard Controls, Architecture, Testing, License)
- `docs/` directory — Blog post on projection mapping architecture

**Assessment:** Complete. Users have all critical instructions for installation and usage.

---

### ✅ Configuration & Metadata

**Included:**
- `VERSION` — Source of truth for release versioning (per team decision 2026-02-20)

**Assessment:** Complete. Script correctly reads this to name the archive.

---

### ✅ License

**Included:**
- `LICENSE` — MIT license file

**Assessment:** Complete. Legal requirement satisfied.

---

## Files Included in Script

```
✓ pumpkin_face.py          [Core application]
✓ client_example.py        [Example client]
✓ requirements.txt         [Python dependencies]
✓ README.md                [Installation & usage guide]
✓ VERSION                  [Version metadata]
✓ LICENSE                  [MIT license]
✓ install.sh               [Unix-like installer]
✓ install.ps1              [Windows installer]
✓ docs/                    [Documentation directory]
```

---

## Critical Omissions

### 1. **timeline.py** — MUST BE ADDED

**Severity:** CRITICAL  
**Reason:** The application depends on this module for all recording/playback functionality.

**Evidence:**
- `pumpkin_face.py` imports: `from timeline import Timeline, Playback, RecordingSession, FileManager`
- README documents commands: `record start`, `record stop`, `play`, `seek`, `timeline_status`
- Recording format is documented with JSON structure in README
- Users expect to record and playback command sequences

**Without it:** The distributed package will fail at runtime when users try to send recording commands. The socket server will crash on `record start`.

---

## Recommendations

### 1. Add `timeline.py` to the include list (IMMEDIATE)

```python
include_files = [
    "pumpkin_face.py",
    "client_example.py",
    "timeline.py",              # ← ADD THIS LINE
    "requirements.txt",
    "README.md",
    "VERSION",
    "LICENSE",
    "install.sh",
    "install.ps1"
]
```

### 2. Consider including test suite (OPTIONAL)

**Rationale:** Per team decision (history.md, triage decisions), tests are useful for users to validate setup.
- README documents how to run tests: `pip install -r requirements-dev.txt && pytest`
- Users on Raspberry Pi could validate projection mapping and other features
- Adds confidence in deployment

**Files:** Include `tests/` directory if validation is valued; exclude if distribution size is a concern.

**Guidance:** Team should decide based on:
- Target audience (developers vs end-users)
- Deployment environment (CI/CD vs interactive displays)
- Distribution channel (GitHub Releases for automated download)

Current decision (from team history) suggests **tests are valuable for deployment validation**, so I recommend including `tests/`.

### 3. Consider excluding `.squad/` and `.github/` (Already correctly excluded)

**Current behavior:** Script correctly skips these.  
**Assessment:** ✓ Correct. End users do not need squad coordination files or CI/CD workflows.

---

## Verdict

### Current State: **NOT READY**

**Reason:** Missing `timeline.py` will cause runtime failure when users issue recording commands.

### After Recommended Changes: **READY FOR PRODUCTION**

**Required change:**
- Add `timeline.py` to `include_files` list

**Optional enhancement:**
- Add `tests/` directory to `include_dirs` list (aligns with team decision on validation)

---

## Validation Checklist for Maintainer

Before merging the fix:

- [ ] Add `timeline.py` to include_files
- [ ] Optionally add `tests/` to include_dirs
- [ ] Run the script: `python scripts/package_release.py`
- [ ] Verify archive contents: `unzip -l mr-pumpkin-v*.zip`
- [ ] Extract archive and run: `./install.sh` (on Unix) or `.\install.ps1` (on Windows)
- [ ] Verify application starts: `python pumpkin_face.py`
- [ ] Test socket commands including: `echo "record start" | nc localhost 5000`
- [ ] Confirm recording works end-to-end

---

## Summary Table

| Requirement | Status | Notes |
|---|---|---|
| Core files | ⚠️ INCOMPLETE | Missing `timeline.py` |
| Dependencies | ✅ COMPLETE | `requirements.txt` included |
| Installation | ✅ COMPLETE | Both `install.sh` and `install.ps1` |
| Documentation | ✅ COMPLETE | README + blog post in docs/ |
| Metadata | ✅ COMPLETE | VERSION file |
| License | ✅ COMPLETE | LICENSE included |
| **Overall** | **❌ NOT READY** | **Blocking issue: `timeline.py` must be added** |

---

**Recommendation:** Add `timeline.py` to the script's `include_files` list and merge. The fix is a one-line addition. This will resolve the critical blocking issue and make the package distribution-ready.

### 2026-02-26: Remove .squad/ guard workflow and gitignore restrictions
**By:** Jinx  
**Issue:** #40  
**What:** Removed all mechanisms preventing `.squad/` from being committed to `preview` and `main` branches: deleted `squad-main-guard.yml` workflow, removed `.gitignore` entries, removed validation check from `squad-preview.yml`.  
**Why:** Squad team state (decisions, histories, routing rules, agent charters) should flow through normal git workflow like any other project directory. This preserves team evolution history and shares it across branches. The original guard design kept squad coordination files off release branches, but this prevented team knowledge from being versioned and distributed with the codebase.  
**Impact:** `.squad/` is now fully git-tracked. Future merges to `preview` and `main` will include squad state files. Release artifacts may need explicit exclusion patterns if `.squad/` should not ship to end users.

# TCP Protocol Specification — Timeline Recording & Playback
## Issue #34 Timeline Feature

**Author:** Jinx (Lead)  
**Date:** 2026-02-25  
**Status:** Design proposal (pending implementation)

---

## Overview

This document specifies the TCP command protocol for timeline recording/playback functionality. The design extends the existing text-based TCP command system (port 5000) with new timeline commands while maintaining full backward compatibility with expression/animation commands.

---

## Design Principles

1. **Backward compatibility:** All existing commands (expressions, blink, gaze, etc.) continue to work unchanged
2. **Text-based simplicity:** Consistent with existing command format (space-separated text)
3. **Non-blocking execution:** Timeline playback runs in background; commands return immediately
4. **Single active timeline:** Only one recording OR one playback active at a time
5. **Graceful error handling:** Invalid commands print error to console, don't crash server
6. **Flat response format:** JSON for structured data (status, file listings), plain text for confirmation/errors

---

## Command Grammar

### Recording Commands

```
record_start
  → Begins capturing all incoming commands with timestamps
  → Response: "OK Recording started"
  → Error if recording already active: "ERROR Recording already in progress"

record_stop [filename]
  → Stops recording and saves to file
  → filename: Optional. Auto-generated if omitted (format: "recording_YYYY-MM-DD_HHMMSS.json")
  → Response: "OK Saved to {filename}"
  → Error if not recording: "ERROR No active recording"
  → Error if no commands captured: "ERROR Cannot save empty recording"
  → Error if filename exists: "ERROR File already exists: {filename}"

record_cancel
  → Cancels active recording without saving
  → Response: "OK Recording cancelled"
  → Error if not recording: "ERROR No active recording"
```

**Examples:**
```
> record_start
< OK Recording started

> happy
[command captured with timestamp]

> blink
[command captured with timestamp]

> record_stop halloween_intro
< OK Saved to halloween_intro.json

> record_start
> gaze 0 0
> record_cancel
< OK Recording cancelled
```

---

### Playback Commands

```
play <filename>
  → Loads and starts playing timeline file
  → filename: Required. Auto-append ".json" if missing
  → Response: "OK Playing {filename} ({duration_ms}ms)"
  → Error if file not found: "ERROR File not found: {filename}"
  → Error if playback active: "ERROR Playback already active: {current_file}"
  → Error if invalid JSON: "ERROR Invalid timeline file: {filename}"
  → Error during playback if command fails: stops playback, prints error

pause
  → Pauses playback at current position
  → Response: "OK Paused at {position_ms}ms"
  → Error if not playing: "ERROR No active playback"
  → Error if already paused: "ERROR Already paused"

resume
  → Resumes playback from paused position
  → Response: "OK Resumed from {position_ms}ms"
  → Error if not paused: "ERROR Playback not paused"

stop
  → Stops playback and resets to beginning
  → Response: "OK Playback stopped"
  → Error if not playing: "ERROR No active playback"

seek <milliseconds>
  → Jumps to position in timeline (works during playback or paused)
  → milliseconds: Integer timestamp (0 to duration_ms)
  → Response: "OK Seeked to {milliseconds}ms"
  → Error if no timeline loaded: "ERROR No timeline loaded"
  → Error if out of range: "ERROR Seek position out of range (0-{duration_ms}ms)"
```

**Examples:**
```
> play halloween_intro
< OK Playing halloween_intro.json (5000ms)

> pause
< OK Paused at 2341ms

> seek 1000
< OK Seeked to 1000ms

> resume
< OK Resumed from 1000ms

> stop
< OK Playback stopped
```

---

### Status Query Commands

```
timeline_status
  → Returns current playback state as JSON
  → Response format:
    {
      "state": "stopped"|"playing"|"paused",
      "filename": "halloween_intro.json"|null,
      "position_ms": 2341,
      "duration_ms": 5000,
      "is_playing": true|false,
      "recording": true|false
    }
  → Always returns 200 (never errors)

recording_status
  → Returns current recording state
  → Response format:
    {
      "is_recording": true|false,
      "command_count": 42,
      "duration_ms": 3521
    }
  → Always returns 200 (never errors)
```

**Examples:**
```
> timeline_status
< {"state": "playing", "filename": "halloween_intro.json", "position_ms": 2341, "duration_ms": 5000, "is_playing": true, "recording": false}

> recording_status
< {"is_recording": true, "command_count": 12, "duration_ms": 4521}
```

---

### File Management Commands

```
list_recordings
  → Lists all timeline files in recordings directory
  → Response format (JSON array):
    [
      {
        "filename": "halloween_intro.json",
        "size_bytes": 1234,
        "created_at": 1708897200.0,
        "duration_ms": 5000
      },
      ...
    ]
  → Returns empty array [] if no recordings

delete_recording <filename>
  → Deletes a timeline file
  → filename: Required. Auto-append ".json" if missing
  → Response: "OK Deleted {filename}"
  → Error if file not found: "ERROR File not found: {filename}"
  → Error if currently playing: "ERROR Cannot delete file currently in playback"

rename_recording <old_name> <new_name>
  → Renames a timeline file
  → old_name, new_name: Required. Auto-append ".json" if missing
  → Response: "OK Renamed {old_name} to {new_name}"
  → Error if old file not found: "ERROR File not found: {old_name}"
  → Error if new name exists: "ERROR File already exists: {new_name}"
  → Error if currently playing old file: "ERROR Cannot rename file currently in playback"
```

**Examples:**
```
> list_recordings
< [{"filename": "recording_2026-02-25_143022.json", "size_bytes": 523, "created_at": 1708897200.0, "duration_ms": 3200}]

> delete_recording old_test
< OK Deleted old_test.json

> rename_recording recording_2026-02-25_143022 halloween_intro
< OK Renamed recording_2026-02-25_143022.json to halloween_intro.json
```

---

## Integration with Existing Commands

### Recording Mode Behavior

When `record_start` is active:
- **All incoming commands are captured** (expressions, blink, gaze, eyebrow, etc.)
- Commands execute normally AND get recorded with timestamps
- Manual commands sent during recording → captured in timeline
- Example:
  ```
  > record_start
  > happy           ← Executes AND records at t=0ms
  > blink           ← Executes AND records at t=1200ms
  > gaze 45 30      ← Executes AND records at t=2500ms
  > record_stop demo
  ```

### Playback Mode Behavior

When `play <file>` is active:
- **Manual commands pause playback** (playback state → PAUSED)
- Manual command executes immediately
- Playback remains paused until explicit `resume` or `stop`
- Rationale: Operator override should take control, not compete with timeline
- Example:
  ```
  > play demo
  [playback running...]
  > happy           ← Playback auto-pauses, happy executes immediately
  > timeline_status
  < {"state": "paused", "filename": "demo.json", ...}
  > resume          ← Continue playback from paused position
  ```

**Alternative (NOT chosen):** Queue manual commands after playback ends — rejected because operator expects immediate control.

**Alternative (NOT chosen):** Ignore manual commands during playback — rejected because operator loses manual override capability.

### Timeline Commands During Recording

- `play`, `pause`, `resume`, `stop`, `seek` → **Error: "Cannot control playback while recording"**
- `list_recordings`, `delete_recording`, `rename_recording` → **Allowed** (file management is safe)
- `timeline_status` → **Allowed** (query-only)

### Timeline Commands During Playback

- `record_start` → **Error: "Cannot start recording while playback active"**
- All other commands → **Allowed** (manual override pauses playback)

---

## Error Handling

### File Errors
- **File not found during play:** Print error, don't start playback
- **Invalid JSON during play:** Print error with JSON parsing details, don't start playback
- **File exists during save:** Print error, recording data preserved (user can retry with different name)

### State Conflicts
- **Recording already active:** `record_start` rejected
- **Playback already active:** `play` rejected (must `stop` first)
- **Invalid command during playback:** Timeline stops immediately, error printed to console
  - Example: Timeline contains `gaze 500 500` (out of range) → playback stops at that timestamp

### Invalid Arguments
- **Missing required arguments:** Print usage error
- **Invalid numeric arguments:** Print parse error with expected format
- **Filename with path separators:** Reject (security — flat directory only)

---

## Response Format Reference

### Success Responses (Plain Text)
```
OK <action description>
```

### Error Responses (Plain Text)
```
ERROR <error description>
```

### Structured Data Responses (JSON)
```json
{...}
```
or
```json
[...]
```

**Note:** No prefixes like "OK" for JSON responses — client detects format by first character (`{` or `[` = JSON, else text).

---

## Backward Compatibility Guarantee

All existing commands unchanged:
- Expression commands: `neutral`, `happy`, `sad`, `angry`, `surprised`, `scared`, `sleeping`
- Animation commands: `blink`, `wink_left`, `wink_right`, `roll_clockwise`, `roll_counterclockwise`
- Gaze commands: `gaze <x> <y>`, `gaze <lx> <ly> <rx> <ry>`
- Eyebrow commands: `eyebrow_raise`, `eyebrow_lower`, `eyebrow_reset`, `eyebrow <val>`, etc.
- Head movement: `turn_left`, `turn_right`, `turn_up`, `turn_down`, `center_head`
- Nose animation: `twitch_nose`, `scrunch_nose`, `reset_nose`
- Projection offset: `projection_reset`, `jog_offset <dx> <dy>`, `set_offset <x> <y>`

**Integration strategy:** Add new command handlers in `_run_socket_server()` before final `try: Expression(data)` fallback. Timeline commands checked explicitly, existing commands hit enum parsing last.

---

## Implementation Notes for Vi

### Code Structure
1. **Add timeline objects to PumpkinFace:**
   - `self.playback = Playback()` — playback engine instance
   - `self.recording = RecordingSession()` — recording session instance
   - Set command callback: `self.playback.set_command_callback(self._execute_timeline_command)`

2. **Integrate with game loop:**
   - In `update()`: Add `self.playback.update(dt_ms)` to execute timeline commands each frame

3. **Add command handlers in `_run_socket_server()`:**
   - Parse timeline commands before expression enum fallback
   - Call `self.playback.play()`, `self.recording.start()`, etc.
   - Handle errors with try/except, print to console

4. **Manual override logic:**
   - When non-timeline command received during playback: call `self.playback.pause()`
   - Recording capture: In each command handler, if `self.recording.is_recording`: call `self.recording.record_command(cmd, args)`

5. **Command callback implementation:**
   ```python
   def _execute_timeline_command(self, command: str, args: dict):
       """Execute command from timeline playback."""
       # Map timeline command format to existing methods
       # Example: command="set_expression", args={"expression": "happy"}
       #   → self.set_expression(Expression.HAPPY)
   ```

### Delta Time Calculation
- Current `update()` doesn't track delta time
- Timeline playback needs dt in milliseconds
- Add: `self.last_update_time = time.time()` at start of `update()`
- Compute: `dt_ms = (time.time() - self.last_update_time) * 1000`
- Pass to: `self.playback.update(dt_ms)`

### JSON Response Handling
- Current socket server prints strings to console (no client response)
- For timeline commands: Send response back to client socket
- Add: `client_socket.sendall(response.encode('utf-8') + b'\n')`
- Format: JSON responses as-is, text responses with "OK" or "ERROR" prefix

---

## Open Questions / Design Decisions for Review

### 1. Response Channel
**Current behavior:** Socket server accepts commands but doesn't send responses to client (all output goes to console).

**Proposed change:** Timeline commands send responses back over socket (JSON or text).

**Question:** Should ALL commands start sending responses, or only timeline commands?
- **Option A:** Only timeline commands (status, list, etc.) → minimal change
- **Option B:** All commands send "OK" or error → consistency

**Recommendation:** Option A (timeline-only responses) — less disruption to existing client_example.py.

### 2. Manual Command During Playback
**Current design:** Manual command during playback → auto-pause playback.

**Alternative:** Manual command queued, executed after playback ends.

**Question:** Is auto-pause the right behavior?

**Recommendation:** Yes — operator expects immediate control. If they want timeline to continue, they shouldn't send manual commands.

### 3. Recording Expression vs Command Format
**Current behavior:** Expressions sent as strings (`"happy"`), parsed to enum.

**Recording format:** Should timeline store:
- **Option A:** Original command string (`"happy"`) — matches wire format
- **Option B:** Normalized command + args dict (`{"command": "set_expression", "args": {"expression": "happy"}}`) — explicit

**Current implementation:** timeline.py uses Option B (command + args dict).

**Implication:** Need mapping layer from TCP string → command dict during recording, and dict → method call during playback.

**Recommendation:** Keep Option B — more robust for complex commands like `gaze 45 30 50 35`.

### 4. Filename Restrictions
**Security consideration:** Filenames with `../` could escape recordings directory.

**Proposed validation:** Reject filenames containing `/` or `\` characters.

**Implementation:** Add check in file management commands before passing to Timeline classes.

---

## Example Session

```
# Start recording a sequence
> record_start
< OK Recording started

> neutral
[executes and records at t=0ms]

> gaze 0 0
[executes and records at t=500ms]

> happy
[executes and records at t=1200ms]

> blink
[executes and records at t=2300ms]

> record_stop greeting
< OK Saved to greeting.json

# List available recordings
> list_recordings
< [{"filename": "greeting.json", "size_bytes": 342, "created_at": 1708897200.0, "duration_ms": 2300}]

# Play it back
> play greeting
< OK Playing greeting.json (2300ms)
[timeline executes: neutral at 0ms, gaze at 500ms, happy at 1200ms, blink at 2300ms]

# Check status mid-playback
> timeline_status
< {"state": "playing", "filename": "greeting.json", "position_ms": 1450, "duration_ms": 2300, "is_playing": true, "recording": false}

# Pause playback
> pause
< OK Paused at 1523ms

# Seek to beginning
> seek 0
< OK Seeked to 0ms

# Resume from beginning
> resume
< OK Resumed from 0ms

# Manual override during playback
> sad
[playback auto-pauses, sad expression executes immediately]
< OK Paused at 1102ms (auto-paused by manual command)

# Resume playback
> resume
< OK Resumed from 1102ms

# Stop playback
> stop
< OK Playback stopped

# Rename file
> rename_recording greeting welcome_sequence
< OK Renamed greeting.json to welcome_sequence.json

# Clean up
> delete_recording welcome_sequence
< OK Deleted welcome_sequence.json
```

---

## Summary

This protocol design:
- ✅ Maintains full backward compatibility with existing commands
- ✅ Uses simple text-based command format (consistent with current system)
- ✅ Provides operator control via manual override (auto-pause during playback)
- ✅ Enables recording any sequence of existing commands
- ✅ Returns structured data (JSON) for status queries and file listings
- ✅ Handles errors gracefully without crashing socket server
- ✅ Supports non-blocking playback (runs in game loop background)
- ✅ Enforces single-file-at-a-time constraint (per issue #34 spec)

**Next step:** Vi implements integration in pumpkin_face.py using timeline.py classes.

### 2026-02-26: Issue #19 — Nose Movement & Animation (consolidated)
**By:** Jinx
**What:** Nose animation system with twitch and scrunch movements, orthogonal state management, and comprehensive test coverage. Architecture includes graphics design (white triangle on black), animation easing, expression composition, and backend socket integration.
**Why:** Nose movement adds expressivity to pumpkin face, requires careful integration with existing expression system. Multiple reviews (architecture, graphics, testing, backend, implementation) converged on shared design ensuring quality and team alignment.
**Decisions consolidated:**
- 2026-02-25: Issue #19 architecture — Nose Movement
- 2026-02-24: Issue #19 graphics design — Nose rendering & animation
- 2026-02-24: Issue #19 testing insights — Nose movement test coverage
- 2026-02-24: Issue #19 test framework — Nose movement validation
- 2026-02-24: Issue #19 backend design — Nose state & commands
- 2026-02-25: Issue #19 backend implementation — Nose Animation Backend
- 2026-02-25: Issue #19 implementation decisions — Nose Animation Backend


### 2026-02-21: Gaze Control & Rolling Eyes Integration (consolidated)
**By:** Ekko, Vi
**What:** Gaze coordinate system with centered origin (0,0), rolling eyes that track current position and return to starting angle, and seamless integration with existing expression system. Commands: gaze (2 or 4 args), eye position queries, and auto-return after gaze operations.
**Why:** Multiple independent decisions on same date (2026-02-21) covered gaze API, coordinate defaults, rolling eye behavior, and integration fixes. Consolidated to reflect unified design: eyes respond to gaze commands while maintaining orthogonal animation state.
**Decisions consolidated:**
- 2026-02-21: Rolling Eyes Enhancement — Current Position Tracking
- 2026-02-21: Rolling Eyes Return to Starting Angle
- 2026-02-21: Gaze Control Implementation
- 2026-02-21: Gaze Coordinate System and Default Position
- 2026-02-21: Gaze Control API Mismatch — Test vs Implementation
- 2026-02-21: Rolling Eyes Gaze Integration Fix
- 2026-02-21: Rolling Eyes Gaze Sequencing Fix

---

### 2025-07-14: WebSocket upload_timeline uses inline JSON format

**By:** Vi (Backend Dev)  
**Task:** Fix upload_timeline in the WebSocket handler

**What:** WebSocket clients send `upload_timeline` as a single inline message: `upload_timeline <filename> <json_string>`. The WebSocket handler (`_ws_handler` in `pumpkin_face.py`) intercepts this command **before** routing to `command_router`, parses filename and JSON content from the message, and calls `file_manager.upload_timeline(filename, json_content)` directly.

**Why:** TCP uses a multi-step handshake protocol (send filename → recv READY → send JSON → send END_UPLOAD). This stateful protocol cannot be replicated over WebSocket's single-message model. The `command_router` returns the string `"UPLOAD_MODE"` as a placeholder when it sees `upload_timeline` — this is meaningless to a WS client. The WebSocket handler therefore short-circuits `upload_timeline` and handles it inline, keeping both protocols functional with their respective designs.

**Security:** Path separators (`/`, `\`) are rejected in the filename to prevent directory traversal. Invalid JSON is caught by `file_manager.upload_timeline` and returned as an `ERROR` response.

---


---


---

### 2026-02-27: Issue triage — Round 1
**By:** Jinx
**What:** Triaged issues #43, #39, #33, #20 and set routing/priority
**Why:** Ralph activated for continuous backlog management

---

## Issue #43: Convert to websockets instead of straight sockets
- **Route to:** Vi (Backend Dev)
- **Priority:** P1 (should have)
- **Type:** Backend / Infrastructure
- **Blocker?** No — straightforward protocol upgrade
- **Dependencies:** None
- **Next step:** Vi to evaluate websocket library options (websockets, aiohttp) and propose minimal migration path. Current TCP socket server works fine; this is about enabling browser-based UIs.
- **Complexity estimate:** 6-8 hours (library integration, protocol adaptation, backward compatibility testing)
- **Notes:** Enables future web-based control panels. Consider maintaining TCP socket backward compatibility or documenting breaking change. Vi should evaluate whether to run both protocols simultaneously or phase out TCP.

---

## Issue #39: Create a mr-pumpkin skill for LLM-driven recording generation
- **Route to:** Vi (Backend Dev) + Mylo (Tester)
- **Priority:** P2 (nice to have)
- **Type:** Feature / Integration / DevOps
- **Blocker?** No — but requires architectural review first
- **Dependencies:** None, but synergizes with #44 (upload timeline) which is complete
- **Next step:** Jinx to define skill interface contract (input: natural language prompt, output: valid timeline JSON). Then Vi builds skill script that generates timeline JSON from LLM response, Mylo validates against existing timeline schema.
- **Complexity estimate:** 12-16 hours (LLM integration, prompt engineering, JSON schema generation, validation)
- **Notes:** This is a **tooling/automation feature**, not a core pumpkin_face.py feature. Deliverable is a CLI script (e.g., `scripts/generate_recording.py --prompt "happy dance"`) that writes JSON files compatible with `upload_timeline` command. Requires:
  1. LLM API integration (OpenAI/Anthropic/local model)
  2. Prompt template that teaches LLM the timeline JSON schema
  3. Validation against existing recording schema (version 1.0)
  4. Upload capability via existing socket command
- **Architectural decision needed:** Which LLM provider? Local vs. cloud? How to handle API keys? Mike's preference required.

---

## Issue #33: Automatic updates
- **Route to:** Vi (Backend Dev)
- **Priority:** P1 (should have)
- **Type:** DevOps / Infrastructure
- **Blocker?** Yes — architectural decision required on update strategy
- **Dependencies:** None
- **Next step:** Jinx to decide: (1) External script that polls GitHub API and manages process lifecycle, OR (2) Built-in update mechanism in pumpkin_face.py. Then Vi implements chosen approach.
- **Complexity estimate:** 16-20 hours (GitHub API integration, version comparison, download/extraction, process management, cross-platform compatibility, rollback strategy)
- **Notes:** This is critical for deployment stability but has architectural implications:
  - **External script approach:** Separate updater.py that runs independently (cron/Task Scheduler), polls GitHub Releases API, downloads ZIP, stops pumpkin_face.py via PID, extracts new version, restarts. Pros: clean separation, no runtime overhead. Cons: extra process to manage.
  - **Built-in approach:** pumpkin_face.py checks for updates on startup or periodic interval, downloads in background, restarts itself. Pros: single binary. Cons: complicates core application, cross-platform process replacement is tricky.
  - **Recommendation:** External script for cleaner separation of concerns. Vi to implement Python script that uses GitHub API, handles version comparison (parse VERSION file from release), manages download/extract/restart lifecycle, logs to ~/.mr-pumpkin/update.log.
  - **Platform concerns:** Windows (taskkill + Task Scheduler), Linux/macOS (kill + cron), Raspberry Pi (systemd service restart). Cross-platform process management is non-trivial.
  - **Rollback:** Backup current installation before extraction, restore on failure.

---

## Issue #20: Lip-Syncing
- **Route to:** Ekko (Graphics Dev) + Vi (Backend Dev)
- **Priority:** P2 (nice to have)
- **Type:** Feature / Graphics / Backend
- **Blocker?** Yes — major architectural review required
- **Dependencies:** None, but may require external audio analysis library (aubio, librosa, phoneme recognition)
- **Next step:** Jinx to architect lip-sync system: (1) Audio input mechanism, (2) Phoneme/viseme mapping, (3) Mouth shape vocabulary, (4) Real-time vs. pre-computed approach. Then Ekko designs mouth shapes, Vi implements audio analysis pipeline.
- **Complexity estimate:** 40-60 hours (audio analysis, phoneme detection, mouth shape design, timing synchronization, projection-safe rendering)
- **Notes:** This is a **major feature** with significant scope:
  - **Audio input:** Real-time microphone vs. pre-recorded file? Socket command to start/stop lip-sync mode?
  - **Phoneme detection:** Audio analysis to detect vowel/consonant shapes (A, E, I, O, U, M, B, F, V, etc.). Requires phoneme recognition library or pre-computed viseme timing.
  - **Mouth shapes:** Current mouth is expression-based (happy curve, sad frown, etc.). Lip-sync requires 8-12 distinct mouth shapes (visemes) for phonemes. Ekko must design projection-safe white outlines for each.
  - **Synchronization:** Frame-accurate timing between audio playback and mouth shape changes. 60fps rendering means 16ms windows.
  - **Projection constraints:** All mouth shapes must be pure white outlines on black background (no fills, no anti-aliasing).
  - **Integration:** New animation mode orthogonal to expressions (like blink/wink). Lip-sync overrides expression mouth, preserves expression eyes/eyebrows.
  - **Recording compatibility:** Should lip-sync timings be recordable in timeline JSON? Requires schema extension.
- **Recommendation:** This is a P2 feature because it's complex, requires external dependencies (audio analysis), and significantly expands the rendering pipeline. Should be tackled after P0/P1 features are stable. Consider phased approach: (1) Manual viseme control via socket commands first (no audio analysis), (2) Pre-computed viseme timing from file, (3) Real-time audio analysis last.

---

## Summary

**Routing breakdown:**
- Vi (Backend Dev): #43, #39 (with Mylo), #33, #20 (with Ekko)
- Ekko (Graphics Dev): #20 (with Vi)
- Mylo (Tester): #39 (with Vi)
- Jinx (Lead): Architectural decisions for #39, #33, #20 before team starts work

**Priority distribution:**
- P0 (blocking release): None
- P1 (should have): #43 (websockets), #33 (auto-updates)
- P2 (nice to have): #39 (LLM skill), #20 (lip-sync)

**Blockers:**
- #39: Needs LLM provider decision from Mike
- #33: Needs update strategy decision (external vs. built-in)
- #20: Needs full architectural design (audio input, phoneme mapping, mouth shape vocabulary)

**Recommended execution order:**
1. #43 (websockets) — clean backend work, enables browser UIs
2. #33 (auto-updates) — after architectural decision, critical for deployment
3. #39 (LLM skill) — after Mike clarifies LLM provider preference
4. #20 (lip-sync) — last, most complex, requires phased approach

**Next actions for Jinx:**
- Schedule architectural design session for #33 (update strategy)
- Schedule architectural design session for #20 (lip-sync system)
- Clarify with Mike: LLM provider preference for #39 (OpenAI? Anthropic? Local model?)
- Unblock Vi to start #43 immediately (no architectural decisions needed)

---

# Recording File Upload Implementation

**Date:** 2026-02-25  
**Decision Owner:** Vi (Backend Dev)  
**Issue:** #44 - Allow users to upload recording files with validation

## What

Implemented `upload_timeline` socket command that allows clients to upload JSON recording files to the server with full validation.

## Why

Users need a way to programmatically upload pre-recorded or externally-generated timeline files. The implementation leverages the existing `FileManager` validation infrastructure to ensure only valid timeline files are accepted.

## Design Decisions

### 1. Multi-line JSON Protocol (READY/END_UPLOAD Handshake)

**Decision:** Use explicit READY and END_UPLOAD markers rather than expecting JSON on a single line.

**Rationale:**
- Timeline JSON files can be multi-line for readability
- Socket protocol is line-based, but JSON may contain newlines
- Handshake approach is explicit and prevents accidental data truncation
- Easy for clients to implement: read READY, send JSON, send END_UPLOAD marker

**Pattern:**
```
Client: upload_timeline <filename>
Server: READY
Client: <json content (multiple lines)>
Client: END_UPLOAD
Server: OK Uploaded <filename>.json
```

### 2. Leverage Existing FileManager Validation

**Decision:** Use `FileManager.upload_timeline()` which already validates JSON structure.

**Rationale:**
- DRY principle - validation logic already exists and is tested
- Consistent error messages across all upload paths
- Simplifies socket handler to focus on protocol, not validation logic
- FileManager already handles file system operations and collision detection

### 3. Add FileManager to PumpkinFace Initialization

**Decision:** Create `self.file_manager = FileManager()` in `__init__`.

**Rationale:**
- Consistent with existing patterns (timeline_playback, recording_session)
- Single instance reused across all socket commands
- Centralized file management state (if needed for future features)

### 4. Include upload_timeline in Timeline Commands List

**Decision:** Add "upload_timeline" to the list of commands that don't pause playback.

**Rationale:**
- Uploading a file is a file management operation, not an expression/animation command
- User might want to prepare a recording while playback is active
- Consistent with other timeline management commands (list, rename, delete)

## Implementation Details

### Error Handling

All errors return explicit messages to help clients debug:
- Missing filename: `ERROR Missing filename`
- Path traversal attempt: `ERROR Invalid filename: path separators not allowed`
- File collision: `ERROR File already exists: <filename>`
- Invalid JSON: `ERROR Invalid timeline: <error details>`
- Connection loss: `ERROR Connection lost while reading JSON`

### Client-Side Implementation

Added `upload_timeline(filename, json_file_path)` to client_example.py:
1. Validates local file exists
2. Reads file contents
3. Connects to server
4. Sends command, waits for READY
5. Transmits JSON content
6. Sends END_UPLOAD marker
7. Displays server response

### Security Considerations

- Path separator validation prevents directory traversal (e.g., `../../etc/passwd`)
- No shell commands or file operations beyond .json reading
- FileManager ensures only valid timeline structure is saved
- File permissions handled by OS filesystem

## Testing

- All 362 existing tests pass (no regressions)
- Protocol validated with client_example.py example
- Error paths covered (invalid JSON, file exists, missing args)
- Integration with existing recording/playback/file management infrastructure verified

## Future Extensions

- Support for gzip compression (large timeline files)
- Batch upload (multiple files in one connection)
- Streaming large files (don't read entire file into memory)
- Download/export timeline with validation


### 2026-02-25: Issue #43 analysis — WebSocket upgrade proposal
**By:** Vi
**What:** Analyzed TCP socket implementation and proposed WebSocket migration strategy
**Why:** P1 feature enabling browser-based UIs

## Current State Assessment

### Socket Code Footprint
**Location:** `pumpkin_face.py` lines 1352-2035 (~680 lines)
**Core server:** Lines 1352-1357 (server setup), 1360-2031 (client handler loop), 2035 (cleanup)
**Protocol characteristics:**
- Single-threaded blocking server (`socket.socket`, `bind`, `listen(1)`)
- Runs in daemon thread (spawned at line 1224)
- Port: 5000 (localhost only)
- Connection: One client at a time (`listen(1)`)
- Protocol: Text-based, newline-delimited (`\n` terminated)
- Encoding: UTF-8

### Command Protocol Format
**Request structure:** Simple string commands, case-insensitive (`.lower()` at line 1366)
- **Simple commands:** `"blink"`, `"happy"`, `"pause"`, etc.
- **Parameterized commands:** `"gaze 45 -30"`, `"seek 1500"`, `"play recording1"`
- **Multi-line upload:** Special handshake protocol for `upload_timeline`:
  1. Client sends `"upload_timeline <filename>"`
  2. Server responds `"READY\n"`
  3. Client sends JSON content (multiple 4096-byte chunks)
  4. Client sends `"END_UPLOAD"` marker
  5. Server responds `"OK Uploaded <filename>.json\n"` or error

**Response structure:** Text messages prefixed with status codes
- **Success:** `"OK <message>\n"` (e.g., `"OK Expression changed to happy"`)
- **Error:** `"ERROR <message>\n"` (e.g., `"ERROR Unknown expression: invalid"`)
- **Data responses:** Raw JSON strings with `\n` terminator (for `recording_status`, `list_recordings`, `timeline_status`, `download_timeline`)
- **Special responses:** `"READY\n"` for upload handshake

### State Shared Between Socket Handler and Game Loop
**Orthogonal state management pattern:** Socket handler directly modifies PumpkinFace instance state variables:
- Expression state: `self.set_expression(expression)`
- Animation triggers: `self.blink()`, `self.wink_left()`, `self.roll_clockwise()`
- Gaze control: `self.set_gaze(x, y)` or `self.set_gaze_independent(x1, y1, x2, y2)`
- Eyebrow positioning: `self.raise_eyebrows()`, `self.set_eyebrow(value)`
- Projection offset: `self.jog_projection(dx, dy)`, `self.set_projection_offset(x, y)`
- Nose animation: `self._start_nose_twitch()`, `self._start_nose_scrunch()`
- Head movement: `self._move_head_to(x, y)`
- Timeline playback: `self.timeline_playback.play(filename)`, `self.timeline_playback.pause()`
- Recording session: `self.recording_session.start()`, `self.recording_session.stop(filename)`

**No mutex/lock protection:** Game loop runs in main thread at 60 FPS, socket handler runs in daemon thread. State modifications are atomic method calls on shared PumpkinFace instance. Python's GIL provides thread safety for individual assignments, but no explicit locking used.

**Threading model:**
- Main thread: pygame event loop + rendering (`pumpkin.run()` at line 2062)
- Daemon thread: TCP socket server (spawned at line 1224-1225)
- Thread lifecycle: Socket thread terminates when `self.running = False` (main thread exit)

### Command Handler Architecture
**Pattern:** Giant if-elif chain (lines 1370-2029) — no routing table
- 60+ command handlers in linear sequence
- Each handler:
  1. Parses command string (`data.split()` or `data.startswith()`)
  2. Validates parameters (try-except blocks for ValueError/IndexError)
  3. Calls PumpkinFace methods
  4. Constructs response string
  5. Sends via `client_socket.sendall((response + '\n').encode('utf-8'))`
  6. Prints to console for logging
  7. `continue` to next loop iteration

**Command categories:**
1. **Expressions** (7): neutral, happy, sad, angry, surprised, scared, sleeping
2. **Animations** (10): blink, wink_left, wink_right, roll_clockwise, roll_counterclockwise, raise_eyebrows, etc.
3. **Gaze control** (1): `gaze <x> <y>` or `gaze <x1> <y1> <x2> <y2>`
4. **Nose control** (3): twitch_nose, scrunch_nose, reset_nose
5. **Projection offset** (3): jog_offset, set_offset, projection_reset
6. **Head movement** (3): move_head, reset_head, head_status
7. **Timeline playback** (6): play, pause, resume, stop, seek, timeline_status
8. **Recording** (5): record_start, record_stop, record_cancel, recording_status, list_recordings
9. **File management** (4): delete_recording, rename_recording, upload_timeline, download_timeline

**Reusability potential:** Command parsing logic is embedded in socket handler. No command registry or abstraction layer exists.

---

## Proposed Architecture

### Recommendation: Dual-Protocol Support (TCP + WebSocket)

**Rationale:**
1. **Backward compatibility:** Existing Python/shell clients use raw TCP sockets (`client_example.py`, nc/netcat scripts)
2. **Browser enablement:** WebSocket required for browser-based control panels (JavaScript WebSocket API)
3. **Migration safety:** Run both protocols in parallel, deprecate TCP later if adoption justifies
4. **Zero breaking changes:** Existing users unaffected

### Recommended Library: `websockets` (asyncio-based)

**Why `websockets`:**
- **Minimal dependencies:** Pure Python, no C extensions (important for Raspberry Pi compatibility)
- **Async native:** Integrates cleanly with modern Python patterns
- **Production-ready:** Battle-tested, used by major projects
- **Lightweight:** ~150 KB installed size vs. FastAPI's 5+ MB
- **Protocol focus:** WebSocket-only (no HTTP bloat like aiohttp/FastAPI)

**Why NOT alternatives:**
- **FastAPI:** Overkill — adds HTTP routing, dependency injection, OpenAPI docs we don't need. Dependencies include pydantic, starlette, uvicorn (heavy install).
- **aiohttp:** Adds full HTTP client/server framework. We only need WebSocket, not web server.
- **socket + handshake:** Reinventing the wheel. RFC 6455 WebSocket handshake is complex (HTTP upgrade, SHA-1 hashing, base64 encoding).

### Architecture: Command Abstraction Layer

**New module:** `command_handler.py`
```python
class CommandRouter:
    def __init__(self, pumpkin_face):
        self.pumpkin = pumpkin_face
        self.handlers = self._register_handlers()
    
    def execute(self, command_str: str) -> str:
        """Parse and execute command, return response string."""
        # Extract existing if-elif logic from socket handler
        # Return "OK ..." or "ERROR ..." strings
        pass
    
    def _register_handlers(self) -> dict:
        """Map command prefixes to handler functions."""
        # Future: convert to routing table
        pass
```

**Benefits:**
1. **Protocol agnostic:** Both TCP and WebSocket call `router.execute(command_str)`
2. **Testable in isolation:** Unit test commands without socket/websocket setup
3. **Single source of truth:** Command parsing logic lives in one place
4. **Incremental refactoring:** Start by extracting current if-elif chain, refactor to routing table later

### Dual Server Architecture

**Pattern:** Run two servers in separate threads
```python
# In PumpkinFace.__init__()
self.command_router = CommandRouter(self)

# In run() method
tcp_thread = threading.Thread(target=self._run_tcp_server, daemon=True)
ws_thread = threading.Thread(target=self._run_ws_server, daemon=True)
tcp_thread.start()
ws_thread.start()
```

**TCP Server (unchanged):**
```python
def _run_tcp_server(self):
    # Existing implementation (lines 1352-2035)
    # Replace command handling with: response = self.command_router.execute(data)
    pass
```

**WebSocket Server (new):**
```python
import asyncio
import websockets

def _run_ws_server(self):
    """Run WebSocket server in asyncio event loop (separate thread)."""
    asyncio.run(self._ws_server_main())

async def _ws_server_main(self):
    async with websockets.serve(self._ws_handler, 'localhost', 5001):
        await asyncio.Future()  # Run forever

async def _ws_handler(self, websocket):
    """Handle WebSocket client connection."""
    async for message in websocket:
        response = self.command_router.execute(message)
        await websocket.send(response)
```

**Port allocation:**
- TCP: Port 5000 (unchanged, backward compatible)
- WebSocket: Port 5001 (new, browser clients)
- Both on localhost only (security isolation)

### Multi-line Protocol Adaptation (upload_timeline)

**Challenge:** Current `upload_timeline` uses stateful handshake (READY/END_UPLOAD markers)
**WebSocket solution:** Send JSON object in single message
```javascript
// Browser client:
ws.send(JSON.stringify({
    command: "upload_timeline",
    filename: "test.json",
    content: {...}  // Timeline JSON as nested object
}));
```

**Backend handling:**
```python
# In command_router.execute():
if command_str.startswith('{'):
    # WebSocket JSON format
    data = json.loads(command_str)
    if data['command'] == 'upload_timeline':
        return self._handle_upload_json(data['filename'], data['content'])
else:
    # TCP text format (existing)
    if command_str.startswith('upload_timeline'):
        return self._handle_upload_tcp(client_socket, filename)
```

**Backward compatibility preserved:** TCP clients continue using READY/END_UPLOAD, WebSocket clients use single JSON message.

---

## Implementation Plan

### Milestone 1: Command Router Extraction (5-7 hours)
**Goal:** Decouple command parsing from TCP socket handler

**Tasks:**
1. Create `command_handler.py` module
2. Define `CommandRouter` class with `execute(command_str) -> response_str` method
3. Extract existing if-elif chain from `_run_socket_server()` (lines 1370-2029)
4. Update TCP handler to call `self.command_router.execute(data)`
5. Verify all 362 existing tests still pass (no behavioral changes)

**Files modified:** `pumpkin_face.py`, `command_handler.py` (new)
**Lines of code:** ~700 lines moved to new module, ~20 lines TCP handler cleanup
**Blocking dependencies:** None
**Risk:** Medium — large code movement, potential for copy-paste errors

### Milestone 2: WebSocket Server Setup (3-4 hours)
**Goal:** Add WebSocket server running in parallel with TCP

**Tasks:**
1. Add `websockets>=11.0,<12.0` to `requirements.txt`
2. Implement `_run_ws_server()` and `_ws_handler()` methods in `pumpkin_face.py`
3. Spawn WebSocket thread in `run()` method (line ~1226)
4. Test with browser JavaScript client (simple HTML test page)
5. Verify both protocols work simultaneously

**Files modified:** `pumpkin_face.py`, `requirements.txt`
**Lines of code:** ~30 lines WebSocket server, ~10 lines thread spawn
**Blocking dependencies:** Milestone 1 (command router must exist)
**Risk:** Low — additive change, no modifications to existing TCP path

### Milestone 3: JSON Protocol Adapter (2-3 hours)
**Goal:** Support JSON-formatted commands for WebSocket clients

**Tasks:**
1. Add JSON detection to `CommandRouter.execute()` (check if `command_str.startswith('{')`)
2. Implement JSON parsing: `{"command": "blink"}` → `"blink"`
3. Implement JSON response formatting: `"OK Blink"` → `{"status": "ok", "message": "Blink"}`
4. Add optional parameter: `execute(command_str, format='text')` where format can be 'text' or 'json'
5. Update WebSocket handler to use `format='json'`

**Files modified:** `command_handler.py`, `pumpkin_face.py` (WebSocket handler)
**Lines of code:** ~50 lines JSON parsing/formatting
**Blocking dependencies:** Milestone 2
**Risk:** Low — TCP clients unaffected (still use text format)

### Milestone 4: Multi-line Upload Refactor (4-5 hours)
**Goal:** Support `upload_timeline` in both TCP (stateful) and WebSocket (stateless) modes

**Tasks:**
1. Extract TCP upload logic to `_handle_upload_tcp(client_socket, filename)` method
2. Implement WebSocket upload handler: `_handle_upload_json(filename, content_dict)`
3. Update `CommandRouter` to delegate based on protocol detection
4. Test both paths: TCP with READY/END_UPLOAD, WebSocket with single JSON message
5. Update `client_example.py` with WebSocket upload example

**Files modified:** `command_handler.py`, `pumpkin_face.py`, `client_example.py`
**Lines of code:** ~60 lines refactoring, ~40 lines WebSocket upload
**Blocking dependencies:** Milestone 3
**Risk:** Medium — stateful TCP protocol requires careful handling in abstraction layer

### Milestone 5: Documentation & Testing (3-4 hours)
**Goal:** Document WebSocket API and add integration tests

**Tasks:**
1. Update `README.md` with WebSocket section:
   - Connection endpoint: `ws://localhost:5001`
   - JSON command format examples
   - Browser JavaScript client example
   - Migration guide for TCP users
2. Create `docs/websocket-api.md` with full protocol spec
3. Create `tests/test_websocket_integration.py` — integration tests using `websockets` library
4. Add browser client example: `client_example.html` (simple test page)
5. Test on Raspberry Pi (verify `websockets` library installs cleanly)

**Files modified:** `README.md`, `docs/websocket-api.md` (new), `tests/test_websocket_integration.py` (new), `client_example.html` (new)
**Lines of code:** ~200 lines documentation, ~150 lines tests, ~80 lines HTML example
**Blocking dependencies:** Milestone 4
**Risk:** Low — documentation and testing only

### Total Effort Estimate
**Development time:** 17-23 hours (3-4 days of focused work)
**Testing time:** 4-6 hours (included in milestone 5)
**Total:** ~21-29 hours

---

## Risk Assessment

### Technical Risks

**1. Threading + asyncio interaction**
- **Risk:** WebSocket server runs asyncio event loop in separate thread. Calling synchronous PumpkinFace methods from async handler may cause issues.
- **Likelihood:** Medium
- **Impact:** Medium (WebSocket functionality degraded)
- **Mitigation:** 
  - Use `asyncio.to_thread(self.command_router.execute, command)` for CPU-bound operations
  - Test with high message volume (100+ commands/sec) to detect race conditions
  - Monitor for deadlocks during integration testing

**2. GIL contention with game loop**
- **Risk:** Two socket servers + 60 FPS game loop all competing for GIL. Rendering frame rate may drop.
- **Likelihood:** Low (command volume typically <10/sec)
- **Impact:** High (visible animation stutter)
- **Mitigation:**
  - Profile with `cProfile` under load (10 concurrent WebSocket clients)
  - If contention detected, batch commands and process in game loop instead of handler threads
  - Worst case: make command handling async-only (requires refactoring game loop to asyncio — major change)

**3. WebSocket library compatibility on Raspberry Pi**
- **Risk:** `websockets` library may not install cleanly on older Pi models (32-bit ARM).
- **Likelihood:** Low (pure Python library)
- **Impact:** Medium (blocks Pi users from upgrading)
- **Mitigation:**
  - Test install on Pi 3B, 4, and 5 before release
  - Add fallback to `requirements.txt`: if websockets fails, only TCP available (graceful degradation)
  - Document manual install steps for edge cases

**4. Command router abstraction leaks protocol details**
- **Risk:** TCP's stateful `upload_timeline` handshake hard to abstract cleanly. Router may need socket handle passed in.
- **Likelihood:** High (already identified in multi-line upload analysis)
- **Impact:** Low (localized to one command)
- **Mitigation:**
  - Create separate handler methods: `_handle_upload_tcp(socket)` vs `_handle_upload_json(data)`
  - Router delegates based on protocol detection, not one-size-fits-all abstraction
  - Accept that some commands have protocol-specific implementations

### Compatibility Risks

**5. Breaking existing TCP clients**
- **Risk:** Refactoring TCP handler introduces subtle behavior changes (response timing, error messages).
- **Likelihood:** Low (careful extraction + comprehensive tests)
- **Impact:** High (user scripts break)
- **Mitigation:**
  - Run full test suite after each milestone (362 tests)
  - Test `client_example.py` and shell scripts (`echo "happy" | nc localhost 5000`) manually
  - Add regression test: capture all TCP responses before/after refactor, diff outputs

**6. Port conflicts**
- **Risk:** Port 5001 already in use on user's machine (another service).
- **Likelihood:** Low (5001 not commonly used)
- **Impact:** Medium (WebSocket server fails to start)
- **Mitigation:**
  - Make WebSocket port configurable via environment variable: `WS_PORT=5002 python pumpkin_face.py`
  - Graceful degradation: if WebSocket bind fails, log warning and continue with TCP-only mode
  - Document port requirements in README

**7. Browser CORS restrictions**
- **Risk:** Browsers block WebSocket connections from `file://` HTML pages (CORS policy).
- **Likelihood:** High (standard browser security)
- **Impact:** Low (users need simple HTTP server)
- **Mitigation:**
  - Document workaround in README: `python -m http.server 8000` to serve HTML client
  - Or: add minimal HTTP server for serving `client_example.html` (adds complexity)

### Testing Risks

**8. Parallel protocol testing complexity**
- **Risk:** Tests need to verify both TCP and WebSocket paths for every command (doubles test surface area).
- **Likelihood:** High
- **Impact:** Medium (longer test development time)
- **Mitigation:**
  - Parameterize tests: `@pytest.mark.parametrize('protocol', ['tcp', 'websocket'])`
  - Reuse command router tests (protocol-agnostic layer)
  - Focus integration tests on critical commands (expressions, recording, playback)

**9. Async test infrastructure**
- **Risk:** Existing tests are synchronous (pytest). WebSocket tests require `pytest-asyncio` plugin.
- **Likelihood:** High
- **Impact:** Low (add dependency)
- **Mitigation:**
  - Add `pytest-asyncio>=0.21.0` to `requirements-dev.txt`
  - Isolate async tests in separate file (`test_websocket_integration.py`)
  - Use `@pytest.mark.asyncio` decorator for WebSocket-specific tests

---

## Collaboration Points

### Ekko (Graphics Dev) Collaboration
**Scope:** None required
**Rationale:** WebSocket implementation is pure backend infrastructure. Graphics layer untouched.

### Mylo (Tester) Collaboration
**Required:**
1. **Test strategy review** (Milestone 5) — Validate integration test coverage
2. **Browser client testing** (Milestone 5) — Manual testing of `client_example.html` on different browsers
3. **Raspberry Pi verification** (Milestone 5) — Test WebSocket install and functionality on Pi hardware

**Artifacts to provide:**
- Test plan for dual-protocol scenarios (concurrent TCP + WebSocket clients)
- Browser compatibility matrix (Chrome, Firefox, Safari, Edge)
- Pi installation report (Pi 3, Pi 4, Pi 5)

### Jinx (Team Lead) Collaboration
**Decision points:**
1. **Port allocation approval** — Confirm port 5001 for WebSocket (or suggest alternative)
2. **Dependency approval** — Add `websockets` library to production dependencies (affects release package size)
3. **Migration timeline** — When (if ever) to deprecate TCP protocol
4. **API format decision** — JSON-only for WebSocket, or support both text and JSON?

---

## Open Questions

1. **WebSocket subprotocol:** Should we define custom subprotocol (`ws://localhost:5001/?protocol=pumpkin-v1`) for versioning?
2. **Authentication:** Both TCP and WebSocket are localhost-only. Future: add token-based auth for remote access?
3. **Binary protocol:** Timeline JSON can be large (100s of commands). Use binary encoding (MessagePack) for efficiency?
4. **Broadcast mode:** Should WebSocket support pub/sub (multiple clients receive state updates)? Or stay request-response like TCP?
5. **Error handling:** Should WebSocket send structured errors (`{"status": "error", "code": 404, "message": "..."}`) or match TCP text format?

---

## Recommendation Summary

**Proceed with dual-protocol implementation using `websockets` library.**

**Key advantages:**
- Zero breaking changes (TCP remains fully functional)
- Browser compatibility unlocked (JavaScript WebSocket API)
- Clean abstraction layer (command router testable in isolation)
- Minimal dependencies (websockets is lightweight, pure Python)
- Incremental rollout (5 milestones, each independently testable)

**Next steps:**
1. **Approval from Jinx** on port 5001 and websockets dependency
2. **Start Milestone 1** (command router extraction) — foundation for both protocols
3. **Consult Mylo** on test strategy before Milestone 5

**Timeline:** 3-4 weeks for full implementation (working in parallel with other P1 issues)


---

# Decision: Add socket.shutdown(SHUT_WR) in send_command() to fix recv deadlock

**Date:** 2025-07-21  
**Author:** Vi (Backend Dev)  
**File changed:** `client_example.py`

## Problem

`send_command()` always called `client.recv()` after sending, but certain commands (`blink`, `roll_clockwise`, `roll_counterclockwise`, `gaze`, and all eyebrow/head/nose commands) return `""` from `execute()` in `command_handler.py`. The server only sends a response `if response:`, so for these commands it sends nothing and loops back to its own `recv()`.

Result: client blocks on `recv()`, server blocks on `recv()` — **deadlock**. The server can no longer accept new connections, breaking all subsequent commands including expression changes.

## Decision

Add `client.shutdown(socket.SHUT_WR)` immediately after `client.send(command.encode('utf-8'))` in `send_command()`.

\\\python
client.send(command.encode('utf-8'))
client.shutdown(socket.SHUT_WR)  # Signal EOF so server breaks its recv loop
\\\

## Why This Works

`SHUT_WR` sends a TCP FIN, signaling EOF to the server. The server's `recv()` returns `b""` after it finishes processing, which breaks its inner `while` loop and causes it to close the socket. This unblocks the client's `recv()` in all cases:

- **Commands with a response:** server sends response → server loops → server gets EOF → closes socket → client recv() gets data then empty
- **Commands without a response:** server processes → sends nothing → server loops → server gets EOF → closes socket → client recv() gets empty → prints "Sent: {command}"

## Scope

- **Changed:** `send_command()` in `client_example.py` — one line added
- **Not changed:** `upload_timeline()` — multi-step protocol requires keeping the connection open across multiple sends/recvs
- **Not changed:** Server code (`pumpkin_face.py`, `command_handler.py`)

## Alternatives Considered

- **Timeout on recv():** Fragile, adds latency, masks the real issue
- **Sending a sentinel/ack from server for all commands:** Would require server changes and change the protocol contract
- **Separate connection per command (already the case):** The pattern is correct; only the EOF signal was missing
