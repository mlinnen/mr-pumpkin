# Mylo history

## Learnings

- Added pytest skeletons covering expression transitions, rapid command sequences, invalid commands, and rendering timeouts.
- Recommended mocking pygame for unit tests and using SDL_VIDEODRIVER=dummy for CI headless runs.
- Ran pytest locally: tests executed but several failures/errors occurred (expected until the PumpkinFace API is adapted to tests). Next steps: adapt tests to the real API, implement pygame mocks, and add a CI headless integration job.
