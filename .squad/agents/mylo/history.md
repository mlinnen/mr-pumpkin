# Mylo history

## Learnings

- Added pytest skeletons covering expression transitions, rapid command sequences, invalid commands, and rendering timeouts.
- Recommended mocking pygame for unit tests and using SDL_VIDEODRIVER=dummy for CI headless runs.
- Ran pytest locally: tests executed but several failures/errors occurred (expected until the PumpkinFace API is adapted to tests). Next steps: adapt tests to the real API, implement pygame mocks, and add a CI headless integration job.
- Created branch `squad/99-mylo-tests` with initial test scaffolding (tests/), a headless CI workflow (.github/workflows/ci-tests.yml), and an inbox decision for Jinx (.squad/decisions/inbox/mylo-issue99.md).
- Added skipped test placeholders for: state transitions (tests/test_transitions.py), command handling (tests/test_commands.py), and recording/playback (tests/test_recording.py). These are intentionally skipped until APIs are stable.
- Implemented a lightweight pygame shim in tests/conftest.py to avoid import errors in environments without pygame.

Next actions
------------
- Implement concrete tests that instantiate PumpkinFace and assert state/animation correctness.
- Coordinate with Jinx to confirm CI environment support for pygame or to approve continued use of mocks.
- Expand CI to run integration tests under a headless display (xvfb) if needed.

