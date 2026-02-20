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
