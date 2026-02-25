# History — Vi

### Project Learnings (from import)

**Project:** Animated 2D Graphics Pumpkin Face (Python)  
**Owner:** Mike Linnen  
**Stack:** Python, 2D graphics, animation  
**Key domains:** Graphics/animation rendering, command parsing & state management, expression logic  
**Team composition:** Jinx (Lead), Ekko (Graphics), Vi (Backend), Mylo (Tester), Scribe, Ralph  

---

## Learnings

📌 Team update (2026-02-25): Feature branch workflow standard and repository cleanliness directive — decided by Mike Linnen  
📌 Team update (2026-02-25): Test suite reorganization verified (189 tests passing) — decided by Mylo

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

### Eyebrow Animation Backend (Issue #16)

**What:** Implemented backend state management for eyebrow animation control.

**Key patterns used:**
1. **Orthogonal state system:** Eyebrow offsets are independent of expression state machine (follow same pattern as gaze control)
2. **Sign convention:** Negative values = raise (up), positive = lower (down) — matches screen Y coordinates
3. **Range clamping:** All values clamped to [-50, +50] pixels to prevent extreme positioning
4. **Incremental + absolute control:** Both step-based methods (raise/lower by 10px) and absolute positioning (set_eyebrow)
5. **Socket command parsing:** String-based commands with error handling follow established pattern from gaze/blink commands

**File changes:**
- `pumpkin_face.py`:
  - Added state variables: `eyebrow_left_offset`, `eyebrow_right_offset` (lines 60-63)
  - Added 8 helper methods: `set_eyebrow`, `raise_eyebrows`, `lower_eyebrows`, `raise_eyebrow_left`, `lower_eyebrow_left`, `raise_eyebrow_right`, `lower_eyebrow_right`, `reset_eyebrows` (lines 311-351)
  - Added keyboard shortcuts: U/J for both, [ and ] with optional Shift modifier for individual control (lines 668-683)
  - Added 10 socket commands: `eyebrow_raise`, `eyebrow_lower`, `eyebrow_raise_left`, `eyebrow_lower_left`, `eyebrow_raise_right`, `eyebrow_lower_right`, `eyebrow_reset`, `eyebrow <val>`, `eyebrow_left <val>`, `eyebrow_right <val>` (lines 750-815)

**Verified orthogonality:** `set_expression()` does NOT modify eyebrow state — eyebrow positions persist across expression changes.

**All 43 existing tests pass:** No breaking changes to existing functionality.

### Projection Offset Backend (Issue #18)

**What:** Implemented command handler for projection offset adjustment (jog/nudge functionality).

**Key patterns used:**
1. **Orthogonal state system:** Projection offset is independent of expression state machine, gaze, eyebrows, blink, wink, etc.
2. **Boundary clamping:** All values clamped to [-500, +500] pixels to prevent extreme positioning while allowing significant adjustment
3. **Dual control modes:** Both relative (`jog_projection(dx, dy)`) and absolute (`set_projection_offset(x, y)`) positioning
4. **Integer precision:** Pixel offsets use integers (no sub-pixel precision needed for projection alignment)
5. **Socket command parsing:** String-based commands with error handling follow established pattern from gaze/blink/eyebrow commands

**File changes:**
- `pumpkin_face.py`:
  - Added state variables: `projection_offset_x`, `projection_offset_y` (lines 79-82)
  - Applied offset to center coordinates in `draw()` method (lines 112-114)
  - Added 3 command methods: `jog_projection`, `set_projection_offset`, `reset_projection_offset` (lines 459-487)
  - Added keyboard shortcuts: arrow keys for 5px nudge, 0 for reset (lines 820-830)
  - Added 3 socket commands: `jog_offset <dx> <dy>`, `set_offset <x> <y>`, `projection_reset` (lines 962-986)
- `test_projection_offset.py`: Test script for command validation

**Verified orthogonality:** Projection offset persists across expression changes, blinks, winks, gaze changes, and eyebrow adjustments. It's a global rendering transform applied at the top level of `draw()`.

**Design rationale:**
- **±500px range:** Allows for significant realignment without causing features to disappear off-screen on standard displays
- **Applied to center point:** Single offset affects all features uniformly (eyes, eyebrows, mouth move together)
- **No negative coordinate prevention:** Clamping at ±500 is sufficient; features can safely move partially off-screen for edge cases
- **Clean interface:** Simple method signatures that Ekko's UI controls can easily call from graphics layer

### Nose Animation Backend (Issue #19)

**What:** Implemented backend state management for nose animation control (twitch, scrunch, reset).

**Key patterns used:**
1. **Orthogonal animation state:** Nose animation is independent of expression state machine (follows same pattern as rolling eyes)
2. **Time-based state tracking:** Uses `time.time()` for backend state management (animation_start_time, animation_end_time, animation_duration)
3. **Frame-based graphics coordination:** `_update_nose_animation()` called from `update()` loop calculates progress and calls Ekko's graphics methods
4. **Non-interrupting guards:** Cannot start new animation while one is in progress (checks `is_twitching` or `is_scrunching`)
5. **Auto-return to neutral:** Animation automatically resets when progress >= 1.0
6. **Socket command parsing:** String-based commands with optional magnitude parameter

**File changes:**
- `pumpkin_face.py`:
  - Added state variables: `nose_offset_x`, `nose_offset_y`, `nose_scale`, `is_twitching`, `is_scrunching`, `nose_animation_progress`, `nose_animation_start_time`, `nose_animation_end_time`, `nose_animation_duration` (lines 93-102)
  - Added backend methods: `_start_nose_twitch(magnitude=50)`, `_start_nose_scrunch(magnitude=50)`, `_reset_nose()` (lines 600-648)
  - Updated `_update_nose_animation()`: Changed from frame-based delta_time to time-based tracking using `time.time()` (lines 846-870)
  - Added 3 socket commands: `twitch_nose [magnitude]`, `scrunch_nose [magnitude]`, `reset_nose` (lines ~1318-1344)
- `test_nose_commands.py`: Test script for command validation and non-interrupting behavior

**Socket command parsing pattern:**
- Command format: `"command_name"` or `"command_name parameter"`
- Parse: `data.split()` to separate command from arguments
- Validate: Try-except blocks catch ValueError/IndexError for malformed commands
- Default values: Use `if len(parts) > 1 else default_value` pattern for optional parameters
- Example: `magnitude = float(parts[1]) if len(parts) > 1 else 50.0`

**State lifecycle pattern:**
1. **Initialization:** All state variables set to defaults in `__init__` (zero offsets, neutral scale, flags False)
2. **Start trigger:** Socket command calls `_start_nose_twitch()` or `_start_nose_scrunch()`
3. **Guard check:** Method checks `if is_twitching or is_scrunching` and rejects if already animating
4. **Capture state:** Records `animation_start_time = time.time()`, calculates `animation_end_time`, sets duration
5. **Progress tracking:** `_update_nose_animation()` calculates `progress = elapsed / duration` each frame
6. **Graphics update:** Calls Ekko's `_animate_nose_twitch()` or `_animate_nose_scrunch()` with current progress
7. **Completion:** When `progress >= 1.0`, calls `_start_nose_reset()` to return to neutral
8. **Reset:** Clears all flags, resets offsets/scale, nullifies time tracking variables

**Non-interrupting guard implementation:**
- Check at start of `_start_nose_twitch()` and `_start_nose_scrunch()`: `if self.is_twitching or self.is_scrunching: return`
- Print message: `"Nose animation already in progress"` for debugging
- No state changes if guard rejects
- Exception: `reset_nose` command bypasses guard and immediately cancels any active animation

**Coordination pattern with graphics layer (Ekko):**
- Backend (Vi) manages: State flags (`is_twitching`, `is_scrunching`), time tracking, progress calculation
- Graphics (Ekko) manages: Visual interpolation (`nose_offset_x`, `nose_scale`) via `_animate_nose_twitch()` and `_animate_nose_scrunch()`
- Interface: Backend calls Ekko's animation methods each frame with updated `nose_animation_progress` (0.0 to 1.0)
- Separation: Backend never directly modifies visual properties (offset_x, scale); only Ekko's methods do
- Pattern matches rolling eyes: Backend tracks angle/duration/progress, graphics handles visual pupil positioning

**Time-based vs frame-based:**
- **Time-based (state):** `time.time()` used for start/end timestamps, `elapsed = current_time - start_time`
- **Frame-based (graphics):** Progress 0.0-1.0 passed to Ekko's methods, which use sin/ease curves for interpolation
- **Why both:** Time-based ensures consistent animation duration regardless of frame rate; frame-based allows smooth visual effects
- **Implementation:** `_update_nose_animation()` converts time to progress, then calls frame-based graphics methods

### Test Organization (Issue #32)

**What:** Reorganized test files into proper Python package structure for cleaner distribution and development workflows.

**Key changes:**
- **Test directory structure:** Created `tests/` directory with `__init__.py` and `conftest.py`
- **File relocation:** Moved all 11 `test_*.py` files from repo root to `tests/` subdirectory
- **Requirements split:** Separated production (`requirements.txt`) from development dependencies (`requirements-dev.txt`)
- **Package exclusion:** Updated `scripts/package_release.py` to exclude test files from release ZIP archives

**Files modified:**
- `requirements.txt`: Removed pytest (now production-only: pygame)
- `requirements-dev.txt`: New file with `-r requirements.txt` + pytest>=7.0.0
- `scripts/package_release.py`: Removed `test_projection_mapping.py` from include list
- `tests/conftest.py`: Adds parent directory to `sys.path` for clean imports

**Design rationale:**
- **Standard Python convention:** Test files belong in `tests/` directory, not repo root
- **Clean releases:** Distribution packages should not include developer tools or test suites
- **Import strategy:** `conftest.py` ensures tests can import `pumpkin_face` module without path hacks in each test file
- **Dev vs prod deps:** Users installing from ZIP don't need pytest; developers clone repo and use `requirements-dev.txt`

**pytest behavior:** All tests continue to pass unchanged. Pytest automatically discovers tests in `tests/` directory when run from repo root.
