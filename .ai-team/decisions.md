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

### 2026-02-20: .ai-team/ tracking policy

**By:** Jinx

**What:** .ai-team/ and .ai-team-templates/ are tracked on dev but NOT on preview or main. These directories are in .gitignore on preview and main. When merging dev→preview, untrack them with `git rm -r --cached .ai-team/ .ai-team-templates/` before committing the merge.

**Why:** .ai-team/ is squad internal state — it should not ship with the product.

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
