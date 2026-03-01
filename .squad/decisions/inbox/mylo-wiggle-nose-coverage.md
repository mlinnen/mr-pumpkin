# Decision: wiggle_nose Test Coverage Complete

**Date:** 2026-03-01  
**Decider:** Mylo (Tester)  
**Status:** ✅ Implemented  
**Related:** PR #51, Issue #50, branch `squad/50-nose-wiggle-reset`

## Context

The `wiggle_nose` command was added by Jinx as a user-friendly alias for `twitch_nose` in PR #51. However, the implementation had ZERO dedicated test coverage for the alias itself, creating a regression risk if the alias logic ever changed independently.

**Test coverage gap identified:**
- `twitch_nose`: 45+ comprehensive tests in `test_nose_movement.py`
- `scrunch_nose`: 45+ comprehensive tests in `test_nose_movement.py`
- `wiggle_nose`: 0 tests (gap!)

## Decision

Created comprehensive test suite `test_wiggle_nose_alias.py` with 21 tests covering:

1. **Command recognition** (5 tests)
   - Router recognizes wiggle_nose
   - Default magnitude (50)
   - Custom magnitude parameter
   - Case insensitivity

2. **Alias equivalence** (3 tests)
   - Behavioral parity with twitch_nose (no params)
   - Behavioral parity with twitch_nose (with magnitude)
   - Same internal method call verification

3. **Edge cases** (8 tests)
   - Invalid magnitude graceful degradation
   - Negative/zero magnitude handling
   - Extra parameters ignored
   - Non-interrupting behavior (already twitching)
   - Cross-animation blocking (during scrunch)
   - Reset and re-wiggle workflow

4. **Recording integration** (3 tests)
   - Command captured during recording (xfail - bug found)
   - Magnitude preserved in recording (xfail - bug found)
   - Not captured when not recording (pass)

5. **Parameter parsing** (4 tests)
   - Float values, large values, whitespace variations, empty params

## Test Results

**19 passed, 2 xfail** (expected failures)

The two xfail tests document a discovered bug: `wiggle_nose` is not included in the `_capture_command_for_recording()` whitelist in `pumpkin_face.py` (lines 1211-1228). This means wiggle_nose works correctly but won't be captured in timeline recordings.

## Consequences

✅ **Benefits:**
- wiggle_nose alias now has explicit test coverage
- Regression protection if alias logic changes
- Bug discovered: recording capture missing for wiggle_nose
- Test suite serves as documentation of expected behavior

⚠️ **Limitations:**
- Two recording tests marked xfail until Jinx fixes the recording capture bug
- Implementation fix needed: add wiggle_nose to recording whitelist (identical to twitch_nose logic)

🔧 **Follow-up needed:**
- Jinx should add wiggle_nose handling to `_capture_command_for_recording()`
- After fix, remove `@pytest.mark.xfail` from two recording tests
- Verify all 21 tests pass without xfail markers

## Implementation

**File:** `tests/test_wiggle_nose_alias.py`  
**Commit:** c29b23d  
**Branch:** `squad/50-nose-wiggle-reset`  
**Lines:** 362 lines, 21 tests

## Test Coverage Gap: CLOSED ✅

The wiggle_nose command alias now has comprehensive test coverage. The gap is closed, though two tests are marked xfail pending a bug fix in the recording capture logic.
