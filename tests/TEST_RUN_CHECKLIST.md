Test run checklist for CI (headless pygame strategy or mocking):

1. Prefer mocking pygame for unit tests where possible to avoid graphics dependencies.
2. For integration tests that require rendering, use a headless display:
   - On CI, set environment variable SDL_VIDEODRIVER=dummy before importing pygame.
   - Install xvfb or use pygame headless/backends as available.
3. Run pytest with -q and capture logs: pytest -q --maxfail=1
4. Fail the build on any unhandled exceptions, timeouts (>1s per render), or invalid state transitions.
5. If tests rely on real timing, use monkeypatch to control time.sleep or use fake timers to avoid flakiness.
