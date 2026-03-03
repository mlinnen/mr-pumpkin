# Decision: Help Command Test Strategy (Issue #56)

**By:** Mylo (Tester)  
**Date:** 2026-03-04  
**Issue:** #56 — Add `help` command over TCP/WebSockets

## Decision

Tests were written as provisional (against expected interface) but Vi had already landed the implementation. All 28 tests pass immediately.

## Test Strategy Choices

**Plain-text vs JSON:** The `help` command returns structured plain text, not JSON. Tests use a `_try_parse_json()` helper that allows the JSON-specific test to skip gracefully when the response is plain text. This keeps tests forward-compatible if the format ever changes to JSON.

**Flexibility in syntax-hint detection:** Rather than hard-coding exact syntax strings, tests check for any of several syntax indicators (`<`, `[`, `filename`, `ms`, `angle`, etc.). This avoids brittle tests that break on minor formatting changes.

**"PROVISIONAL" comments retained:** Even though Vi's implementation was present when tests ran, the `# PROVISIONAL` comment pattern documents that tests were designed against an expected interface — useful for future reference.

**State immutability:** Added `test_help_does_not_change_pumpkin_state` to guard against accidental side effects (e.g., help accidentally triggering a recording or expression change).

## No Architectural Changes Required

The `help` command fits naturally into the existing `CommandRouter.execute()` dispatch pattern. No new infrastructure needed.
