# TCP Protocol Specification — Timeline Recording & Playback
## Issue #34 Timeline Feature

**Author:** Jinx (Lead)  
**Date:** 2026-02-25  
**Status:** Design proposal (pending implementation)

---

## Overview

This document specifies the TCP command protocol for timeline recording/playback functionality. The design extends the existing text-based TCP command system (port 5000) with new timeline commands while maintaining full backward compatibility with expression/animation commands.

---

## Design Principles

1. **Backward compatibility:** All existing commands (expressions, blink, gaze, etc.) continue to work unchanged
2. **Text-based simplicity:** Consistent with existing command format (space-separated text)
3. **Non-blocking execution:** Timeline playback runs in background; commands return immediately
4. **Single active timeline:** Only one recording OR one playback active at a time
5. **Graceful error handling:** Invalid commands print error to console, don't crash server
6. **Flat response format:** JSON for structured data (status, file listings), plain text for confirmation/errors

---

## Command Grammar

### Recording Commands

```
record_start
  → Begins capturing all incoming commands with timestamps
  → Response: "OK Recording started"
  → Error if recording already active: "ERROR Recording already in progress"

record_stop [filename]
  → Stops recording and saves to file
  → filename: Optional. Auto-generated if omitted (format: "recording_YYYY-MM-DD_HHMMSS.json")
  → Response: "OK Saved to {filename}"
  → Error if not recording: "ERROR No active recording"
  → Error if no commands captured: "ERROR Cannot save empty recording"
  → Error if filename exists: "ERROR File already exists: {filename}"

record_cancel
  → Cancels active recording without saving
  → Response: "OK Recording cancelled"
  → Error if not recording: "ERROR No active recording"
```

**Examples:**
```
> record_start
< OK Recording started

> happy
[command captured with timestamp]

> blink
[command captured with timestamp]

> record_stop halloween_intro
< OK Saved to halloween_intro.json

> record_start
> gaze 0 0
> record_cancel
< OK Recording cancelled
```

---

### Playback Commands

```
play <filename>
  → Loads and starts playing timeline file
  → filename: Required. Auto-append ".json" if missing
  → Response: "OK Playing {filename} ({duration_ms}ms)"
  → Error if file not found: "ERROR File not found: {filename}"
  → Error if playback active: "ERROR Playback already active: {current_file}"
  → Error if invalid JSON: "ERROR Invalid timeline file: {filename}"
  → Error during playback if command fails: stops playback, prints error

pause
  → Pauses playback at current position
  → Response: "OK Paused at {position_ms}ms"
  → Error if not playing: "ERROR No active playback"
  → Error if already paused: "ERROR Already paused"

resume
  → Resumes playback from paused position
  → Response: "OK Resumed from {position_ms}ms"
  → Error if not paused: "ERROR Playback not paused"

stop
  → Stops playback and resets to beginning
  → Response: "OK Playback stopped"
  → Error if not playing: "ERROR No active playback"

seek <milliseconds>
  → Jumps to position in timeline (works during playback or paused)
  → milliseconds: Integer timestamp (0 to duration_ms)
  → Response: "OK Seeked to {milliseconds}ms"
  → Error if no timeline loaded: "ERROR No timeline loaded"
  → Error if out of range: "ERROR Seek position out of range (0-{duration_ms}ms)"
```

**Examples:**
```
> play halloween_intro
< OK Playing halloween_intro.json (5000ms)

> pause
< OK Paused at 2341ms

> seek 1000
< OK Seeked to 1000ms

> resume
< OK Resumed from 1000ms

> stop
< OK Playback stopped
```

---

### Status Query Commands

```
timeline_status
  → Returns current playback state as JSON
  → Response format:
    {
      "state": "stopped"|"playing"|"paused",
      "filename": "halloween_intro.json"|null,
      "position_ms": 2341,
      "duration_ms": 5000,
      "is_playing": true|false,
      "recording": true|false
    }
  → Always returns 200 (never errors)

recording_status
  → Returns current recording state
  → Response format:
    {
      "is_recording": true|false,
      "command_count": 42,
      "duration_ms": 3521
    }
  → Always returns 200 (never errors)
```

**Examples:**
```
> timeline_status
< {"state": "playing", "filename": "halloween_intro.json", "position_ms": 2341, "duration_ms": 5000, "is_playing": true, "recording": false}

> recording_status
< {"is_recording": true, "command_count": 12, "duration_ms": 4521}
```

---

### File Management Commands

```
list_recordings
  → Lists all timeline files in recordings directory
  → Response format (JSON array):
    [
      {
        "filename": "halloween_intro.json",
        "size_bytes": 1234,
        "created_at": 1708897200.0,
        "duration_ms": 5000
      },
      ...
    ]
  → Returns empty array [] if no recordings

delete_recording <filename>
  → Deletes a timeline file
  → filename: Required. Auto-append ".json" if missing
  → Response: "OK Deleted {filename}"
  → Error if file not found: "ERROR File not found: {filename}"
  → Error if currently playing: "ERROR Cannot delete file currently in playback"

rename_recording <old_name> <new_name>
  → Renames a timeline file
  → old_name, new_name: Required. Auto-append ".json" if missing
  → Response: "OK Renamed {old_name} to {new_name}"
  → Error if old file not found: "ERROR File not found: {old_name}"
  → Error if new name exists: "ERROR File already exists: {new_name}"
  → Error if currently playing old file: "ERROR Cannot rename file currently in playback"
```

**Examples:**
```
> list_recordings
< [{"filename": "recording_2026-02-25_143022.json", "size_bytes": 523, "created_at": 1708897200.0, "duration_ms": 3200}]

> delete_recording old_test
< OK Deleted old_test.json

> rename_recording recording_2026-02-25_143022 halloween_intro
< OK Renamed recording_2026-02-25_143022.json to halloween_intro.json
```

---

## Integration with Existing Commands

### Recording Mode Behavior

When `record_start` is active:
- **All incoming commands are captured** (expressions, blink, gaze, eyebrow, etc.)
- Commands execute normally AND get recorded with timestamps
- Manual commands sent during recording → captured in timeline
- Example:
  ```
  > record_start
  > happy           ← Executes AND records at t=0ms
  > blink           ← Executes AND records at t=1200ms
  > gaze 45 30      ← Executes AND records at t=2500ms
  > record_stop demo
  ```

### Playback Mode Behavior

When `play <file>` is active:
- **Manual commands pause playback** (playback state → PAUSED)
- Manual command executes immediately
- Playback remains paused until explicit `resume` or `stop`
- Rationale: Operator override should take control, not compete with timeline
- Example:
  ```
  > play demo
  [playback running...]
  > happy           ← Playback auto-pauses, happy executes immediately
  > timeline_status
  < {"state": "paused", "filename": "demo.json", ...}
  > resume          ← Continue playback from paused position
  ```

**Alternative (NOT chosen):** Queue manual commands after playback ends — rejected because operator expects immediate control.

**Alternative (NOT chosen):** Ignore manual commands during playback — rejected because operator loses manual override capability.

### Timeline Commands During Recording

- `play`, `pause`, `resume`, `stop`, `seek` → **Error: "Cannot control playback while recording"**
- `list_recordings`, `delete_recording`, `rename_recording` → **Allowed** (file management is safe)
- `timeline_status` → **Allowed** (query-only)

### Timeline Commands During Playback

- `record_start` → **Error: "Cannot start recording while playback active"**
- All other commands → **Allowed** (manual override pauses playback)

---

## Error Handling

### File Errors
- **File not found during play:** Print error, don't start playback
- **Invalid JSON during play:** Print error with JSON parsing details, don't start playback
- **File exists during save:** Print error, recording data preserved (user can retry with different name)

### State Conflicts
- **Recording already active:** `record_start` rejected
- **Playback already active:** `play` rejected (must `stop` first)
- **Invalid command during playback:** Timeline stops immediately, error printed to console
  - Example: Timeline contains `gaze 500 500` (out of range) → playback stops at that timestamp

### Invalid Arguments
- **Missing required arguments:** Print usage error
- **Invalid numeric arguments:** Print parse error with expected format
- **Filename with path separators:** Reject (security — flat directory only)

---

## Response Format Reference

### Success Responses (Plain Text)
```
OK <action description>
```

### Error Responses (Plain Text)
```
ERROR <error description>
```

### Structured Data Responses (JSON)
```json
{...}
```
or
```json
[...]
```

**Note:** No prefixes like "OK" for JSON responses — client detects format by first character (`{` or `[` = JSON, else text).

---

## Backward Compatibility Guarantee

All existing commands unchanged:
- Expression commands: `neutral`, `happy`, `sad`, `angry`, `surprised`, `scared`, `sleeping`
- Animation commands: `blink`, `wink_left`, `wink_right`, `roll_clockwise`, `roll_counterclockwise`
- Gaze commands: `gaze <x> <y>`, `gaze <lx> <ly> <rx> <ry>`
- Eyebrow commands: `eyebrow_raise`, `eyebrow_lower`, `eyebrow_reset`, `eyebrow <val>`, etc.
- Head movement: `turn_left`, `turn_right`, `turn_up`, `turn_down`, `center_head`
- Nose animation: `twitch_nose`, `scrunch_nose`, `reset_nose`
- Projection offset: `projection_reset`, `jog_offset <dx> <dy>`, `set_offset <x> <y>`

**Integration strategy:** Add new command handlers in `_run_socket_server()` before final `try: Expression(data)` fallback. Timeline commands checked explicitly, existing commands hit enum parsing last.

---

## Implementation Notes for Vi

### Code Structure
1. **Add timeline objects to PumpkinFace:**
   - `self.playback = Playback()` — playback engine instance
   - `self.recording = RecordingSession()` — recording session instance
   - Set command callback: `self.playback.set_command_callback(self._execute_timeline_command)`

2. **Integrate with game loop:**
   - In `update()`: Add `self.playback.update(dt_ms)` to execute timeline commands each frame

3. **Add command handlers in `_run_socket_server()`:**
   - Parse timeline commands before expression enum fallback
   - Call `self.playback.play()`, `self.recording.start()`, etc.
   - Handle errors with try/except, print to console

4. **Manual override logic:**
   - When non-timeline command received during playback: call `self.playback.pause()`
   - Recording capture: In each command handler, if `self.recording.is_recording`: call `self.recording.record_command(cmd, args)`

5. **Command callback implementation:**
   ```python
   def _execute_timeline_command(self, command: str, args: dict):
       """Execute command from timeline playback."""
       # Map timeline command format to existing methods
       # Example: command="set_expression", args={"expression": "happy"}
       #   → self.set_expression(Expression.HAPPY)
   ```

### Delta Time Calculation
- Current `update()` doesn't track delta time
- Timeline playback needs dt in milliseconds
- Add: `self.last_update_time = time.time()` at start of `update()`
- Compute: `dt_ms = (time.time() - self.last_update_time) * 1000`
- Pass to: `self.playback.update(dt_ms)`

### JSON Response Handling
- Current socket server prints strings to console (no client response)
- For timeline commands: Send response back to client socket
- Add: `client_socket.sendall(response.encode('utf-8') + b'\n')`
- Format: JSON responses as-is, text responses with "OK" or "ERROR" prefix

---

## Open Questions / Design Decisions for Review

### 1. Response Channel
**Current behavior:** Socket server accepts commands but doesn't send responses to client (all output goes to console).

**Proposed change:** Timeline commands send responses back over socket (JSON or text).

**Question:** Should ALL commands start sending responses, or only timeline commands?
- **Option A:** Only timeline commands (status, list, etc.) → minimal change
- **Option B:** All commands send "OK" or error → consistency

**Recommendation:** Option A (timeline-only responses) — less disruption to existing client_example.py.

### 2. Manual Command During Playback
**Current design:** Manual command during playback → auto-pause playback.

**Alternative:** Manual command queued, executed after playback ends.

**Question:** Is auto-pause the right behavior?

**Recommendation:** Yes — operator expects immediate control. If they want timeline to continue, they shouldn't send manual commands.

### 3. Recording Expression vs Command Format
**Current behavior:** Expressions sent as strings (`"happy"`), parsed to enum.

**Recording format:** Should timeline store:
- **Option A:** Original command string (`"happy"`) — matches wire format
- **Option B:** Normalized command + args dict (`{"command": "set_expression", "args": {"expression": "happy"}}`) — explicit

**Current implementation:** timeline.py uses Option B (command + args dict).

**Implication:** Need mapping layer from TCP string → command dict during recording, and dict → method call during playback.

**Recommendation:** Keep Option B — more robust for complex commands like `gaze 45 30 50 35`.

### 4. Filename Restrictions
**Security consideration:** Filenames with `../` could escape recordings directory.

**Proposed validation:** Reject filenames containing `/` or `\` characters.

**Implementation:** Add check in file management commands before passing to Timeline classes.

---

## Example Session

```
# Start recording a sequence
> record_start
< OK Recording started

> neutral
[executes and records at t=0ms]

> gaze 0 0
[executes and records at t=500ms]

> happy
[executes and records at t=1200ms]

> blink
[executes and records at t=2300ms]

> record_stop greeting
< OK Saved to greeting.json

# List available recordings
> list_recordings
< [{"filename": "greeting.json", "size_bytes": 342, "created_at": 1708897200.0, "duration_ms": 2300}]

# Play it back
> play greeting
< OK Playing greeting.json (2300ms)
[timeline executes: neutral at 0ms, gaze at 500ms, happy at 1200ms, blink at 2300ms]

# Check status mid-playback
> timeline_status
< {"state": "playing", "filename": "greeting.json", "position_ms": 1450, "duration_ms": 2300, "is_playing": true, "recording": false}

# Pause playback
> pause
< OK Paused at 1523ms

# Seek to beginning
> seek 0
< OK Seeked to 0ms

# Resume from beginning
> resume
< OK Resumed from 0ms

# Manual override during playback
> sad
[playback auto-pauses, sad expression executes immediately]
< OK Paused at 1102ms (auto-paused by manual command)

# Resume playback
> resume
< OK Resumed from 1102ms

# Stop playback
> stop
< OK Playback stopped

# Rename file
> rename_recording greeting welcome_sequence
< OK Renamed greeting.json to welcome_sequence.json

# Clean up
> delete_recording welcome_sequence
< OK Deleted welcome_sequence.json
```

---

## Summary

This protocol design:
- ✅ Maintains full backward compatibility with existing commands
- ✅ Uses simple text-based command format (consistent with current system)
- ✅ Provides operator control via manual override (auto-pause during playback)
- ✅ Enables recording any sequence of existing commands
- ✅ Returns structured data (JSON) for status queries and file listings
- ✅ Handles errors gracefully without crashing socket server
- ✅ Supports non-blocking playback (runs in game loop background)
- ✅ Enforces single-file-at-a-time constraint (per issue #34 spec)

**Next step:** Vi implements integration in pumpkin_face.py using timeline.py classes.
