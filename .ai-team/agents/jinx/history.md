# History — Jinx

### Project Learnings (from import)

**Project:** Animated 2D Graphics Pumpkin Face (Python)  
**Owner:** Mike Linnen  
**Stack:** Python, 2D graphics, animation  
**Key domains:** Graphics/animation rendering, command parsing & state management, expression logic  
**Team composition:** Jinx (Lead), Ekko (Graphics), Vi (Backend), Mylo (Tester), Scribe, Ralph  

---

## Learnings

*Patterns, conventions, and decisions discovered during work.*

### .ai-team/ Branch Tracking Policy (2026-02-20)
- **Root cause**: `.ai-team/` and `.ai-team-templates/` were tracked on `dev` but had been manually removed from `preview` via `git rm` in commit `2cb5057`. The `.gitignore` on `preview` (and `main`) did NOT list these directories, meaning any future dev→preview merge would re-introduce them into tracking.
- **Fix applied**: Added `.ai-team/` and `.ai-team-templates/` to `.gitignore` on both `preview` and `main`. On `main` this was already done; on `preview` it was missing and added.
- **Git strategy for future-proofing**: `.gitignore` alone does NOT prevent re-tracking if a merge commit brings tracked files in from another branch. The authoritative prevention is: (1) `.gitignore` entries on preview/main, (2) manual `git rm -r --cached .ai-team/ .ai-team-templates/` after any dev→preview merge, and (3) the CI validation check in `squad-preview.yml` acts as the safety net to catch any slip.
- **Decision filed**: `decisions/inbox/jinx-ai-team-tracking-policy.md`

### Projection Mapping Architecture
- **Pure contrast design principle**: Projection mapping on 3D surfaces demands binary color schemes (black/white) rather than gradients or intermediate tones. Falloff at oblique angles eliminates gray values entirely.
- **Projection-first, not projection-optional**: Build the core rendering around projection constraints rather than adding a feature flag. Single pipeline reduces bugs and makes all future features projection-ready by design.
- **15:1 contrast as minimum threshold**: Our 21:1 ratio (RGB 0,0,0 to 255,255,255) provides 40% safety margin for real-world conditions (stage lighting, curved geometry, angle loss).

### Testing Patterns
- **Specificity beats coverage**: Tests that check "pixel at (x,y) equals (255,255,255)" catch subtle color drift that "colors look right" misses.
- **Proactive test-driven architecture**: Mylo's 6-class, 50+ test suite defined the contract before Ekko's implementation. This enabled parallel work and confidence in deployment.
- **Edge cases first**: Resolution independence, rapid transitions, and boundary conditions caught in development, not in the field.

### Team Workflow
- **Constraint-based design unlocks expressiveness**: By treating projection colors as architectural constraints, Ekko had clear boundaries for all expression designs (six states across multiple resolutions).
- **Architectural ownership by Lead**: Project lead (Jinx) establishes rendering pipeline constraints; domain specialists (Ekko, Mylo) execute within those constraints at high velocity.

### CI/CD Workflow Migration (Python)
- **Workflows were Node.js scaffolded**: All three GitHub Actions workflows (`squad-ci.yml`, `squad-preview.yml`, `squad-release.yml`) used `actions/setup-node`, `node --test`, and read version from `package.json`. None of these apply to a Python project.
- **VERSION file as single source of truth**: Chose a flat `VERSION` file (content: `0.1.0`) over embedding version in `setup.py`, `pyproject.toml`, or elsewhere — simpler to read in shell scripts (`cat VERSION`) and consistent across all three workflows.
- **pytest is already in requirements.txt**: No need to install pytest separately or fall back to `python test_projection_mapping.py`. `pip install -r requirements.txt` handles it, then `python -m pytest` picks up all tests automatically.
- **Minimal surgical changes**: Preserved all release logic (tag creation, GitHub Release, `.ai-team/` file check) — only replaced the Node.js tooling surface.

### File References
- **pumpkin_face.py**: Core rendering with projection-safe colors (BACKGROUND_COLOR, FEATURE_COLOR) baked into base class
- **test_projection_mapping.py**: 6 test classes validating color purity, contrast, expressions, and edge cases
- **blog-post-projection-mapping.md**: Narrative explanation of projection mapping architecture for team + developer audience

### Issue Triage Session (2026-02-20)

**Codebase findings:**
- **Current expression system:** 6 expressions (neutral, happy, sad, angry, surprised, scared) via enum
- **Transition architecture:** Linear interpolation with `transition_progress` (0.0 → 1.0) and configurable `transition_speed`
- **Socket server:** Port 5000, accepts expression names as strings, converts to enum via `Expression(data)`
- **Keyboard shortcuts:** Keys 1-6 map to expressions, ESC exits
- **Cross-platform design:** Pure Python + pygame, no OS-specific code, works on Windows/Linux/macOS/Raspberry Pi
- **Dependencies:** pygame (rendering), pytest (testing) — both cross-platform
- **Release infrastructure:** GitHub Actions workflow already creates releases from `VERSION` file

**Triage decisions:**
- **Issue #4 (Sleeping expression):** Graphics work (closed eyes) → Ekko; Backend (add enum + command) → Vi; Testing → Mylo. Low complexity, 1-2 hours.
- **Issue #5 (Blink animation):** Animation architecture (temporary state change with slower timing) → Ekko; Testing → Mylo. Medium complexity, 3-4 hours. Requires new animation pattern (blink is not an expression, it's a temporary detour that returns to original state).

**Release package architectural decisions:**
- **Distribution model:** ZIP archive with install scripts (not pip package) — this is a standalone application, not a library
- **Platform support:** Cross-platform by default, Raspberry Pi as first-class target (requires SDL2 system dependencies on Linux)
- **Dependency pinning:** Semi-pinned (major version constraints) — `pygame>=2.0.0,<3.0.0` allows security patches, blocks breaking changes
- **Exclusions:** `.ai-team/`, `.github/`, `.git/`, `__pycache__/`, `.copilot/` — end users don't need squad coordination files or CI/CD workflows
- **Inclusions:** Core scripts (pumpkin_face.py, client_example.py), README, requirements.txt, VERSION, test suite (useful for users to validate setup)
- **Automation strategy:** Modify `squad-release.yml` to create ZIP archive and attach to GitHub Release as asset

**Key architectural insight for blink animation:**
- Current transition system is expression-to-expression (stateful)
- Blink is expression-to-closed-to-same-expression (temporary detour)
- Solution: Add `is_blinking` flag + separate `blink_progress` counter, orthogonal to expression transitions
- Socket command `"blink"` triggers animation method, not enum value change
