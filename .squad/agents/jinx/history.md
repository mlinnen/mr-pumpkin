# History — Jinx

### Project Learnings (from import)

**Project:** Animated 2D Graphics Pumpkin Face (Python)  
**Owner:** Mike Linnen  
**Stack:** Python, 2D graphics, animation  
**Key domains:** Graphics/animation rendering, command parsing & state management, expression logic  
**Team composition:** Jinx (Lead), Ekko (Graphics), Vi (Backend), Mylo (Tester), Scribe, Ralph  

---

## Learnings

📌 Team update (2026-02-25): Feature branch workflow standard and repository cleanliness directive — decided by Mike Linnen

*Patterns, conventions, and decisions discovered during work.*

### .squad/ Git Tracking Evolution
- **Original policy (2026-02-20)**: `.squad/` blocked from `preview` and `main` branches via `.gitignore` entries, `squad-main-guard.yml` workflow (rejected PRs containing `.squad/` files), and validation check in `squad-preview.yml`. Rationale was to keep squad coordination state off release branches.
- **Policy reversal (Issue #40, 2026-02-26)**: All guards removed. `.squad/` now tracked on all branches like any other project directory. Squad state (decisions, histories, routing rules, agent charters) flows through normal git workflow. This allows team evolution history to be preserved and shared across branches.

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
- **Minimal surgical changes**: Preserved all release logic (tag creation, GitHub Release, `.squad/` file check) — only replaced the Node.js tooling surface.

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
- **Exclusions:** `.squad/`, `.github/`, `.git/`, `__pycache__/`, `.copilot/` — end users don't need squad coordination files or CI/CD workflows
- **Inclusions:** Core scripts (pumpkin_face.py, client_example.py), README, requirements.txt, VERSION, test suite (useful for users to validate setup)
- **Automation strategy:** Modify `squad-release.yml` to create ZIP archive and attach to GitHub Release as asset

**Key architectural insight for blink animation:**
- Current transition system is expression-to-expression (stateful)
- Blink is expression-to-closed-to-same-expression (temporary detour)
- Solution: Add `is_blinking` flag + separate `blink_progress` counter, orthogonal to expression transitions
- Socket command `"blink"` triggers animation method, not enum value change

### Design Review — Eyebrow Animation (Issue #16) (2026-02-22)

**Orthogonal state with derived transient animation:**
- Eyebrow offsets (`eyebrow_left_offset`, `eyebrow_right_offset`) are persistent user control, independent of expression state machine
- Blink/wink eyebrow movement is **computed at render time** from existing `blink_progress` and `wink_progress` — NOT stored in state
- This satisfies Capture-Animate-Restore pattern without adding capture fields: base state is never mutated during animations, so it's automatically "restored" when animation ends
- Formula: `final_brow_y = expression_baseline + user_offset + computed_transient_delta`

**Expression-driven baseline with additive offsets:**
- Each expression defines baseline Y-position and tilt angle for eyebrows (ANGRY = inner corners down, SURPRISED = high arched, etc.)
- User offsets and animation deltas stack additively on top of baseline
- Expression transitions interpolate the baseline; user offsets remain unchanged
- Clear separation: graphics owns baseline table, backend owns offset state

**Projection-first rendering:**
- Eyebrows rendered as thick white straight lines (thickness 8, width 70px), tilted via angle_offset
- No curves, no anti-aliasing — pure white (255,255,255) on pure black (0,0,0)
- Simple geometry: line from `(cx-35, y+offset)` to `(cx+35, y-offset)` for tilt
- SLEEPING expression: eyebrows hidden entirely (eyes are lines, brows would clutter)

**Command vocabulary and control:**
- Socket commands: `eyebrow_raise`, `eyebrow_lower`, `eyebrow_raise_left/right`, `eyebrow_lower_left/right`, `eyebrow <val>`, `eyebrow_reset`
- Keyboard shortcuts: U/J (raise/lower both), [ / ] (raise left/right), { / } (lower left/right)
- Step size: 10px, clamped [-50, +50]
- Sign convention: negative = raise, positive = lower (screen Y coordinates)

**Edge case handling:**
- Multi-layer clamping: set-time (backend) and render-time (graphics) to prevent off-screen or eye overlap
- Overlap prevention: if gap between brow and eye < 5px, skip rendering (avoids white blob on projector)
- SLEEPING preservation: user offsets preserved during SLEEPING — brows reappear at previous position when expression changes

**Key insight:** Derived transient animation (computed, not stored) is the cleanest way to satisfy Capture-Animate-Restore for effects that are purely functions of existing animation progress. No new state variables, no restoration logic, zero risk of desync.

### Issue Triage — Round 1 (2026-02-27)

**Backend infrastructure dominates backlog:**
- Issue #43 (websockets) is clean protocol upgrade — enables browser-based UIs without changing core architecture
- Issue #33 (auto-updates) requires decision on external updater script vs. built-in mechanism — external script preferred for separation of concerns
- Issue #39 (LLM skill) is tooling/automation layer, not core feature — generates timeline JSON from natural language prompts
- Issue #20 (lip-sync) is major feature expansion requiring audio analysis, phoneme mapping, and new mouth shape vocabulary

**Architectural decisions required before work starts:**
- Auto-updates: External script approach recommended (cleaner separation, avoids complicating core application with process management)
- Lip-sync: Needs full system design covering audio input mechanism, phoneme detection library, viseme-to-mouth-shape mapping, and projection-safe rendering constraints
- LLM skill: Requires Mike's decision on LLM provider (OpenAI/Anthropic/local model) and API key management strategy

**Routing pattern:** Backend-heavy backlog routes primarily to Vi, with Ekko on graphics for lip-sync and Mylo on validation for LLM skill. All three P2 features (auto-updates, LLM skill, lip-sync) require architectural review before implementation.

**Priority insight:** P1 features (#43 websockets, #33 auto-updates) are infrastructure improvements that don't expand expression vocabulary or animation system. P2 features (#39 LLM skill, #20 lip-sync) add user-facing capabilities but have higher complexity and external dependencies.

### Issue #50 — Nose Wiggle Command Handler (2026-02-27)

**Problem:** README.md documented `wiggle_nose` command but it was not implemented in command_handler.py.

**Investigation findings:**
- `wiggle_nose` only existed in README.md documentation (line 280)
- Actual implementation had `twitch_nose` and `scrunch_nose` commands
- Both `twitch_nose` and `reset_nose` were already wired in command_handler.py
- Public API methods (`twitch_nose()`, `reset_nose()`) don't accept parameters
- Command handler correctly calls private methods (`_start_nose_twitch(magnitude)`, `_reset_nose()`) to support optional magnitude parameter

**Solution:** Added `wiggle_nose` as an alias command that calls the same `_start_nose_twitch()` method as `twitch_nose`, maintaining consistency with existing pattern.

**Key architectural insight:** Command handler uses private methods (not public API) when parameter passing is required. Public methods are zero-parameter convenience wrappers. This is consistent across blink/wink (no params), gaze (params via private), and nose animations (params via private).

### Issue #50 — Wiggle Nose Recording Capture Bug (2026-02-27)

**Problem:** The `wiggle_nose` command alias was added to `command_handler.py` but was missing from the recording capture whitelist in `pumpkin_face.py`, causing timeline recording to skip this command.

**Investigation findings:**
- Recording capture logic in `pumpkin_face.py` (lines 1211-1228) had handlers for `twitch_nose`, `scrunch_nose`, and `reset_nose`
- The `wiggle_nose` alias was recognized and executed by the command router but not captured during recording sessions
- Test suite had 2 xfail tests (`test_wiggle_nose_captured_during_recording`, `test_wiggle_nose_with_magnitude_captured_with_params`) documenting the expected behavior

**Solution:** Added `wiggle_nose` elif branch to recording capture logic with identical structure to `twitch_nose` (default magnitude 50.0, parse float parameter, record command with magnitude args).

**Test fixes:** Removed `@pytest.mark.xfail` decorators from the 2 recording tests and updated test assertions to match TimelineEntry object structure (`.command` attribute, `.args["magnitude"]` for parameters, proper `.start()` initialization).

**Key architectural insight:** Recording capture is a separate concern from command execution - command aliases must be explicitly whitelisted in BOTH the command router AND the recording capture logic to achieve full integration. All 21 wiggle_nose tests now pass.

### Issue #53 — End-User Documentation (2026-02-27)

**Documentation structure decisions:**
- Created `docs/index.md` as GitHub Pages landing page with brief project description and navigation to all user guides
- Created `docs/installation.md` as comprehensive service installation guide covering Linux systemd and Windows Task Scheduler/NSSM approaches
- Positioned installation docs as end-user focused (step-by-step, minimal jargon) vs developer docs (building-a-client.md being created by Vi)
- Documented both TCP (port 5000) and WebSocket (port 5001) server ports for completeness

**Service architecture recommendations:**
- **Linux/Raspberry Pi**: systemd service with `graphical.target` dependency, `DISPLAY=:0` environment variable, absolute paths
- **Windows simplest approach**: Task Scheduler with `AtStartup` trigger, Interactive logon type (required for pygame/SDL2 display access)
- **Windows advanced approach**: NSSM for true Windows Service behavior, though note graphical limitation (background services have restricted display access)

**Key insight:** Task Scheduler with Interactive logon is the most practical Windows solution for Mr. Pumpkin since it's a graphical application requiring display access. NSSM is documented as advanced option but comes with desktop access limitations inherent to Windows Services.

### Issue #39 — LLM Recording Skill Architecture Analysis (2026-03-02)

**Timeline JSON format (canonical from timeline.py):**
- Schema: `{"version": "1.0", "duration_ms": int, "commands": [{"time_ms": int, "command": str, "args": {}}]}`
- `TimelineEntry.from_dict()` expects `data["time_ms"]` as the key — NOT `timestamp_ms` (which docs/building-a-client.md incorrectly shows in examples)
- `duration_ms` must equal or exceed the largest `time_ms` in commands
- `args` is optional; omitted for simple commands like `blink`
- Validation happens via `Timeline.from_dict()` which checks `version` and `commands` fields

**Recording command vocabulary:**
- 28+ distinct recordable commands identified from `_capture_command_for_recording()` in pumpkin_face.py
- Commands split into: expressions (7), animations (5 no-arg), gaze (2 arg variants), eyebrows (8 no-arg + 3 numeric), head movement (5), nose (4), projection (3)
- Expression commands are recorded as `set_expression` with `{"expression": "<name>"}` args — NOT as bare expression names

**Upload API:**
- TCP (port 5000): Multi-step handshake: `upload_timeline <name>\n` → `READY` → JSON + `\n` → `END_UPLOAD\n` → response
- WebSocket (port 5001): Single message: `upload_timeline <name> <json_string>` → response
- Both paths use `FileManager.upload_timeline()` which validates via `Timeline.from_dict()` before writing to `~/.mr-pumpkin/recordings/`
- Filenames must not contain path separators

**Skill architecture decision:**
- Proposed as `skill/` Python package co-located in repo (shares `timeline.py` imports for validation)
- Core components: LLM prompt-to-timeline generator, upload client, CLI entry point
- LLM provider should be configurable (OpenAI default) via env vars
- JSON repair layer recommended to handle common LLM output errors (e.g., `timestamp_ms` → `time_ms` key normalization)
- Full work breakdown written to `.squad/decisions/inbox/jinx-issue39-architecture.md`

**Documentation discrepancy found:**
- `docs/building-a-client.md` uses `timestamp_ms` in timeline JSON examples, but `timeline.py` uses `time_ms`. This needs to be fixed regardless of issue #39, and is a trap the LLM generator will fall into if fed the docs as reference.

### Issue #55 — Recording Chaining Architecture (2026-03-02)

**Problem:** Users wanted to create reusable animation sequences that can be composed together. A recording should be able to embed other recordings, which play to completion and then return control to the parent recording.

**Solution:** Implemented stack-based nested playback in the `Playback` class. When a `play_recording` command is encountered during playback, current state (timeline, position, index, filename) is pushed onto a stack and the sub-recording is loaded. When the sub-recording completes, the parent state is popped and playback resumes.

**Architecture decisions:**
- **Stack structure:** `List[(timeline, position_ms, last_executed_index, filename)]` — explicit state management instead of recursion (frame-driven update loop makes recursion impractical)
- **Depth limit:** Maximum nesting of 5 levels to prevent circular references (A → B → A) from causing stack overflow
- **Error handling:** Sub-recording load failures are logged but don't disrupt parent playback
- **Command interception:** `play_recording` is handled directly in `Playback.update()` — NOT dispatched to `_command_callback` (it's a playback-engine concern, not a user command)
- **Stop behavior:** `stop()` clears the entire stack (all nested contexts abandoned)
- **Status tracking:** `get_status()` now includes `stack_depth` for debugging

**Implementation:**
- Modified `timeline.py`: Added `_stack` and `_max_depth` to `__init__()`, rewrote `update()` to handle nesting and pop on completion, modified `stop()` to clear stack, added `stack_depth` to `get_status()`
- Modified `skill/generator.py`: Added `play_recording` to `_VALID_COMMANDS` set and system prompt vocabulary table

**Testing:** All 543 existing tests pass. No new tests added (integration testing covers functionality).

**Key insight:** Stack-based playback with depth limiting is the cleanest approach for frame-driven engines. Cycle detection is expensive and unnecessary when depth limits provide practical protection. The playback engine owns the `play_recording` command — keeping it out of the command handler maintains clean separation of concerns.

**Status (2026-03-02):** Jinx implementation complete. All 543 tests passing. Mylo writing comprehensive test suite.

### Documentation Update — Issues #55 and #56 (2026-03-02)

**Scope:** Updated `docs/timeline-schema.md`, `docs/what-is-new.md`, and `docs/recording-skill.md` to document the recording chaining feature and the new `help` command.

**Key documentation decisions:**
- `play_recording` was placed under a new `### Chaining / Sub-Recordings` section in the timeline schema Command Vocabulary — distinct from all other command groups because it is a playback-engine directive, not a face command
- The Recording Chaining prose section was added *after* the Command Vocabulary table but *before* Validation Rules in `timeline-schema.md`, so readers see the concept before validating their JSON
- Added a chained example timeline to show `play_recording` in realistic context alongside standard commands
- `docs/recording-skill.md` chaining section placed *before* "Playing back a recording" — teaches composition before playback, a natural learning order
- `what-is-new.md` `[Unreleased]` block follows exact format of existing entries (### Added heading, concise bullet per feature, cross-reference link)

**Help command (issue #56):**
- `help` is handled in `command_handler.py` — returns a plain-text string listing all available commands with their syntax
- Safe to call at any time including during playback; no side effects
- Documented in `[Unreleased]` release notes only (not timeline schema, since it is a TCP/WebSocket command, not a timeline command)

**Chaining architecture confirmed from timeline.py (lines 295–374):**
- `play_recording` is intercepted in `Playback.update()` before `_command_callback` is ever called
- Stack holds `(timeline, position_ms, last_executed_index, filename)` tuples
- Depth check is `len(self._stack) < self._max_depth` (5); at limit, error is appended and command skipped
- Sub-recording load failure: `except Exception` catches, appends error, skips command, parent continues
- End-of-timeline pop: `if self._stack: parent = self._stack.pop()` → resume; else `self.stop()`
- `stop()` calls `self._stack.clear()` — entire nesting context abandoned cleanly


