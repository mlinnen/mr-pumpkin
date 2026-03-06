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
📌 Team update (2026-02-27): Issue triage Round 1: #43 (websockets P1), #39 (LLM skill P2, Vi+Mylo), #33 (auto-updates P1), #20 (lip-sync P2, Vi+Ekko) — decided by Jinx
📌 Team update (2026-03-02): Issue #39 architecture finalized: LLM provider abstraction, JSON validation, upload client, CLI entry point — decided by Jinx, Vi, Mylo, Ekko
📌 Team update (2026-03-03): Issue #54 resolved: Migrated GeminiProvider from google-generativeai to google-genai SDK. Updated requirements.txt, all 27 tests pass — decided by Vi, Mylo
📌 Team update (2026-03-03): Issue #57 resolved: Built Jekyll 4.3 static site for GitHub Pages. Custom dark theme (orange #FF6B00 on #0d0d0d), 7 pages + blog, responsive nav, updated squad-docs.yml CI — decided by Vi

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

**Architecture decision:** Exclude `.squad/`, `.github/`, `.git/`, `__pycache__/`, `.copilot/` from release package. Include `docs/` folder (owner override of earlier decision).

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

### Timeline Data Structure & Playback Engine (Issue #34, WI-1 & WI-2)

**What:** Implemented core timeline data structure and frame-based playback engine for recording and playing back TCP command sequences.

**Key files:**
- `timeline.py` — Timeline, TimelineEntry, Playback, PlaybackState classes

**Timeline Format (JSON):**
Chose JSON for human-readability and forward compatibility:
```json
{
  "version": "1.0",
  "duration_ms": 5000,
  "commands": [
    {"time_ms": 0, "command": "set_expression", "args": {"expression": "happy"}},
    {"time_ms": 1000, "command": "blink"},
    {"time_ms": 3000, "command": "play_timeline", "args": {"filename": "other.json"}}
  ]
}
```

**Design decisions:**
1. **Millisecond timestamps:** Provides sub-second precision while staying compatible with 60 FPS frame timing (~16.67ms per frame)
2. **Frame-based playback:** Integrates with game loop via `update(dt_ms)` called each frame — no separate threads needed
3. **Flat file naming:** All recordings in `~/.mr-pumpkin/recordings/` with unique filenames (no subdirectories)
4. **Nested playback support:** Commands can include `play_timeline` to trigger other recordings
5. **Graceful error handling:** Invalid commands during playback stop execution and return error messages
6. **Callback pattern:** Playback engine calls `command_callback(command, args)` for each command — decouples from PumpkinFace internals

**Frame-based timing pattern (60 FPS):**
- Each frame passes delta time (`dt_ms`) to `playback.update(dt_ms)`
- Playback advances `current_position_ms += dt_ms`
- Commands execute when `cmd.time_ms <= current_position_ms`
- Timing precision: within one frame (~16.67ms at 60 FPS)
- No drift: position tracked independently of frame rate fluctuations

**State machine:**
- `PlaybackState.STOPPED` — No active playback, position at 0
- `PlaybackState.PLAYING` — Advancing through timeline, executing commands
- `PlaybackState.PAUSED` — Position frozen, no command execution

**Execution tracking:**
- `_last_executed_index` prevents re-execution of commands during seek or pause/resume
- Seek updates this index to skip already-executed commands before target position
- Invalid command stops playback immediately (fail-fast pattern)

**File storage:**
- Default: `~/.mr-pumpkin/recordings/` (cross-platform via `pathlib.Path.home()`)
- Auto-creates directory on first save
- JSON files with `.json` extension (auto-appended if omitted)
- Atomic operations: rename/delete check existence first

**Playback control methods:**
- `play(filename)` — Load timeline and start from beginning
- `stop()` — Reset to position 0, state = STOPPED
- `pause()` / `resume()` — Freeze/unfreeze position advancement
- `seek(position_ms)` — Jump to arbitrary position, update execution index
- `update(dt_ms)` — Advance playback, execute commands, return errors

**Status query methods:**
- `get_status()` — Returns dict with state, filename, position, duration, is_playing
- `get_duration(filename)` — Query duration without loading into playback
- `list_recordings()` — Scan directory, return metadata for all valid timelines

**File management methods:**
- `delete_recording(filename)` — Remove file (raises FileNotFoundError if missing)
- `rename_recording(old, new)` — Rename file (raises FileExistsError if collision)

**Testability patterns:**
- All state is queryable (state, position, duration)
- Callback injection for command execution (easy to mock)
- Timeline serialization is lossless (round-trip save/load)
- Errors returned as strings (not just logged)

**Lessons learned:**
1. **Frame-based > thread-based:** Simpler state management, no race conditions, integrates cleanly with existing game loop
2. **Callback decoupling:** Playback engine doesn't know about PumpkinFace — testable in isolation
3. **Index tracking prevents re-execution:** Critical for pause/resume and seek — without it, commands execute multiple times
4. **Millisecond precision sufficient:** 60 FPS gives ~16ms granularity, matches human perception for animations
5. **Fail-fast on errors:** Invalid command immediately stops playback — prevents cascading failures
6. **Flat file structure simplifies:** No directory tree logic, unique names enforced by filesystem

### Seek, Recording, and File Management (Issue #34, WI-3 through WI-6)

**What:** Extended timeline.py with seek functionality, recording session capture, playback status queries, and file management operations.

**Key additions:**
- `RecordingSession` class — Command capture for creating timelines
- `FileManager` class — File operations (upload, download, delete, rename, list)
- Enhanced `Playback.seek()` — Fast-forward/rewind with state preservation
- `Playback.get_status()` — Query playback state, position, duration
- `update()` execution order fix — Commands execute before end-of-playback check

**Seek implementation (WI-3):**
- Clamps position to [0, duration_ms] range automatically
- Updates `_last_executed_index` to track which commands were already executed
- Works in all playback states (STOPPED, PLAYING, PAUSED)
- Seeking forward skips intermediate commands (no execution)
- Seeking backward doesn't re-execute already-run commands
- State machine preserved: seeking while PLAYING keeps state PLAYING, seeking while PAUSED keeps state PAUSED

**Recording session pattern (WI-5):**
- `start()` — Capture start time as milliseconds (using `time.time() * 1000`)
- `record_command(cmd, args)` — Store command with relative timestamp
- `stop(filename=None)` — Save timeline to JSON file
- Auto-naming: If filename is None, uses `recording_YYYY-MM-DD_HHMMSS.json` format
- Validation: Raises ValueError if no commands captured, FileExistsError if filename collision
- `cancel()` — Discard recording without saving
- All timestamps relative to recording start (not absolute wall clock)

**File management API (WI-4):**
- `list_recordings()` — Returns list with filename, size_bytes, created_at, duration_ms
- `download_timeline(filename)` — Return raw JSON string (validates JSON before returning)
- `upload_timeline(filename, json_content)` — Parse and validate JSON structure, then save
- `delete_timeline(filename)` — Remove file from disk (raises FileNotFoundError if missing)
- `rename_timeline(old, new)` — Atomic rename operation (checks both existence and collision)
- All methods auto-append `.json` extension if omitted
- All operations scoped to `~/.mr-pumpkin/recordings/` directory

**Status query pattern (WI-6):**
- `get_status()` returns dict: `{"state": "playing", "filename": "test.json", "position_ms": 1234, "duration_ms": 5000, "is_playing": True}`
- State values: "stopped", "playing", "paused" (from PlaybackState enum)
- `is_playing` convenience field: True only when state == PLAYING
- All fields always present (filename can be None when stopped)

**Critical bug fix — Command execution order:**
- **Problem:** Original `update()` checked `position >= duration` BEFORE executing commands, causing commands at exact duration timestamp to never execute
- **Solution:** Moved end-of-playback check to AFTER command execution loop
- **Impact:** Commands at final timestamp now execute correctly before playback stops
- **Pattern:** Execute → then check end, not check end → then execute

**Seek state machine integration:**
- Seek updates position without changing state (PLAYING stays PLAYING, PAUSED stays PAUSED)
- `_last_executed_index` reset to -1, then recalculated by scanning commands before new position
- Commands with `time_ms < position_ms` marked as already executed
- No commands are executed during seek operation itself (position jumps instantly)
- Next `update()` call will execute commands from new position forward

**Recording timestamp capture:**
- Start time captured as `time.time() * 1000` (milliseconds since epoch)
- Each command timestamp = `current_time_ms - start_time_ms` (relative offset)
- Ensures timeline is self-contained (not dependent on wall clock)
- Compatible with playback engine's millisecond-based timing

**File operations error handling:**
- `FileNotFoundError` — Consistent across delete, rename, download when file missing
- `FileExistsError` — Consistent across upload, rename, record stop when name collision
- `ValueError` — Invalid JSON structure or empty recording
- Clear error messages include filename for debugging

**Design decisions:**
1. **Separate RecordingSession from Playback:** Recording is write-only, playback is read-only — different concerns, different classes
2. **Separate FileManager from Playback:** File ops are pure I/O, playback is state machine — cleaner separation of concerns
3. **Auto-append .json extension:** User convenience — `"test"` and `"test.json"` both work identically
4. **Timestamp-based auto-naming:** Avoids filename collisions, human-readable, sortable by creation time
5. **Execute-then-check order in update():** Ensures final command executes, matches user expectation that duration includes all commands
6. **Seek doesn't re-execute:** Fast-forward/rewind is instant position change, not "fast playback" — commands between old/new position are skipped

**Testing approach:**
- `test_timeline_features.py` — 5 comprehensive tests covering all WI-3 through WI-6 features
- Tests use temporary directories for isolated file operations
- Validates edge cases: seek clamping, empty recordings, duplicate filenames, invalid JSON
- Confirms command execution order fix (final command executes)
- All 332 existing tests still pass — no regressions

**TCP integration readiness:**
- RecordingSession can wrap any command sent to PumpkinFace (set_expression, blink, etc.)
- FileManager provides complete CRUD operations for remote timeline management
- Playback status queries enable real-time progress monitoring over TCP
- Seek enables scrubbing UI controls (progress bar drag, skip forward/back buttons)

### Recording File Upload with Validation (Issue #44)

**What:** Implemented `upload_timeline` socket command to allow clients to upload recording files to the server with automatic validation.

**Key additions:**
- `pumpkin_face.py`:
  - Added `FileManager` import for file operations
  - Added `self.file_manager = FileManager()` initialization in `__init__`
  - Implemented `upload_timeline` socket command handler with multi-line JSON protocol
  - Uses READY/END_UPLOAD handshake for reliable multi-line data transfer
  - Added "upload_timeline" to timeline_command list to prevent playback pause

- `client_example.py`:
  - Added `upload_timeline(filename, json_file_path)` function for client-side uploads
  - Reads local JSON file, connects to server, sends filename
  - Waits for READY signal before transmitting JSON
  - Sends END_UPLOAD marker to signal completion
  - Handles errors and provides feedback

**Validation strategy:**
- JSON syntax validation (invalid JSON immediately rejected)
- Timeline structure validation (delegated to `FileManager.upload_timeline()`)
- File collision detection (raises FileExistsError if file exists)
- Path separator validation (prevents directory traversal attacks)
- Clear error messages returned to client on any validation failure

**Protocol design:**
1. Client sends: `upload_timeline <filename>\n`
2. Server responds: `READY\n`
3. Client sends: JSON content (multiple lines allowed)
4. Client sends: `END_UPLOAD\n`
5. Server responds: `OK Uploaded <filename>.json\n` or error message

**Error handling:**
- Missing filename → "ERROR Missing filename"
- Invalid filename (contains path separators) → "ERROR Invalid filename: path separators not allowed"
- File exists → "ERROR File already exists: <filename>"
- Invalid JSON → "ERROR Invalid timeline: <error details>"
- Connection lost → "ERROR Connection lost while reading JSON"

**Testing:** All 362 existing tests pass with no regressions. Feature integrates cleanly with existing recording/playback infrastructure.

### WebSocket Migration Analysis (Issue #43)

**What:** Analyzed TCP socket implementation for WebSocket migration to enable browser-based control panels.

**Current socket architecture:**
- **Footprint:** 680 lines (lines 1352-2035 in pumpkin_face.py)
- **Protocol:** Text-based, newline-delimited (`\n` terminated), UTF-8 encoded
- **Server:** Single-threaded blocking socket, one client at a time, runs in daemon thread
- **Port:** 5000 (localhost only)
- **Command format:** Case-insensitive string commands (`"blink"`, `"happy"`, `"gaze 45 -30"`)
- **Response format:** `"OK <message>\n"` or `"ERROR <message>\n"`, JSON strings for status queries
- **Special protocol:** `upload_timeline` uses stateful handshake (READY/END_UPLOAD markers) for multi-line JSON transfer

**State sharing pattern:**
- Socket handler (daemon thread) directly modifies PumpkinFace instance state variables via method calls
- No explicit mutex/lock protection (relies on Python GIL for thread safety)
- Game loop (main thread) runs at 60 FPS, reads state modified by socket handler
- Orthogonal state system: each feature (gaze, eyebrows, projection, animations) has independent state variables

**Command handler architecture:**
- Giant if-elif chain (60+ commands in linear sequence)
- No routing table or abstraction layer
- Command parsing embedded directly in socket handler
- Each handler: parse → validate → call method → send response → log → continue

**Proposed approach:**
1. **Dual-protocol support:** Run TCP and WebSocket servers in parallel (backward compatible)
2. **Library choice:** `websockets` (asyncio-based, lightweight, pure Python, Pi-compatible)
3. **Port allocation:** TCP on 5000 (unchanged), WebSocket on 5001 (new)
4. **Command abstraction:** Extract command parsing to `CommandRouter` class in new `command_handler.py` module
5. **Protocol adaptation:** Both TCP and WebSocket call same `router.execute(command_str)` method
6. **Multi-line handling:** TCP keeps READY/END_UPLOAD handshake, WebSocket uses single JSON message

**Architecture pattern:**
```python
class CommandRouter:
    def __init__(self, pumpkin_face):
        self.pumpkin = pumpkin_face
    
    def execute(self, command_str: str, format='text') -> str:
        """Parse and execute command, return response.
        Protocol-agnostic: works for both TCP and WebSocket."""
        # Extract existing if-elif logic from socket handler
        # Return "OK ..." or "ERROR ..." strings (text mode)
        # Or {"status": "ok", "message": "..."} (json mode)
        pass
```

**Implementation plan (5 milestones, 21-29 hours total):**
1. **Command Router Extraction** (5-7h) — Decouple parsing from TCP handler
2. **WebSocket Server Setup** (3-4h) — Add parallel WebSocket server on port 5001
3. **JSON Protocol Adapter** (2-3h) — Support `{"command": "blink"}` format for WebSocket
4. **Multi-line Upload Refactor** (4-5h) — Dual protocol support for `upload_timeline`
5. **Documentation & Testing** (3-4h) — README, WebSocket API docs, integration tests, browser client example

**Risk assessment:**
- **Threading + asyncio:** WebSocket uses asyncio in separate thread; may need `asyncio.to_thread()` for CPU-bound operations
- **GIL contention:** Two socket servers + 60 FPS game loop competing for GIL; profile under load to detect frame drops
- **Pi compatibility:** Test `websockets` library install on Pi 3/4/5 before release
- **Command router abstraction:** `upload_timeline` TCP handshake hard to abstract; use protocol-specific handlers
- **Breaking changes:** Run all 362 tests after each milestone to catch regressions
- **Port conflicts:** Make WebSocket port configurable via env var, graceful degradation if bind fails
- **Browser CORS:** Document need for HTTP server to serve HTML client (can't use `file://` protocol)

**Collaboration requirements:**
- **Mylo (Tester):** Test strategy review, browser compatibility testing, Pi verification
- **Jinx (Lead):** Approval for port 5001 and websockets dependency, API format decision

**Recommendation:** Proceed with dual-protocol implementation using `websockets` library. Zero breaking changes, browser compatibility unlocked, clean abstraction layer, minimal dependencies, incremental rollout.

**Lessons learned:**
1. **Protocol agnostic design:** Command router enables testing in isolation, supports multiple transport protocols
2. **Backward compatibility first:** Dual-protocol approach avoids breaking existing TCP clients during migration
3. **Stateful protocols need escape hatches:** TCP upload handshake can't be cleanly abstracted; protocol-specific handlers required
4. **Threading model matters:** asyncio + threading + GIL requires careful testing under load to detect contention
5. **Incremental milestones reduce risk:** 5 small milestones (each 2-7 hours) easier to test and rollback than monolithic rewrite

---

## Milestone 1 Complete: Command Router Extracted (Issue #43)

**Date:** 2025-01-28
**Status:** ✅ Complete — 403 tests passing, zero regressions

### Implementation Summary
Successfully extracted ~660 lines of command parsing logic from TCP socket handler into new `CommandRouter` class. All 60+ commands now route through protocol-agnostic command layer.

**Files modified:**
- `command_handler.py` (NEW) — 700 lines, CommandRouter class with execute() method
- `pumpkin_face.py` — Added CommandRouter import and initialization, replaced socket handler command if-elif chain with router delegation

**Command categories extracted:**
- Expression commands (neutral, happy, sad, angry, surprised, scared, sleeping)
- Animation commands (blink, wink_left, wink_right, roll_clockwise, roll_counterclockwise)
- Gaze control (2-arg and 4-arg variants)
- Eyebrow commands (raise, lower, independent left/right, reset, parametric)
- Head movement (turn_left/right/up/down, center_head, projection offsets)
- Nose animation (twitch_nose, scrunch_nose, reset_nose)
- Timeline playback (play, pause, resume, stop, seek)
- Recording (record_start, record_stop, record_cancel)
- File management (list_recordings, delete_recording, rename_recording, upload_timeline, download_timeline)
- Status queries (timeline_status, recording_status)
- Reset command

**Special handling preserved:**
- `upload_timeline` still uses socket-specific multi-step protocol (READY/END_UPLOAD handshake)
- Animation commands return empty string (no response sent to client)
- Expression/timeline commands return "OK ..." or "ERROR ..." strings
- Status queries return JSON
- Recording capture logic preserved (commands auto-record during active sessions)
- Playback pause on manual override preserved

**Test results:**
- 403/403 tests passing (100% success rate)
- Zero behavioral changes
- All client integration tests passing
- Recording, playback, and file management verified

### Learnings
1. **Extracted command parsing from socket handler into CommandRouter class:** Clean separation enables protocol-agnostic command execution
2. **Protocol-agnostic command execution enables dual TCP/WebSocket support:** Same command logic works for both transports
3. **362 tests verify zero behavioral changes after refactoring:** Comprehensive test coverage caught all edge cases during extraction
4. **TCP recv() deadlock pattern — no-response commands:** When a server conditionally sends a response (only `if response:`), a client that always calls `recv()` will deadlock if the server sends nothing. Both sides block waiting on the other. Fix: call `socket.shutdown(SHUT_WR)` after `send()` to signal EOF. The server's `recv()` returns `b""`, breaking its loop and closing the connection — which unblocks the client's `recv()` with empty data. This is the correct pattern for single-exchange TCP command protocols.

**Unblocks:** Milestone 2 (WebSocket server setup) ready to begin

## WS upload_timeline inline fix
- WebSocket upload_timeline uses a single-message inline format: `upload_timeline <filename> <json>`  
- TCP uses a multi-step handshake (READY/END_UPLOAD); the command_router returns `UPLOAD_MODE` as a placeholder — not suitable for WS  
- Fix: intercept `upload_timeline` in `_ws_handler` before routing to command_router; call `file_manager.upload_timeline(filename, json_content)` directly  
- Test update: send JSON content inline (not a file path), assert `OK Uploaded <filename>.json`

## Client Documentation (Issue #53)

**What:** Created comprehensive end-user documentation for building clients that control Mr. Pumpkin.

**File:** `docs/building-a-client.md`

**Audience:** End users integrating Mr. Pumpkin into their projects (home automation, Halloween displays, performances) — NOT developers of Mr. Pumpkin itself.

**Coverage:**
- Connection basics (TCP port 5000, one command per connection)
- Quick start (minimal 5-line Python example)
- Complete command reference organized by category (expressions, animations, gaze, eyebrows, head movement, nose, projection, recording, playback, file management)
- Response handling (fire-and-forget, OK/ERROR text, JSON status)
- Multi-language examples (Python, Node.js, C#, bash/netcat)
- Timeline file format and programmatic creation
- Upload protocol (multi-step READY/END_UPLOAD handshake)
- Troubleshooting guide (connection refused, port conflicts, no response, remote access)

**Documentation principles:**
1. **User-focused tone:** Assumes basic programming knowledge but not networking expertise
2. **Working code examples:** Every command shown with real, copy-pasteable code
3. **Protocol clarity:** TCP socket pattern clearly explained (connect → send → shutdown write → read → close)
4. **Complete reference:** All commands from command_handler.py documented with parameters and return values
5. **Real-world use cases:** Home automation, Halloween displays, interactive performances, art installations

**Key insight:** The upload_timeline protocol is complex (5-step handshake) compared to other commands — deserves its own section with detailed example code.

**Links to existing resources:** Points users to `client_example.py` for complete working implementation.

## WebSocket Documentation Update

**What:** Updated docs/building-a-client.md to document WebSocket support alongside existing TCP documentation.

**Changes made:**
1. **Intro update:** Changed "All communication happens through simple text commands sent over TCP sockets" to mention both TCP (port 5000) and WebSocket (port 5001)
2. **Connection Basics expansion:** Split into two subsections (TCP and WebSocket) with clear comparison table
3. **New WebSocket Connection section:** Comprehensive guide with Python async/await examples, Node.js examples, interactive control patterns
4. **Upload Timeline:** Split into TCP (multi-step) vs WebSocket (single message) methods
5. **Troubleshooting:** Added "WebSocket Not Available" entry (missing websockets library, port conflicts)

**Key technical facts documented:**
- Port 5001 for WebSocket (vs TCP on 5000)
- Persistent connection model (one connection, many commands)
- Requires websockets library (pip install websockets)
- Same commands work on both protocols
- Responses only sent for commands that return data (fire-and-forget commands get no response over WebSocket)
- Upload timeline simpler on WebSocket: single message format vs TCP 5-step handshake
- Server gracefully disables WebSocket if library not installed

**Documentation philosophy:**
- Side-by-side comparison helps users choose protocol (TCP for scripts, WebSocket for interactive/streaming)
- Async/await examples for Python WebSocket (modern idiomatic approach)
- Preserved all existing TCP docs (backward compatibility)
- Surgical edits only — no rewrites of working content

### Recording Skill Package (Issue #39 — WI-1, WI-2, WI-3, WI-7)

**What:** Built the `skill/` package — LLM-powered timeline generator and upload client for Mr. Pumpkin.

**Files created:**
- `skill/__init__.py` — Package with public API exports
- `skill/generator.py` — Prompt-to-Timeline generator
- `skill/uploader.py` — TCP and WebSocket upload client
- `skill/requirements.txt` — Skill-specific dependencies

**Key import path pattern:** `skill/generator.py` uses `sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))` before `from timeline import Timeline` to handle the parent-directory import cleanly when running as a package.

**LLM provider abstraction pattern:**
- Abstract `LLMProvider` base class with single `generate(system_prompt, user_prompt) -> str` method
- `GeminiProvider` reads API key from `GEMINI_API_KEY` (fallback: `GOOGLE_API_KEY`)
- Provider passed as optional arg to `generate_timeline()` — defaults to `GeminiProvider`
- Pattern enables swap to OpenAI / Anthropic / local models without changing call sites

**System prompt strategy:**
- Full 28-command vocabulary embedded as formatted table in system prompt constant `_SYSTEM_PROMPT`
- Two few-shot example timelines included (surprised→relieved, getting sleepy)
- Timing guidelines from Ekko's domain knowledge (blink ~300ms, expressions ~500ms gap)
- Schema constraints: version "1.0", ascending time_ms, duration_ms = last time_ms + buffer

**Repair heuristic pattern:**
- `_repair(data)` normalises `timestamp_ms` → `time_ms` in command entries before validation
- Handles common LLM mistake (our own docs had this inconsistency per architecture doc)
- `_extract_json(text)` strips ```json ... ``` or ``` ... ``` code fences from LLM responses

**Validation strategy:** Parse → Repair → `Timeline.from_dict()` — raises `ValueError` with clear message if validation fails.

**TCP upload pattern (from client_example.py):**
1. Connect with 10s timeout
2. Send `upload_timeline <filename>\n`
3. Wait for `READY` line
4. Send JSON + `\n`
5. Send `END_UPLOAD\n`
6. Read response; raise `ValueError` on ERROR

**WebSocket upload pattern:** Single-message `upload_timeline <filename> <json>`, async via `asyncio.run()`.

**WebSocket optional dependency:** Uses `importlib.util.find_spec("websockets")` to check availability; falls back to TCP with `RuntimeWarning` if ws requested but unavailable.

**Root requirements.txt conflict:** Root `requirements.txt` pins `websockets>=11.0,<12.0` but `skill/requirements.txt` needs `>=12.0`. Must be reconciled — see decisions inbox `vi-skill-package-decisions.md`.

**Doc bug fixed (WI-1):** All 4 occurrences of `timestamp_ms` in `docs/building-a-client.md` changed to `time_ms` to match `TimelineEntry.from_dict()` which reads `data["time_ms"]`.

### Google Gemini API Migration (Issue #54)

**What:** Migrated GeminiProvider from deprecated google-generativeai package to the new google-genai package.

**Files changed:**
- skill/generator.py — Updated GeminiProvider.__init__() and generate() to use client-based API
- equirements.txt — Added google-genai>=1.0.0 dependency

**Key API changes:**
- **Old:** import google.generativeai as genai + genai.configure(api_key) + genai.GenerativeModel(model_name, system_instruction)
- **New:** rom google import genai + rom google.genai import types + genai.Client(api_key=api_key)

**Pattern shift:**
- Old API: Model instance with embedded system instruction, call model.generate_content(user_prompt)
- New API: Client instance, call client.models.generate_content(model=..., contents=..., config=types.GenerateContentConfig(system_instruction=...))

**Critical change:** The system_prompt parameter in generate() is now actually used (passed to system_instruction), whereas the old implementation ignored it in favor of _SYSTEM_PROMPT baked into the model at construction time.

**Import error message:** Changed from "google-generativeai is required..." to "google-genai is required for GeminiProvider. Install it with: pip install google-genai" (removed version constraint for cleaner message).

**Tests:** All 27 tests in 	ests/test_skill_generator.py pass (they mock GeminiProvider so no actual package installation required for test suite).

### Help Command (Issue #56)

**What:** Added help command to CommandRouter.execute() in command_handler.py.

**Pattern:** Placed the handler in the "status query" section (before 	imeline_status), matching the convention for read-only informational commands. Returns a plain-text formatted string (not JSON) because help is human-readable documentation, not machine-parseable state — consistent with OK ... / ERROR ... plain text responses for action feedback.

**Key decisions:**
1. **Plain text over JSON:** Status commands (	imeline_status, ecording_status, list_recordings) return JSON because callers parse them. help is for humans at a terminal or WebSocket client — plain text is the right format.
2. **No recording capture:** help returns before the recording-capture code path, so it is never baked into a recorded timeline (correct — it's a query, not an animation command).
3. **No playback pause:** Returns early before the is_timeline_command guard, so sending help during playback does NOT pause the animation.
4. **Includes all commands:** All animation, eyebrow, projection, head, nose, timeline, recording, file-management, expression, and meta commands are documented with syntax and brief description.
5. **Alias documented:** list alias for list_recordings is explicitly called out.

### GitHub Pages Static Site (Issue #57)

**Branch:** squad/57-github-pages-site  
**PR:** #58

Built full Jekyll 4.3 site under docs/ with 7 pages, dark pumpkin theme, and mobile navigation. Navigation driven by _data/navigation.yml. All existing docs/*.md files received Jekyll front matter (non-destructive). Blog posts migrated to docs/_posts/. Search implemented as a GitHub redirect. Updated squad-docs.yml CI workflow: Ruby 3.2 + bundler cache, undle exec jekyll build, deploy via ctions/deploy-pages@v4.

**Key Decisions:**
- Jekyll 4.3 over Hugo/MkDocs — native GitHub Pages engine
- Custom _layouts/default.html over minima — full design control for dark theme
- GitHub search redirect over lunr.js — no build-time index overhead
- Trigger: push to preview branch touching docs/**

📌 Team update (2026-03-03): Jekyll GitHub Pages site built for Issue #57; PR #58 open

## 2026-03-03 10:45 - Lunr.js On-Site Search Implementation

Replaced the GitHub-redirect search with a proper client-side search using Lunr.js for the Jekyll docs site. Created search.json to generate a Jekyll-based search index, added a search results page (search.md), rewrote search.js to build and query the Lunr index, and updated default.html with baseurl meta tag for path resolution. The search form now navigates to /search?q= instead of opening GitHub search in a new tab. This provides a better UX with instant on-site search results.

## 2026-03-03 - Mouth Speech State Variables (Issue #59)

**What:** Added orthogonal mouth/speech control state machine infrastructure to PumpkinFace — first step implementing independent mouth control for speech simulation.

**Changes made:**
1. **State variables (line 115-118):** Added three mouth control variables after nose animation state block:
   - `self.mouth_viseme` — Current viseme override (None or "closed"|"open"|"wide"|"rounded")
   - `self.mouth_transition_progress` — Transition progress 0.0 → 1.0
   - `self.mouth_transition_speed = 0.15` — Faster than expression transitions (0.05) for snappy speech

2. **Public API methods (after line 539):** Added `set_mouth_viseme()` and `reset_mouth()`:
   - `set_mouth_viseme(viseme)` — Sets mouth to a viseme ("closed", "open", "wide", "rounded", "neutral", or None), resets transition progress
   - `reset_mouth()` — Clears speech override, returns mouth to expression-driven control

3. **Update loop (line 1107-1109):** Added mouth transition progress update in main update loop, placed between nose animation update and expression transition update:
   ```python
   if self.mouth_transition_progress < 1.0:
       self.mouth_transition_progress = min(1.0, self.mouth_transition_progress + self.mouth_transition_speed)
   ```

**Architecture pattern:** Follows the established orthogonal state machine pattern (same as eyebrows and nose). Mouth speech control is INDEPENDENT of the expression system — visemes can override expression-driven mouth shapes during speech, then release control back to the expression when done.

**Next steps:** Ekko will integrate these state variables into `_get_mouth_points()` and `_draw_mouth()` to blend viseme shapes with expression shapes. Command handler integration will come later.


## 2026-03-03 - Mouth Speech Commands Added (Issue #59)

**What:** Added mouth/speech control commands to CommandRouter in command_handler.py — second step implementing interactive mouth control for speech simulation.

**Commands added (before TIMELINE COMMANDS section, after reset_nose):**
1. **Individual viseme shorthand commands:**
   - mouth_closed — Set mouth to closed viseme (M, B, P sounds)
   - mouth_open — Set mouth to open viseme (AH, AA sounds)
   - mouth_wide — Set mouth to wide viseme (EE, IH sounds)
   - mouth_rounded — Set mouth to rounded viseme (OO, OH sounds)
   - mouth_neutral — Release mouth to expression-driven control

2. **Parameterized command:**
   - mouth <viseme> — Set mouth to named viseme (closed/open/wide/rounded/neutral)
   - Uses startswith("mouth ") pattern to match
   - Validates viseme name against valid set
   - Provides error message for invalid viseme names

**Implementation pattern:** Followed the established pattern from wiggle_nose command:
- Recording check: if self.pumpkin.recording_session.is_recording: self.pumpkin._capture_command_for_recording(data)
- Calls self.pumpkin.set_mouth_viseme(viseme) method added in previous task
- All commands return "" (empty string) like other animation commands
- Parameterized command uses data.split() to extract viseme name

**Help text updated:** Added 6 mouth command entries to help_text string before eset entry.

**Files modified:**
- command_handler.py — Added mouth commands (lines 303-358), updated help text (lines 492-497)

## Learnings
Updated client_example.py to document mouth speech commands (mouth_closed, mouth_open, mouth_wide, mouth_rounded, mouth_neutral) in both module docstring and interactive help text (Issue #59).

### Audio Analysis Provider Implementation (Issue #69)

**What:** Implemented `skill/audio_analyzer.py` — Gemini multimodal audio analysis for lip-sync and beat-driven animation.

**Key patterns:**
1. **ABC pattern mirrors LLMProvider:** AudioAnalysisProvider abstract base class with single `analyze_audio()` method, following exact same pattern as `skill/generator.py` LLMProvider for consistency
2. **Two-pass Gemini analysis:** Pass 1 extracts structured timing JSON (speech_segments, beats, pauses), Pass 2 extracts emotion as single word — separation prevents mixed-format responses
3. **File upload lifecycle:** Upload with `client.files.upload()`, poll `client.files.get()` until state == "ACTIVE" (required by Gemini), clean up with `client.files.delete()` in finally block
4. **Graceful JSON retry:** First parse attempt with lenient prompt, retry once with strict "JSON only" prompt if JSONDecodeError, then raise descriptive ValueError with both error messages
5. **MIME type detection:** Map file extensions (.mp3, .wav, .ogg, etc.) to MIME types for upload — critical for Gemini to accept audio files
6. **Dataclass hierarchy:** WordTiming, BeatEvent, PauseSegment nested in AudioAnalysis — clean structured data for downstream timeline builder

**Gotchas found:**
- Gemini file upload requires polling `get(name=file.name)` until state=="ACTIVE" before analysis — immediate use fails
- JSON responses sometimes wrapped in markdown fences even when prompt says "ONLY JSON" — always strip with regex fallback
- Emotion responses can be verbose (e.g., "The dominant emotion is happy") — need `.strip().lower()` and validation against expected set
- File cleanup in finally block prevents orphaned files in Gemini storage even if analysis fails

**Implementation decisions:**
- Used `google.genai` (not `google.generativeai`) to match existing GeminiProvider pattern in generator.py
- Logged at INFO level for analysis results (segment/beat/pause counts), DEBUG for file operations, WARNING for retries
- get_provider() factory function allows future providers (Whisper, AssemblyAI, etc.) without client code changes


## Learnings

**2025-01-XX: Timeline audio_file field (#68)**
- Added optional udio_file field to Timeline class for audio playback pairing
- Implemented lazy pygame imports inside Playback methods (not module-level) to avoid initialization overhead
- Audio playback is non-fatal: exceptions are caught and logged as warnings, animation continues without audio
- pygame.mixer.music provides simple single-file audio playback (load → play → stop)
- Backward compatibility maintained: audio_file is optional in JSON, older timelines continue working

**2025-01-XX: upload_audio endpoint implementation (#67)**

**What:** Added upload_audio server endpoint and client uploader to support audio file uploads for lip-sync/animation workflows.

**Key implementation patterns:**
1. **Protocol duality (TCP + WebSocket):** Mirrored existing upload_timeline pattern exactly — TCP uses multi-step handshake (command → READY → bytes → END_UPLOAD), WebSocket uses single-message base64 encoding
2. **Binary upload handling:** TCP handler accumulates raw bytes in chunks (4096), scans for delimiter in buffer, reassembles full audio file from chunk list
3. **Command routing exclusion:** Both upload_timeline and upload_audio bypass CommandRouter to handle socket-specific multi-step protocols directly in server handlers
4. **Auto-extension logic:** Server auto-appends .mp3 if filename has no extension, validates against allowed set (.mp3, .wav, .ogg)
5. **FileManager parallel:** upload_audio() method saves raw bytes with filepath.write_bytes(), validates format, raises FileExistsError if duplicate

**Files modified:**
- pumpkin_face.py: TCP handler (line 1537+), WebSocket handler (line 1580+)
- timeline.py: FileManager.upload_audio() method
- command_handler.py: Help text entry for upload_audio
- skill/uploader.py: upload_audio() client function with TCP and WS helpers

**Byte boundary handling approach:**
- Used chunked accumulation with delimiter scanning (similar to upload_timeline line-based approach but for binary data)
- Buffer reset after each scan to prevent memory bloat on large audio files
- Kept upload_buf as sliding window for END_UPLOAD detection only
- Early break on delimiter match prevents reading extra data

**Protocol decision:**
- TCP: upload_audio <filename> → wait READY → send raw bytes → send END_UPLOAD
- WebSocket: upload_audio <filename> <base64-encoded-bytes> (single message)
- Reason: Matches existing upload_timeline conventions for team consistency

**Pattern consistency:**
- Followed exact error message format from upload_timeline
- Reused FileExistsError exception pattern from FileManager.upload_timeline
- Client uploader signature matches upload_timeline (filename, data, host, ports, protocol) for API symmetry
