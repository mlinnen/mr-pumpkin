# Decision: Command Aliases Require Dual Whitelisting for Recording Integration

**Date:** 2026-02-27  
**Decider:** Jinx (Lead)  
**Status:** Accepted  
**Context:** Issue #50 (wiggle_nose alias recording capture bug)

## Problem

The `wiggle_nose` command was added as an alias in `command_handler.py` but was not captured during timeline recording sessions. The command executed correctly but was silently dropped from recordings, making recorded timelines incomplete.

## Root Cause

Command execution and recording capture are separate architectural layers:
- **Command Router** (`command_handler.py`): Routes command strings to PumpkinFace methods
- **Recording Capture** (`pumpkin_face.py`): Whitelists commands for timeline recording

Adding a command alias to the router does NOT automatically whitelist it for recording. The two systems must be synchronized manually.

## Decision

**Command aliases must be explicitly added to BOTH layers:**

1. **Command Router** (`command_handler.py`): Map alias to execution method
2. **Recording Capture** (`pumpkin_face.py` lines 1211+): Add elif branch with identical parameter parsing

**Pattern for magnitude-based nose commands:**
```python
elif cmd == "wiggle_nose":
    magnitude = 50.0
    if len(parts) >= 2:
        try:
            magnitude = float(parts[1])
        except ValueError:
            pass
    self.recording_session.record_command(cmd, {"magnitude": magnitude})
```

## Consequences

**Positive:**
- Explicit whitelisting provides control over which commands are recordable
- Prevents accidental recording of debug/meta commands
- Clear separation between execution and persistence concerns

**Negative:**
- Manual synchronization required when adding command aliases
- Risk of forgetting to update both locations (as happened with `wiggle_nose`)
- Duplicate parameter parsing logic in both layers

## Alternatives Considered

1. **Auto-capture all executed commands**: Rejected - would record debug commands, infinite loops, meta-commands
2. **Shared command registry**: Rejected - adds complexity, tight coupling, no clear benefit for current 20-command vocabulary
3. **Decorator-based whitelisting**: Rejected - requires refactoring command execution architecture

## Validation

- All 21 `test_wiggle_nose_alias.py` tests pass (including 2 recording integration tests)
- Full test suite: 410 passed, 41 failed (failures are pre-existing TCP integration timeouts, unrelated to this change)
- `wiggle_nose` now captured correctly with default and custom magnitude parameters

## Implementation Notes

When adding future command aliases:
1. Add command to router (`command_handler.py`)
2. Add command to recording capture whitelist (`pumpkin_face.py`)
3. Write tests for both execution AND recording integration
4. Use xfail markers if recording capture is not yet implemented (enables TDD workflow)

## Related

- Issue #50: Nose Wiggle Command Handler & Recording Capture
- File: `pumpkin_face.py` (lines 1211-1228)
- File: `command_handler.py` (wiggle_nose alias)
- Tests: `tests/test_wiggle_nose_alias.py` (TestWiggleNoseRecordingIntegration class)
