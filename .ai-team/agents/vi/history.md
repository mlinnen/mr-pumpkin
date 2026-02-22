# History — Vi

### Project Learnings (from import)

**Project:** Animated 2D Graphics Pumpkin Face (Python)  
**Owner:** Mike Linnen  
**Stack:** Python, 2D graphics, animation  
**Key domains:** Graphics/animation rendering, command parsing & state management, expression logic  
**Team composition:** Jinx (Lead), Ekko (Graphics), Vi (Backend), Mylo (Tester), Scribe, Ralph  

---

## Learnings

*Patterns, conventions, and insights about state machines, commands, and backend architecture.*

### Release Package Architecture (Issue #3)

**What:** Created cross-platform release distribution system using ZIP archives with shell-based install scripts.

**Key files:**
- `scripts/package_release.py` — Python-based ZIP builder (uses zipfile module, reads VERSION file)
- `install.sh` — Bash script for Linux/macOS/Raspberry Pi (detects OS, installs SDL2 on Debian/Ubuntu, runs pip)
- `install.ps1` — PowerShell script for Windows (runs pip with error handling)
- `LICENSE` — MIT license (copyright Mike Linnen, 2026)
- `.github/workflows/squad-release.yml` — Automated release workflow (builds ZIP, attaches to GitHub Release)

**Design patterns:**
1. **Simple version management:** Single `VERSION` file at repo root (no package.json, no git tags for versioning)
2. **ZIP over pip:** Distribution via ZIP archive instead of PyPI package (simpler for end users, no packaging complexity)
3. **Shell script install:** Idiomatic OS-specific scripts (bash for Unix-like, PowerShell for Windows) handle dependencies
4. **Raspberry Pi SDL2 detection:** install.sh detects Pi via `/proc/device-tree/model` and installs SDL2 system libraries (required for pygame on Pi 3/4/5)
5. **Global pip installs:** No virtual environments (per owner request, simplifies Pi deployment)
6. **Dependency pinning:** Use range constraints (`pygame>=2.0.0,<3.0.0`) to allow patch updates while preventing breaking changes

**Architecture decision:** Exclude `.ai-team/`, `.github/`, `.git/`, `__pycache__/`, `.copilot/` from release package. Include `docs/` folder (owner override of earlier decision).

**CI/CD pattern:** GitHub Actions workflow runs `python scripts/package_release.py` after tests pass, then attaches ZIP to release via `gh release create ... {zipfile}`.

**Why shell scripts matter:** Raspberry Pi requires SDL2 system libraries before pygame will install. The install.sh script handles this automatically via apt-get on Debian/Ubuntu, making it "unzip and run" simple for Pi users.

### Rolling Eyes State Machine (Issue #21)

**What:** Enhanced rolling eyes animation to start from current pupil position and return to exact starting angle after 360° rotation.

**Problem:** Previous implementation always started from hardcoded 315° angle and ended at hardcoded 225°, regardless of where pupils were when rolling started.

**Solution Pattern:** Added `rolling_start_angle` state variable that captures `pupil_angle` when rolling begins. Animation logic calculates position as: `(rolling_start_angle + progress * 360 * direction) % 360`. Upon completion (`progress >= 1.0`), restores `pupil_angle = rolling_start_angle`.

**Key State Variables:**
- `rolling_start_angle` — Captured when `roll_clockwise()` or `roll_counterclockwise()` called
- `rolling_progress` — Linear 0.0 to 1.0 over `rolling_duration` (1 second)
- `rolling_direction` — String 'clockwise' or 'counterclockwise' (determines multiplier: +1 or -1)

**Architectural Consistency:** Follows same orthogonal animation pattern as blink (`is_blinking`, `blink_progress`) and wink (`is_winking`, `wink_progress`). Rolling state is independent of expression transitions and pauses during blink/wink (preserved from prior implementation).

**Non-Interrupting Behavior:** Rolling cannot be interrupted by second roll command. All four trigger methods (`roll_clockwise()`, `roll_counterclockwise()`, `roll_eyes_clockwise()`, `roll_eyes_counterclockwise()`) check `if not self.is_rolling` guard.

**Return Guarantee:** Animation ALWAYS returns to exact starting angle using stored `rolling_start_angle`, not a hardcoded default. This means rolling from 90° returns to 90°, from 225° returns to 225°, etc.

**Socket Commands:** Existing "roll_clockwise" and "roll_counterclockwise" socket commands work unchanged — server calls appropriate method which now captures starting angle.
