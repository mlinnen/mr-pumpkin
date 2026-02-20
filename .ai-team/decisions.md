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
