# Decision Inbox — Nose Command Alias Pattern

**Author:** Jinx (Lead)  
**Date:** 2026-02-27  
**Issue:** #50  
**Status:** Implemented  

## Context

README.md documented a `wiggle_nose` command (line 280) but the actual implementation only had `twitch_nose` and `scrunch_nose` commands. The issue requested adding `wiggle_nose` and verifying `reset_nose` was handled.

## Investigation

- `wiggle_nose` existed ONLY in documentation, not in code
- `twitch_nose` was the actual implementation calling `_start_nose_twitch(magnitude)`
- `reset_nose` was already properly implemented in command_handler.py
- Public methods (`twitch_nose()`, `reset_nose()`) are zero-parameter wrappers
- Command handler calls private methods when parameter passing needed

## Decision

**Implemented `wiggle_nose` as a command alias for `twitch_nose`.**

Both commands route to the same underlying `_start_nose_twitch(magnitude)` method with identical behavior. This maintains backward compatibility for any users expecting `twitch_nose` while fulfilling the documented `wiggle_nose` API.

## Rationale

1. **Documentation-first commitment:** README.md is user contract; code should match what's documented
2. **Avoid breaking changes:** Keep `twitch_nose` functional for existing users/scripts
3. **Semantic clarity:** "wiggle" is more user-friendly than "twitch" for general audiences
4. **Implementation simplicity:** Alias pattern is 12 lines, no new state or methods needed
5. **Consistency:** Matches existing pattern where multiple command names can trigger same behavior

## Implementation

Added handler in `command_handler.py` before `twitch_nose`:

```python
if data == "wiggle_nose" or data.startswith("wiggle_nose "):
    if self.pumpkin.recording_session.is_recording:
        self.pumpkin._capture_command_for_recording(data)
    try:
        parts = data.split()
        magnitude = float(parts[1]) if len(parts) > 1 else 50.0
        self.pumpkin._start_nose_twitch(magnitude)
        print(f"Wiggling nose (magnitude={magnitude})")
    except (ValueError, IndexError) as e:
        print(f"Error parsing wiggle_nose command: {e}")
    return ""
```

## Alternatives Considered

1. **Remove wiggle_nose from README:** Rejected. Documentation exists, likely users depend on it.
2. **Deprecate twitch_nose:** Rejected. No reason to break existing functionality.
3. **Add wiggle as distinct animation:** Rejected. Scope creep, twitch already provides wiggle behavior.

## Follow-up Actions

- [x] Add `wiggle_nose` command handler
- [x] Verify `reset_nose` already works
- [x] Create PR #51 with fix
- [x] Document pattern in `.squad/skills/command-routing-pattern/SKILL.md`

## Review Recommendation

**APPROVE.** This is a minimal, non-breaking change that resolves documentation/implementation mismatch. No architectural implications. Suggested routing: Auto-approve or quick review by Vi (backend owner).
