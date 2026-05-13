# Mylo: Issue #99 — Test Suite Migration

Summary
-------
Created initial test scaffolding for state transitions, command handling, and recording/playback. Added a CI workflow to run pytest in a headless environment.

Blockers / Requested infra changes (for Jinx)
-------------------------------------------
- CI must set SDL_VIDEODRIVER=dummy (already set in the workflow), and runner may need SDL libs if pygame is installed.
- Recommend mocking or removing pygame usage from unit tests; if pygame is required in CI, install dependencies (e.g., libasound2, libsdl2-dev) or use xvfb.
- Consider adding a lightweight pygame dev dependency pinned to a known-working version for CI.
- Provide a test-run user or runner with display/headless support if we need integration tests that exercise rendering.

Next steps
----------
- Implement the skipped tests to exercise the real PumpkinFace API.
- Add pygame mocks and/or fixtures to emulate timing and events.
- Iterate on CI matrix to add Windows/macOS runners if platform-specific behavior is required.
