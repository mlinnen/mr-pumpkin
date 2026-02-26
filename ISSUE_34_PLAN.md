# Issue #34 Planning Document: Record & Playback Timeline

**Lead:** Jinx  
**Status:** Planning (awaiting approval)  
**Created:** 2026-02-14  
**Requested By:** User  

---

## Executive Summary

Issue #34 adds recording and playback capabilities to Mr. Pumpkin, allowing users to:
- **Record** a sequence of TCP commands with timestamps
- **Save** recorded sequences to files in a user-accessible directory
- **Playback** sequences with precise timing control
- **Query** playback status and timeline progress

This enhancement transforms Mr. Pumpkin from a real-time command server into a scriptable animation system. The feature set includes file management (list, upload, download, delete, rename) and playback control (play, stop, pause).

---

## Issue Analysis

### Requirements (from Issue #34)

#### Core Recording & Playback
- Record TCP commands with timestamps to capture command sequences
- Automatically group commands on a timeline for organized playback
- Save playback files in a user-accessible directory

#### TCP Command Set

**File Management Commands:**
- `list_recordings` — List available playback files
- `upload <filename> <data>` — Upload/create a playback file
- `download <filename>` — Download/retrieve a playback file
- `delete <filename>` — Remove a playback file
- `rename <old> <new>` — Rename a playback file

**Playback Control Commands:**
- `play <filename>` — Start playback of a recording
- `stop` — Stop current playback
- `pause` — Pause current playback (resume with `play`)

**Playback Query Commands:**
- `playback_status` — Query current playback state (playing/paused/stopped)
- `timeline_progress` — Get current position in timeline (e.g., "50% through")
- `sequence_duration` — Get total duration of current/specified sequence

---

## Current Architecture Context

### Existing Infrastructure

**Socket Server:**
- Currently single-threaded, processes one command per client connection
- Located in `pumpkin_face.py::_run_socket_server()` (lines 1074–1313)
- Handles: expressions, animations (blink, roll, wink), gaze, eyebrows, head movement, nose

**Command Protocol:**
- Text-based, line-oriented: `<command> [args...]`
- Case-insensitive parsing
- Examples: `happy`, `gaze 45 30`, `blink`, `turn_left 100`
- Current limitations:
  - No persistent state between connections
  - No timestamp metadata
  - No batch execution or timeline concept

**Application State:**
- Animation and expression state machine already exists
- Timing driven by pygame frame clock (`self.clock`)
- Frame-by-frame animation loop in `run()` method

**File System:**
- No existing file I/O for recordings
- Application launches from CLI with optional monitor/window args
- No designated "recordings" directory yet

---

## Architectural Decisions Required

### 1. Timeline File Format

**Decision Options:**

| Format | Pros | Cons | Recommendation |
|--------|------|------|-----------------|
| **JSON** (structured) | Human-readable, nested data, flexible | Larger files, slower parsing | ✅ Recommended |
| **CSV** (flat) | Simple, compact, easy to parse | Limited nesting, escaping issues | — |
| **Binary** (protobuf/pickle) | Compact, fast | Not human-readable, schema versioning | — |

**Proposed JSON Schema:**

```json
{
  "version": "1.0",
  "metadata": {
    "name": "sunset_sequence",
    "created_at": "2026-02-14T10:30:00Z",
    "duration_ms": 5000,
    "description": "5-second animation sequence"
  },
  "timeline": [
    {"t": 0, "command": "neutral"},
    {"t": 500, "command": "happy"},
    {"t": 1200, "command": "gaze 45 30"},
    {"t": 2000, "command": "blink"},
    {"t": 3500, "command": "sad"},
    {"t": 5000, "command": "sleep"}
  ]
}
```

**Rationale:**
- JSON is human-readable and debuggable
- Metadata supports future features (tags, categories, author)
- Timeline array is simple to iterate during playback
- Timestamps in milliseconds provide sub-second precision
- Schema versioning enables forward compatibility

### 2. Recording Storage Directory

**Decision Options:**

| Location | Pros | Cons |
|----------|------|------|
| `~/.mr-pumpkin/recordings/` | Standard user config pattern | Platform-specific paths |
| `./recordings/` (relative to app) | Simple, no path logic | Not portable, pollutes repo |
| User-specified (CLI flag) | Flexible | Requires config management |
| Cross-platform helper | Works everywhere | Additional dependency |

**Proposed Solution:**
Use `pathlib.Path.home() / '.mr-pumpkin' / 'recordings'`
- Cross-platform via pathlib
- Follows Unix conventions (hidden `~/.` directory)
- User-accessible without admin
- Can be customized via environment variable `MR_PUMPKIN_RECORDINGS`

### 3. Playback Execution Model

**Decision Options:**

| Model | Pros | Cons |
|-------|------|------|
| **Async (background thread)** | Non-blocking, allows new commands during playback | Complex state sync, race conditions |
| **Sync (blocking)** | Simple, deterministic timing | Blocks socket server, can't accept commands |
| **Event-driven (frame-based)** | Integrated with game loop, precise timing | Requires main loop refactor |

**Proposed Solution: Frame-Based (Event-Driven)**
- Integrate playback state machine into existing pygame loop
- On each frame: check if playback is active, advance timeline if so
- Execute commands that fall within the current frame's timestamp window
- Non-blocking to socket server; playback proceeds independently

**Rationale:**
- Leverages existing frame clock (already 60 FPS)
- Timing precision tied to render frames (good enough)
- No new threads needed
- Allows pausing/resuming without thread state complexity

### 4. Command Recording Strategy

**Decision Options:**

| Strategy | Pros | Cons |
|----------|------|------|
| **Implicit (auto-record on socket)** | Automatic capture | No user control, can't record keyboard |
| **Explicit (record start/stop command)** | User control, clear semantics | Extra commands, manual management |
| **Hybrid (record on demand)** | Flexible, can switch mid-stream | More complex |

**Proposed Solution: Explicit Explicit-Capture via Dedicated Commands**
- `record_start <name>` — Begin recording incoming commands with timestamp
- `record_stop` — Stop recording, save to file
- Timestamps captured at socket server layer (when command received)
- Store in in-memory buffer during recording, serialize to file on stop

**Rationale:**
- Users control what gets recorded
- Clear semantics match other applications
- Can easily add filtering (record only certain commands)
- Extensible to future features (pause recording, split sequences)

---

## Work Item Decomposition

### Scope: 5-8 focused work items suitable for Vi (Backend) and Mylo (Tester)

#### **WI-1: Core Timeline Data Structure & File I/O**

**Owner:** Vi (Backend)  
**Size:** M  
**Priority:** P0 (foundational)  
**Dependencies:** —

**Description:**
Create the timeline representation and file I/O layer:
- Define `Timeline` class: metadata + timeline array
- Implement JSON serialization/deserialization
- Create recordings directory with path resolution (`pathlib` + env var support)
- Implement file operations: `save(path)`, `load(path)`, `exists(path)`
- Add validation: timeline structure, timestamp monotonicity, command validity

**Success Criteria:**
- Load/save round-trip is lossless (serialize → deserialize → compare)
- Handles missing recordings gracefully (descriptive errors)
- Works on Windows/Linux/macOS via pathlib
- Supports environment variable override for recordings path

**Files to Create/Modify:**
- `timeline.py` (new) — Timeline class and file I/O
- Update `pumpkin_face.py` to use Timeline module

---

#### **WI-2: Socket Server Refactor for Recording & Playback States**

**Owner:** Vi (Backend)  
**Size:** M  
**Priority:** P0 (foundational)  
**Dependencies:** WI-1

**Description:**
Extend the socket server to support recording and playback states:
- Add `RecordingState` enum: `IDLE`, `RECORDING`, `PLAYBACK`, `PAUSED`
- Implement recording buffer: capture (timestamp, command) tuples during recording
- Add playback state manager: current timeline, position, elapsed time
- Refactor `_run_socket_server()` to route commands based on state
- Ensure no state corruption when recording, playback, and manual commands overlap

**Success Criteria:**
- Can start/stop recording without side effects
- Can load and start playback without losing state
- Commands received during playback are queued for later or rejected with clear message
- State transitions are logged (for debugging)

**Files to Modify:**
- `pumpkin_face.py` — Add state machine, refactor socket handler

---

#### **WI-3: Implement Playback Execution in Game Loop**

**Owner:** Vi (Backend)  
**Size:** M  
**Priority:** P0  
**Dependencies:** WI-1, WI-2

**Description:**
Integrate timeline playback into the main rendering loop:
- Add playback tick method called once per frame
- Calculate current timeline position based on elapsed time
- Execute all commands whose timestamp ≤ current frame time
- Support pause/resume (freeze elapsed time, don't execute commands)
- Gracefully handle playback end (auto-stop, reset to start)
- Ensure timing precision is within 16ms (60 FPS frame budget)

**Success Criteria:**
- Playback stays synchronized to frame clock (no drift)
- Commands execute at correct timestamps (within ±16ms)
- Pause freezes execution; resume continues from freeze point
- End-of-timeline is detected and playback stops cleanly
- Playback can be canceled mid-stream without hanging

**Files to Modify:**
- `pumpkin_face.py` — Main loop integration

---

#### **WI-4: TCP Commands - File Management (list, upload, download, delete, rename)**

**Owner:** Vi (Backend)  
**Size:** M  
**Priority:** P1  
**Dependencies:** WI-1

**Description:**
Implement file management TCP commands:
- `list_recordings` — Return JSON with available files (name, size, created_at, duration)
- `download <filename>` — Return file contents (raw JSON or encoded)
- `delete <filename>` — Remove file, confirm deletion
- `rename <old> <new>` — Rename file, validate new name
- `upload <filename> <data>` — Create/overwrite file (data is JSON timeline)
- Add input validation: filename sanitization (no path traversal), file size limits

**Success Criteria:**
- All commands parse correctly and handle edge cases
- File operations are atomic or fail with clear error messages
- List returns metadata in parseable format
- Upload validates JSON schema before accepting
- Deletes and renames check for existence first

**Files to Modify:**
- `pumpkin_face.py` — Add command handlers in socket server
- Potentially: `timeline.py` (add file list/metadata methods)

---

#### **WI-5: TCP Commands - Record Start/Stop**

**Owner:** Vi (Backend)  
**Size:** S  
**Priority:** P0  
**Dependencies:** WI-2

**Description:**
Implement recording commands:
- `record_start <name>` — Start capturing commands; allocate timestamp buffer
- `record_stop` — Stop capturing; save buffer to file with metadata
- Ensure timestamps are taken at command arrival (socket layer)
- Validate recording name (avoid collisions, sanitize filename)
- Handle edge cases: start while already recording (error), stop while idle (error)

**Success Criteria:**
- Record start/stop works without data loss
- Timestamps are accurate (millisecond precision)
- Recordings are saved to correct directory
- Clear error messages for invalid states
- Can record and immediately playback

**Files to Modify:**
- `pumpkin_face.py` — Add record handlers

---

#### **WI-6: TCP Commands - Playback Control (play, stop, pause) & Status Queries**

**Owner:** Vi (Backend)  
**Size:** M  
**Priority:** P0  
**Dependencies:** WI-3, WI-4, WI-5

**Description:**
Implement playback control and status commands:
- `play <filename>` — Load timeline and start playback
- `stop` — Stop playback and reset to start
- `pause` — Pause playback (freeze timeline position)
- `playback_status` — Return JSON: state (playing/paused/stopped), elapsed_ms, filename
- `timeline_progress` — Return percentage (0–100) or elapsed/total in human-readable format
- `sequence_duration` — Return total duration in milliseconds (or human-readable)

**Success Criteria:**
- Play loads file and starts playback
- Stop/pause state transitions work correctly
- Status queries return parseable JSON
- Duration queries work for active playback and queried files
- Error handling for missing/invalid files

**Files to Modify:**
- `pumpkin_face.py` — Add playback commands

---

#### **WI-7: Unit & Integration Tests (Mylo - Tester)**

**Owner:** Mylo (Tester)  
**Size:** L  
**Priority:** P0  
**Dependencies:** WI-1 through WI-6

**Description:**
Comprehensive test suite for timeline and playback:

**Unit Tests (timeline module):**
- Timeline creation, serialization (JSON round-trip)
- File save/load with various edge cases (empty, large, invalid JSON)
- Command validation within timeline
- Timestamp ordering and monotonicity

**Integration Tests (playback):**
- Record → save → load → playback flow (end-to-end)
- Playback timing accuracy (commands execute near correct timestamps)
- Pause/resume state transitions
- File management commands (list, delete, rename)
- Error handling: missing files, invalid JSON, corrupt recordings

**Socket-Level Tests:**
- Record start/stop via socket (multi-command sequences)
- Play/pause/stop state machine via socket
- Status/progress queries return correct format
- Concurrent: can query playback while recording? (should fail gracefully)

**Success Criteria:**
- 80%+ code coverage on timeline and playback modules
- All edge cases tested (empty files, large timelines, malformed input)
- Tests document expected behavior for future maintainers
- CI passes (pytest)

**Files to Create/Modify:**
- `tests/test_timeline.py` (new) — Timeline unit tests
- `tests/test_playback.py` (new) — Playback integration tests
- `tests/test_socket_recording.py` (new) — Socket-level recording/playback tests

---

#### **WI-8: Documentation & Examples**

**Owner:** Vi (Backend)  
**Size:** S  
**Priority:** P1  
**Dependencies:** WI-1 through WI-6

**Description:**
User-facing documentation and examples:
- Update README.md with playback feature overview
- Document timeline file format (JSON schema with example)
- Add usage examples:
  - Python: how to record via socket
  - Command-line: how to create/play sequences
  - Example playback file (e.g., "happy_sequence.json")
- Update `client_example.py` to include recording/playback examples
- Add CLI script: `record_sequence.py` for easy recording from terminal

**Success Criteria:**
- New users can understand the feature from README
- Example files are valid and tested
- Command formats documented
- CLI script works without requiring socket knowledge

**Files to Create/Modify:**
- `README.md` — Add playback section
- `client_example.py` — Add recording/playback examples
- `scripts/record_sequence.py` (new) — CLI recording helper
- Example file: `docs/example_sequences/happy_dance.json`

---

## Assumptions & Questions for Lead Approval

### Assumptions Made

1. **Timeline Format:** JSON is acceptable (human-readable, forward-compatible)
2. **Playback Timing:** Frame-based execution (60 FPS) is precise enough for this use case
3. **Recording Scope:** Only TCP commands are recorded (not keyboard input)
4. **File Storage:** `~/.mr-pumpkin/recordings/` is acceptable; users can override with env var
5. **Concurrency:** Recording/playback are mutually exclusive for this iteration (simplifies state)
6. **Command Execution:** Playback commands execute asynchronously (don't wait for completion)

### Questions for Clarification

1. **Multiple Playbacks:** Should users be able to run multiple timelines simultaneously, or is one active playback at a time sufficient?
   - *Impact:* Could spawn multiple playback threads if needed; affects WI-2, WI-3

2. **Recording Filtering:** Should users be able to selectively record (e.g., skip keyboard, only socket)? Or all commands?
   - *Impact:* Simple for socket-only; complicates if filtering needed

3. **Playback Speed Control:** Should playback speed be adjustable (1x, 2x, 0.5x)? Or fixed realtime?
   - *Impact:* Could add via `play <filename> <speed>` if desired; not in current scope

4. **File Organization:** Should recordings support subdirectories/folders? Or flat list?
   - *Impact:* Flat for WI-4; subdirectories would complicate file list/delete

5. **Command Validation During Playback:** If playback references an invalid command, should it skip or fail?
   - *Impact:* WI-6; currently propose: skip invalid, log warning

6. **Maximum Recording Size:** Should there be a limit on file size or timeline length?
   - *Impact:* WI-1, WI-4; propose: 10MB max per file, 100K commands max

7. **Undo for Recording:** If user starts recording, should there be a way to discard without saving?
   - *Impact:* WI-5; propose: `record_cancel` command

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **Timing Drift During Playback** | Medium | High | Frame-based execution; comprehensive timing tests (WI-7) |
| **File Corruption** | Low | High | Atomic writes, JSON validation on load (WI-1) |
| **Socket Server Blocking** | Medium | Medium | Playback in main loop (not socket thread); non-blocking design (WI-3) |
| **State Machine Complexity** | Medium | Medium | Clear state transitions; unit tests; logging (WI-2, WI-7) |
| **Large Timeline Performance** | Low | Medium | Benchmark with 10K+ commands; optimize if needed later |
| **Cross-Platform Path Issues** | Low | Medium | Use pathlib; test on Windows/Linux/macOS (WI-1) |

---

## Success Metrics

- ✅ Record/save/load/playback cycle works end-to-end
- ✅ Playback timing accurate within ±16ms (one frame)
- ✅ All 7 TCP command groups (file mgmt, record, playback control, status) functional
- ✅ 80%+ test coverage with clear documentation
- ✅ No socket server blocking or race conditions
- ✅ User can start pumpkin app and run playback sequence from example

---

## Next Steps (If Approved)

1. **User approval:** Confirm assumptions and answer clarification questions
2. **Assign work:** Distribute WI-1 through WI-8 to Vi and Mylo
3. **Parallel execution:** WI-1 (foundational) unblocks WI-2, WI-3, etc.
4. **Integration:** Scribe logs decisions and learnings as work proceeds
5. **Review gate:** Ralph monitors PR submissions and keeps work flowing

---

**Document Created By:** Jinx (Lead)  
**Ready for Implementation:** Pending user approval and answers to clarification questions
