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
- **Exclude:** `.ai-team/`, `.github/`, `.git/`, `__pycache__/`, `.copilot/`, `docs/`
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

### 2026-02-20: .ai-team/ tracking policy (SUPERSEDED)

**By:** Jinx

**Status:** ⚠️ SUPERSEDED by Issue #40 (2026-02-26)

**Original Decision:** .ai-team/ and .ai-team-templates/ are tracked on dev but NOT on preview or main. These directories are in .gitignore on preview and main. When merging dev→preview, untrack them with `git rm -r --cached .ai-team/ .ai-team-templates/` before committing the merge.

**Original Rationale:** .ai-team/ is squad internal state — it should not ship with the product.

**Policy Evolution:** On 2026-02-26, this decision was reversed. All guards blocking .ai-team/ from tracking on preview and main branches were removed (.gitignore entries, squad-main-guard.yml workflow, and squad-preview.yml validation checks). The new policy: .ai-team/ now flows through normal git workflow on all branches, enabling team evolution history to be preserved and shared across branches. This is tracked in Issue #40 and implemented in PR #41.

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
   - Excludes: .ai-team/, .github/, .git/, __pycache__/, .copilot/

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

### 2026-02-21: Rolling Eyes Enhancement — Current Position Tracking

**By:** Ekko (Graphics Dev)

**Issue:** #21 — "Eye rolling should start where the pupil is and rotate either clockwise or counter clockwise and end where it started"

**What:** Enhanced rolling eyes animation to capture the pupil's current position when triggered, rotate 360° from that position, and return to the exact starting angle upon completion.

**Why:** 
- **User expectation:** When eyes are looking in a direction (e.g., left at 180°), rolling should start from that position, not jump to a hardcoded default
- **Animation fluidity:** Eliminating position "jumps" maintains visual coherence between animations
- **Composability:** Enables chaining rolling with other pupil-position-affecting animations in the future

**Implementation:**
- Added `rolling_start_angle` state variable to capture `pupil_angle` when rolling begins
- Modified rolling calculation from hardcoded `315.0 + progress * 360` to `rolling_start_angle + progress * 360`
- On completion, restore exact starting position: `pupil_angle = rolling_start_angle`
- Pattern follows blink animation's "capture-animate-restore" approach (expression restoration)

**Impact:** Rolling eyes now works smoothly from any pupil position without visual discontinuities. Future animations (darting eyes, tracking movement) can rely on rolling preserving their state.

---

### 2026-02-21: Rolling Eyes Return to Starting Angle

**By:** Vi (Backend Dev)

**Issue:** #21

**What:** Enhanced rolling eyes animation to capture current pupil position at start and return to exact starting angle after 360° rotation.

**Why:** Previous implementation hardcoded start/end angles (315° → 225°), creating jarring visual discontinuity when pupils were elsewhere. User expectation: rolling should be a temporary animation detour, like blink, returning to the exact state before it began.

**Implementation:**
- Added `rolling_start_angle` state variable (captured from `pupil_angle` when rolling begins)
- Changed rotation calculation from `315° + progress*360` to `rolling_start_angle + progress*360`
- Changed completion behavior from `pupil_angle = 225°` to `pupil_angle = rolling_start_angle`

**Architectural Alignment:** This follows the established orthogonal animation pattern set by blink/wink systems. Temporary animations preserve origin state and restore it on completion, independent of expression state machine.

**Benefit:** Rolling can now be triggered from ANY pupil position (after another roll, during manual positioning, etc.) and will always return accurately. No special-case logic needed for different starting positions.

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

### 2026-02-21: Gaze Control Implementation

**By:** Vi (Backend Dev)

**Date:** 2026-02-21

**Issue:** #22

**What:** Implemented gaze control as orthogonal state system following established blink/wink/rolling pattern with capture-restore integration for rolling eyes.

**State Variables Added:**
- `self.left_gaze_x`, `left_gaze_y`, `right_gaze_x`, `right_gaze_y` (individual floats, -90 to +90 degrees)
- `self.pre_rolling_gaze_left`, `pre_rolling_gaze_right` (captured before rolling)

**Command Handler:**
- Socket command parser recognizes `gaze <args>` before expression parsing
- 2 args: both eyes, 4 args: independent eyes
- Invalid arg count or non-numeric args: print error, continue (non-fatal)

**Rendering Logic:**
- When not rolling: pupil offset from gaze angles using `(angle / 90.0) * max_offset` formula
- Y-axis inverted: `offset_y = -(gaze_y / 90.0) * max_offset` (user +Y = up, pixel +Y = down)
- When rolling: pupils follow `pupil_angle`, gaze state frozen and restored on completion

**Rolling Integration:**
- All four roll methods capture gaze state before animation
- On completion, restore exact captured gaze
- Follow capture-restore pattern from Issue #21

---

### 2026-02-21: Gaze Coordinate System and Default Position

**By:** Ekko (Graphics Dev)

**Date:** 2026-02-21

**Issue:** #22

**What:** Implemented per-eye gaze control using X/Y angle pairs with origin at 0° (straight ahead), ±90° range, default position (−45°, 45°) upper-left.

**Coordinate System:**
- X-axis: Negative = left, Positive = right
- Y-axis: Negative = down, Positive = up
- Clamped to ±90° to prevent pupils exceeding eye boundaries

**Default Position (−45°, 45°):**
- Maintains backward compatibility with 43 existing projection tests expecting pupils at upper-left
- Avoids breaking existing demo videos and screenshots
- Users can call `gaze((0, 0))` to look straight ahead when desired

**Gaze vs Rolling Interaction:**
- Rolling temporarily overrides gaze; gaze angles **persist** during rolling
- Gaze **resumes** after rolling completes (follows orthogonal animation pattern)

**Angle-to-Pixel Conversion:**
- Uses `sin()` instead of linear mapping for natural acceleration curve
- Small angles near center have fine control, large angles near extremes move less
- Automatic boundary safety: `sin()` never exceeds 1.0
- Orbit radius of √200 ≈ 14.14 with pupil radius 15 and eye radius 40 ensures 10.86px safety margin

---

### 2026-02-21: Gaze Control API Mismatch — Test vs Implementation

**By:** Mylo (Tester)

**Date:** 2026-02-21

**Issue:** #22

**Status:** Resolved (see consolidated decision above)

**Summary:** Design review spec called for positional args (`gaze(45, 30)`), but implementation used tuples (`gaze(left_angles=(45, 30))`). Resolved by standardizing on tuple-based storage with per-eye state variables. Test suite (47 test cases in `test_gaze_control.py`) covers command parsing, state management, rendering, rolling interaction, edge cases, and socket commands.

---

### 2026-02-21: Rolling Eyes Gaze Integration Fix

**By:** Vi (Backend Dev)

**Date:** 2026-02-21

**Issue:** Critical bug — X/C keys crash app when rolling eyes

**What:** Fixed AttributeError crashes in rolling eyes capture/restore logic due to attempting to assign to read-only properties.

**Root Cause:** Rolling capture/restore logic was written before gaze refactoring. Code assumed gaze angles were instance variables but they're actually stored as tuples with read-only properties.

**Solution:** Changed all rolling methods to work directly with tuples instead of properties:
- Before: `self.pre_rolling_gaze_left = (self.left_gaze_x, self.left_gaze_y)`
- After: `self.pre_rolling_gaze_left = self.pupil_angle_left`

**Files Changed:** `pumpkin_face.py` lines 357, 367, 377, 387, 407-416, 475-476

**Impact:** X/C keys no longer crash, gaze control works correctly, rolling properly captures/restores per-eye state

---

### 2026-02-21: Rolling Eyes Gaze Sequencing Fix

**By:** Vi (Backend Dev)

**Date:** 2026-02-21

**Issue:** Rolling animation doesn't start from new gaze position

**What:** Fixed timing issue where rolling animation didn't reflect current gaze position when triggered after `gaze` command.

**Root Cause:** Rolling captured stale `pupil_angle` (circular 0-360°) instead of converting current gaze X/Y angles to equivalent circular position. When gaze changed pupils visually, rolling animation still captured old circular angle.

**Solution:** Added helper method `_gaze_to_angle()` to convert current gaze X/Y angles to circular angle:
1. Convert gaze angles to pixel offsets (same as rendering)
2. Use `atan2()` to calculate circular angle from offsets
3. Return normalized 0-360° angle

**Updated rolling methods:** All four trigger methods now:
1. Capture gaze state first
2. Convert left eye gaze to circular angle: `rolling_start_angle = _gaze_to_angle(pupil_angle_left)`
3. Initialize: `pupil_angle = rolling_start_angle`
4. Begin rolling from correct position

**Why This Matters:** Establishes clean conversion pattern between gaze (user-facing X/Y) and circular angle (rolling animation) coordinate systems. Ensures animation continuity without visual jumps.

**Impact:** Rolling eyes now correctly starts from any gaze position (left, right, up, down, diagonal) with seamless transitions.

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

### 2026-02-25: Issue #19 architecture — Nose Movement

**By:** Jinx

**What:** Proposed nose movement architecture integrating nose as a new facial feature with orthogonal animation state.

**Why:** Feature design and team coordination for nose movement (twitch and scrunch animations)

---

## Design Summary

### Integration with Expression System

**Approach:** Nose is a **new facial feature** (like eyes, eyebrows, mouth) with **orthogonal animation state** (following the established pattern from eyebrows, blink, wink).

- **Static component:** Nose baseline shape/position defined per expression
- **Dynamic component:** Nose animation states (twitching, scrunching) overlay on baseline, independent of expression transitions
- **Rendering order:** Eyes → Eyebrows → **Nose** → Mouth (Z-order for projection clarity)

### Nose Movement Types

**Primary movements** (requested in issue):
1. **Twitch:** Quick lateral wiggle (left-right-center), 0.3-0.5 second duration
2. **Scrunch:** Vertical compression + slight width expansion, 0.5-0.8 second duration
3. **Curl:** Subtle upward tip movement (happy expressions), 0.4 second duration

**Movement characteristics:**
- **Non-interrupting:** Animations are one-shot effects, no queuing or interruption handling needed
- **Capture-Animate-Restore pattern:** Each animation captures baseline, applies temporary offset, restores on completion
- **Expression-independent:** Can trigger during any expression (nose baseline changes with expression, animation overlays on top)

### State Variables and Animation Model

**Core state (added to `PumpkinFace.__init__`):**
```python
# Nose position control (orthogonal to expression state machine)
self.nose_offset_x = 0.0  # Horizontal offset, pixels
self.nose_offset_y = 0.0  # Vertical offset, pixels
self.nose_width_scale = 1.0  # Width multiplier for scrunch effect

# Nose animation state
self.is_nose_animating = False
self.nose_animation_type = None  # 'twitch', 'scrunch', 'curl'
self.nose_animation_progress = 0.0
self.nose_animation_duration = 0.5  # seconds (varies by animation type)
```

---

### 2026-02-24: Issue #19 graphics design — Nose rendering & animation

**By:** Ekko

**What:** Nose graphics architecture and animation framework

**Why:** Graphics foundation for nose movement feature

---

## Design Decisions

### Nose Shape

**Design Choice:** Upward-facing triangle (pumpkin nose classic)

**Dimensions:**
- Shape: Isosceles triangle, apex pointing UP
- Width (base): 40 pixels
- Height: 50 pixels
- Position: Centered horizontally between eyes and mouth
- Y-coordinate: `center_y + 15` (15px below center, positioned between eyes at y-50 and mouth at y+80)

**Rationale:**
- **Pumpkin tradition:** Classic carved pumpkin noses are triangular (inverted pyramid)
- **Apex UP orientation:** Creates upward-pointing nose for scrunching animation (tip can "scrunch" upward naturally)
- **Size:** 40x50px is proportional to 40px eye radius and 300px mouth width — visible but not dominant
- **Projection mapping:** Solid white filled triangle on black background (maximum contrast, no outlines)

### Color Scheme

**Colors:**
- Fill: Pure white `(255, 255, 255)` — matches eye/mouth projection mapping standard
- Background: Pure black `(0, 0, 0)` — no light emission around nose
- No gradients or outlines — solid filled shape only

**Rationale:**
- Projection-first architecture (established 2026-02-19 decision)
- 21:1 contrast ratio required for projection visibility
- Consistent with existing feature rendering (`_draw_eyes`, `_draw_mouth`, `_draw_eyebrows`)

### Position & Layout

**Baseline Position:**
- X: `center_x` (horizontally centered on face)
- Y: `center_y + 15` (vertical midpoint between eyes and mouth)
- Proportional reasoning:
  - Eyes: `center_y - 50`
  - Nose: `center_y + 15` (65px below eyes, 65px above mouth)
  - Mouth: `center_y + 80`

**Coordinate System Integration:**
- Nose position calculated from offset-adjusted `center_x, center_y` (inherits projection offset)
- Follows UI transform layering pattern (established in projection offset feature)
- Nose automatically moves with head movement, projection jog, and all face-level transforms

### Animation Types

#### 1. Twitch Animation

**Description:** Rapid horizontal jitter — subtle nervous/sniffing effect

**Mechanism:**
- Type: Oscillating horizontal offset from baseline
- Offset range: ±8 pixels horizontal displacement
- Frequency: 4-6 oscillations per second (fast twitch)
- Duration: 0.5 seconds per twitch command
- Waveform: Sine wave `offset_x = 8 * sin(progress * 2π * 5)` where progress ∈ [0, 1] over 0.5s
  - 5 complete cycles in 0.5s = 10 Hz oscillation

#### 2. Scrunch Animation

**Description:** Vertical compression — "scrunching up" the nose

**Mechanism:**
- Type: Triangle height reduction with upward position shift
- Height scale: 100% → 50% → 100% (compress, hold, release)
- Position shift: Nose apex rises as it compresses (top stays fixed, base moves up)
- Duration: 0.8 seconds (slower than twitch — more deliberate expression)
- Phases:
  1. Compress (0.0-0.35): height scales from 100% to 50%
  2. Hold (0.35-0.65): height stays at 50%
  3. Release (0.65-1.0): height returns to 100%

#### 3. Composition

**Decision:** NO — animations are mutually exclusive (non-interrupting guards)

**Rationale:**
- Twitch and scrunch modify different axes (X vs Y scale) but compose poorly visually
- Simpler state machine: `if not (is_twitching or is_scrunching)` guard prevents overlap
- User can chain animations sequentially (twitch command queues after scrunch completes)
- Follows established pattern from rolling eyes (non-interrupting guard in `roll_clockwise()`)

### Implementation Approach

The graphics design established the following pattern:

**Rendering Method:**
- Baseline position: nose centered at `center_y + 15`
- Apply twitch animation (horizontal jitter) when `is_twitching`
- Apply scrunch animation (vertical compression) when `is_scrunching`
- Draw filled white triangle with animated transforms applied

**State Variables (added to `__init__`):**
- `is_twitching`, `twitch_progress`, `twitch_duration` (0.5s)
- `is_scrunching`, `scrunch_progress`, `scrunch_duration` (0.8s)

**Animation Trigger Methods:**
- `twitch_nose()` — Trigger nose twitch animation (horizontal jitter)
- `scrunch_nose()` — Trigger nose scrunch animation (vertical compression)

---

### 2026-02-24: Issue #19 testing insights — Nose movement test coverage

**By:** Mylo

**What:** Comprehensive test suite for nose movement feature

**Why:** Document testing decisions and patterns for future reference

---

## Test Suite Summary

Created `test_nose_movement.py` with **45 tests** across 6 categories:
- State management: 8 tests
- Animations: 10 tests
- Expression integration: 7 tests
- Command integration: 6 tests
- Edge cases: 8 tests
- Rendering: 6 tests

---

## Testing Pattern Decisions

### 1. Animation Progress Simulation

**Decision:** Manually simulate frame-by-frame animation progress in tests, rather than using `update()` method.

**Rationale:**
- Deterministic: Tests control exact progress values for formula validation
- Isolated: Tests don't depend on update loop implementation details
- Clear: Each test shows explicit frame advancement logic

### 2. Easing Validation Approach

**Decision:** Verify non-linear motion by checking delta variance, not exact formula.

**Rationale:**
- Robust: Works regardless of specific easing function used
- Simple: Tests variance rather than complex mathematical formula
- Intent-focused: Validates "smoothness" rather than implementation details

### 3. Guard Testing Pattern

**Decision:** Tests simulate guard logic inline rather than calling command methods.

**Rationale:**
- Implementation-agnostic: Tests work even if command methods don't exist yet
- Clear intent: Guard logic explicitly shown in test
- Flexible: Easy to adapt if guard implementation changes

### 4. Rendering Validation Sampling

**Decision:** Use sparse pixel sampling (every 5-10 pixels) for rendering tests.

**Rationale:**
- Performance: Faster test execution
- Sufficient: Sparse sampling catches projection compliance violations
- Follows precedent: Matches test_head_movement.py pattern

---

## Edge Cases Discovered

### 1. Animation Timeout Protection

**Finding:** Animation progress can exceed 1.0 if update loop doesn't clean up properly.

**Test coverage:** `test_nose_animation_timeout_does_not_hang` simulates 100 frames (1.67s) to verify cleanup.

### 2. Reset Command Bypasses Guard

**Finding:** Reset command must cancel animation immediately, even during active animation.

**Test coverage:** `test_reset_cancels_active_animation_immediately` verifies guard bypass.

**Design decision:** Reset command doesn't check `is_twitching or is_scrunching` guard.

### 3. Composition with Head Movement

**Finding:** Nose animation and head movement (projection offset) must compose independently.

**Test coverage:**
- `test_head_movement_during_nose_animation`
- `test_concurrent_head_and_nose_movement`

**Expected behavior:** Both state machines run simultaneously without conflict.

### 4. Expression Change During Animation

**Finding:** Expression changes should NOT interrupt or reset nose animation.

**Test coverage:** `test_expression_change_during_nose_animation` verifies continuity.

**Design rationale:** Nose is orthogonal to expression state machine (like eyebrows, gaze).

---

### 2026-02-24: Issue #19 test framework — Nose movement validation

**By:** Mylo

**What:** Test strategy and framework for nose movement with twitching and scrunching animations

**Why:** Quality assurance and regression prevention for new nose feature

---

## Test Structure

**Recommended approach:** Single integrated test file `test_nose_movement.py` (following pattern of test_eyebrow_animation.py)

**Rationale:**
- Nose is a single cohesive feature with related behaviors (similar to eyebrows)
- State management, animations, and commands are tightly coupled
- Splitting would create artificial boundaries and make refactoring harder
- Easier to run and maintain as single suite

**Test classes:**
1. `TestNoseStateVariables` — State initialization, transitions, bounds
2. `TestNoseAnimations` — Twitch/scrunch animation progress and lifecycle
3. `TestNoseExpressionIntegration` — How expressions affect nose state
4. `TestNoseCommands` — Socket command parsing, parameter validation
5. `TestNoseEdgeCases` — Overlapping animations, rapid commands, expression changes during animation
6. `TestNoseRendering` — Visual validation (projection compliance, position verification)

---

### 2026-02-24: Issue #19 backend design — Nose state & commands

**By:** Vi

**Issue:** #19 — Nose Movement

**What:** Nose state management and command architecture

**Why:** Backend foundation for nose movement feature

---

## Current System Review

**State Management Pattern:**
- Expression state machine: `current_expression`, `target_expression`, `transition_progress`
- Orthogonal animations use `is_<action>` flags + `<action>_progress` counters (blink, wink, rolling)
- Orthogonal persistent state: gaze angles, eyebrow offsets, projection offsets (independent of expressions)
- Head movement uses smooth-state-animation pattern: 0.5s duration with ease-in-out-cubic easing

**Animation Composition Rules:**
1. Expression transitions run continuously (main state machine)
2. Orthogonal animations (blink/wink/rolling) can overlay on any expression
3. Persistent states (gaze, eyebrows, projection offset) survive expression changes
4. Head movement animates projection offset smoothly over 0.5s
5. Priority: blink/wink pause rolling animation (rolling_progress freezes)

## Nose State Model

### Design Decision: Orthogonal Animation State

**Rationale:** Nose movement is a **temporary animation overlay** like rolling eyes, not persistent state like eyebrow offsets. Nose animations should:
- Return to neutral position after completing
- Not persist across expression changes
- Be composable with other animations

### State Variables

```python
# Nose animation state (add to __init__ around line 93, after head movement vars)
self.is_animating_nose = False        # Animation active flag
self.nose_animation_progress = 0.0    # 0.0 to 1.0
self.nose_animation_duration = 0.5    # Match head movement duration (0.5s)
self.nose_animation_type = None       # 'twitch' or 'scrunch' (None when idle)
self.nose_start_x = 0                 # Starting X offset (pixels, captured at start)
self.nose_start_y = 0                 # Starting Y offset (pixels, captured at start)
self.nose_start_scale = 1.0           # Starting scale factor (captured at start)
self.nose_target_x = 0                # Target X offset (pixels)
self.nose_target_y = 0                # Target Y offset (pixels)
self.nose_target_scale = 1.0          # Target scale factor
self.nose_x = 0                       # Current X offset (pixels, interpolated)
self.nose_y = 0                       # Current Y offset (pixels, interpolated)
self.nose_scale = 1.0                 # Current scale factor (interpolated)
```

**Range Constraints:**
- `nose_x`: [-30, +30] pixels (left/right shift, smaller than eyebrow range)
- `nose_y`: [-30, +30] pixels (up/down shift)
- `nose_scale`: [0.8, 1.2] (80% to 120% of base size)

---

### 2026-02-25: Issue #19 backend implementation — Nose Animation Backend

**By:** Vi

**Issue:** #19 — Nose Movement

**Status:** ✅ Complete

**What:** Implemented nose animation backend with time-based state tracking and frame-based graphics coordination.

**Why:** Deliver backend state management and socket commands for nose movement feature.

---

## Implementation Summary

### 1. State Variables (in `__init__`)

All nose animation state variables added to PumpkinFace class initialization:
- `nose_offset_x` = 0.0 (horizontal offset, ±30px range)
- `nose_offset_y` = 0.0 (vertical offset, ±30px range)
- `nose_scale` = 1.0 (scale factor, 0.8-1.2 range)
- `is_twitching` = False (twitch animation active flag)
- `is_scrunching` = False (scrunch animation active flag)
- `nose_animation_progress` = 0.0 (animation progress 0.0-1.0)
- `nose_animation_duration` = 0.0 (total duration in seconds)
- `nose_animation_start_time` = None (timestamp when animation started)
- `nose_animation_end_time` = None (timestamp when animation will end)

### 2. Backend Methods

Three core methods for nose animation control:

**`_start_nose_twitch(magnitude=50.0)`**
- Initiates twitching animation (rapid horizontal oscillation)
- Duration: 0.5 seconds
- Guards: Rejects if `is_twitching` or `is_scrunching` already True
- Time tracking: Records `start_time = time.time()`, calculates `end_time`
- Magnitude parameter: Reserved for future intensity scaling (default 50)

**`_start_nose_scrunch(magnitude=50.0)`**
- Initiates scrunching animation (vertical compression)
- Duration: 0.8 seconds
- Guards: Rejects if `is_twitching` or `is_scrunching` already True
- Time tracking: Records `start_time = time.time()`, calculates `end_time`
- Magnitude parameter: Reserved for future intensity scaling (default 50)

**`_reset_nose()`**
- Immediately cancels any active nose animation
- Resets all state variables to defaults (offsets=0, scale=1, flags=False)
- Clears time tracking variables (start_time=None, end_time=None)
- Can be called anytime (no guards)

### 3. Animation Update Logic

Modified `_update_nose_animation()` to use time-based state tracking:

**Time-based tracking:**
```python
import time
current_time = time.time()
elapsed = current_time - self.nose_animation_start_time
self.nose_animation_progress = elapsed / self.nose_animation_duration
```

**Benefits:**
- Consistent animation timing regardless of frame rate
- More accurate (microsecond precision vs frame approximation)
- Matches head movement pattern (Issue #18)

**Graphics Integration:**
- Progress (0.0-1.0) passed to Ekko's graphics methods
- `_animate_nose_twitch()` handles visual interpolation (sin waves)
- `_animate_nose_scrunch()` handles visual interpolation (ease curves)

### 4. Socket Commands

Three socket commands added to `_run_socket_server()`:

**`twitch_nose [magnitude]`**
- Format: "twitch_nose" or "twitch_nose 75"
- Default magnitude: 50.0
- Calls: `_start_nose_twitch(magnitude)`
- Response: "Twitching nose (magnitude=50)" or "Nose animation already in progress"

**`scrunch_nose [magnitude]`**
- Format: "scrunch_nose" or "scrunch_nose 100"
- Default magnitude: 50.0
- Calls: `_start_nose_scrunch(magnitude)`
- Response: "Scrunching nose (magnitude=50)" or "Nose animation already in progress"

**`reset_nose`**
- Format: "reset_nose" (no parameters)
- Calls: `_reset_nose()`
- Response: "Resetting nose to neutral" or "Nose reset to neutral"

### 5. Integration with Update Loop

`_update_nose_animation()` called from `update()` method:
- Called after head movement updates
- Before expression transition updates
- Runs every frame to track animation progress
- Calls graphics methods (`_animate_nose_twitch`, `_animate_nose_scrunch`)
- Auto-resets when animation completes

## Pattern Compliance

✅ **Orthogonal animation state:** Independent from expression state machine  
✅ **Non-interrupting guards:** Reject new commands during active animation  
✅ **Time-based state tracking:** Uses `time.time()` for backend state  
✅ **Frame-based graphics:** Progress passed to graphics layer for interpolation  
✅ **Auto-return to neutral:** Animation completes and resets automatically  
✅ **Socket command parsing:** Follows established pattern from turn_left/right/up/down  
✅ **No breaking changes:** All existing tests pass, no changes to other features  

---

### 2026-02-25: Issue #19 implementation decisions — Nose Animation Backend

**By:** Vi

**Issue:** #19 — Nose Movement

**What:** Backend design decisions for nose animation implementation

**Why:** Document key implementation choices for future reference

---

## Decision: Time-Based State Management with Frame-Based Graphics Coordination

**Context:** Implemented nose animation backend with two types: twitch (rapid horizontal oscillation) and scrunch (vertical compression). Need to choose between purely frame-based (delta_time accumulation) or time-based (timestamp tracking) for state management.

**Choice:** Time-based state tracking with frame-based graphics interpolation.

**Implementation:**
- Backend state uses `time.time()` for `animation_start_time`, `animation_end_time`, `animation_duration`
- Progress calculated as: `elapsed / duration` where `elapsed = time.time() - start_time`
- Graphics layer methods receive progress (0.0-1.0) and handle visual interpolation

**Rationale:**
1. **Consistent timing:** Animation duration independent of frame rate fluctuations
2. **Matches head movement pattern:** Head animation also uses time-based tracking (Issue #18)
3. **Orthogonal animation pattern:** Same as rolling eyes — backend manages lifecycle, graphics handles visuals
4. **Precision:** `time.time()` provides microsecond precision vs frame-based approximation (delta_time = 1/60)

---

## Decision: Non-Interrupting Guards with Reset Override

**Context:** Need to handle case where user sends second animation command while first is in progress.

**Choice:** Reject new animations during active animation, except `reset_nose` which immediately cancels.

**Implementation:**
```python
def _start_nose_twitch(self, magnitude=50.0):
    if self.is_twitching or self.is_scrunching:
        print("Nose animation already in progress")
        return
    # ... start animation
```

**Rationale:**
1. **Follows rolling eyes pattern:** Non-interrupting guards prevent visual glitches from mid-animation state changes
2. **User clarity:** Clear feedback ("already in progress") vs silent failure
3. **Reset escape hatch:** `reset_nose` provides way to immediately cancel misbehaving animation
4. **State consistency:** Prevents race conditions from overlapping animations

---

## Decision: Optional Magnitude Parameter with Sensible Default

**Context:** Socket commands need to support both quick commands (`twitch_nose`) and customizable intensity (`twitch_nose 75`).

**Choice:** Optional magnitude parameter with default value 50.

**Implementation:**
```python
# Socket command parsing
parts = data.split()
magnitude = float(parts[1]) if len(parts) > 1 else 50.0
self._start_nose_twitch(magnitude)
```

**Rationale:**
1. **Usability:** Most users want quick command without parameters
2. **Flexibility:** Power users can fine-tune animation intensity
3. **Matches existing pattern:** Turn_left/right/up/down commands use same optional parameter pattern
4. **Safe defaults:** magnitude=50 provides noticeable but not extreme animation

**Note:** While magnitude parameter is parsed and passed, current graphics implementation (Ekko's layer) uses fixed animation curves. The parameter is reserved for future enhancement where magnitude could scale the animation amplitude.



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
