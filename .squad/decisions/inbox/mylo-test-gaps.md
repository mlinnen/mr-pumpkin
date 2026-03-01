# Test Coverage Gap: wiggle_nose Command Alias

**Filed by:** Mylo (Tester)  
**Date:** 2026-02-29  
**Priority:** P3 (Low)  
**Status:** New  

## Summary

The `wiggle_nose` command alias added in PR #51 (Issue #50) lacks dedicated test coverage.

## Details

**What's working:**
- `wiggle_nose` is implemented correctly in `command_handler.py` (lines 260-270)
- It functions as an alias for `twitch_nose`, calling `_start_nose_twitch(magnitude)`
- Accepts magnitude parameter: `wiggle_nose` or `wiggle_nose <magnitude>` (default: 50.0)
- Recording integration works (captures command if session active)
- Error handling in place (ValueError/IndexError for magnitude parsing)

**What's missing:**
- No explicit test coverage for `wiggle_nose` alias in test suite
- `twitch_nose` has 45 tests in `test_nose_movement.py` — `wiggle_nose` has 0 tests
- Grep search confirms: no test files mention `wiggle_nose`

**Risk level:**
- **Low** — Implementation shares code path with well-tested `twitch_nose`
- Regression risk only if alias-specific logic changes (e.g., different default magnitude)

## Recommendation

Add minimal test coverage in `test_nose_commands.py` or `test_nose_movement.py`:

```python
def test_wiggle_nose_alias_calls_twitch_nose():
    """wiggle_nose should function as alias for twitch_nose."""
    pumpkin = PumpkinFace()
    pumpkin._start_nose_twitch = Mock()
    
    command_handler = CommandHandler(pumpkin)
    command_handler.handle_command("wiggle_nose")
    
    pumpkin._start_nose_twitch.assert_called_once_with(50.0)  # default magnitude

def test_wiggle_nose_with_magnitude():
    """wiggle_nose should accept magnitude parameter."""
    pumpkin = PumpkinFace()
    pumpkin._start_nose_twitch = Mock()
    
    command_handler = CommandHandler(pumpkin)
    command_handler.handle_command("wiggle_nose 75.0")
    
    pumpkin._start_nose_twitch.assert_called_once_with(75.0)

def test_wiggle_nose_captured_in_recording():
    """wiggle_nose should be captured during recording sessions."""
    pumpkin = PumpkinFace()
    pumpkin.recording_session.is_recording = True
    pumpkin._capture_command_for_recording = Mock()
    
    command_handler = CommandHandler(pumpkin)
    command_handler.handle_command("wiggle_nose 60.0")
    
    pumpkin._capture_command_for_recording.assert_called_once_with("wiggle_nose 60.0")
```

## Effort

- **1-2 hours** to write and validate tests
- Add to existing `test_nose_commands.py` (or create if doesn't exist)
- No implementation changes needed

## Action Items

- [ ] Assign to Mylo for test creation
- [ ] Review by Jinx (Lead)
- [ ] Merge with PR #51 or create follow-up PR

## References

- Issue #50: Add wiggle_nose command alias
- PR #51: Implements wiggle_nose alias
- `command_handler.py`: Lines 260-270
- `test_nose_movement.py`: Existing nose animation tests (45 tests for twitch_nose/scrunch_nose)
