# Changelog

All notable changes to Mr. Pumpkin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.5] - 2026-03-02

### Added
- `update.sh` (Linux/macOS/Raspberry Pi) and `update.ps1` (Windows) auto-update scripts
- 5-phase update workflow: check version → download → stop → deploy → restart
- GitHub API version check with `gh` CLI preferred, direct URL download fallback
- Process detection via command line pattern match — preserves original launch arguments
- Graceful stop with SIGTERM/Stop-Process, 5s timeout, force kill fallback
- ZIP validation before overwriting files; logs all operations to `mr-pumpkin-update.log`
- Suitable for cron job (Linux/Pi) or Windows Task Scheduler scheduling
- `docs/auto-update.md` — detailed platform setup guide
- README Auto-Update section with cron/Task Scheduler examples

---

## [0.5.4] - 2026-03-01

### Fixed
- `upload_timeline` now works correctly from the WebSocket test client — WebSocket clients send
  filename and JSON inline in a single message, but the handler was routing through command_router
  which returned a TCP-only `UPLOAD_MODE` stub. `_ws_handler` now intercepts `upload_timeline`
  directly and calls `file_manager.upload_timeline()` to save the file.

---

## [0.5.3] - 2026-03-01

### Added
- `wiggle_nose` command: alias for nose twitch animation, callable from TCP client
- `wiggle_nose` added to timeline recording capture whitelist
- 21 test cases covering `wiggle_nose` command routing, alias equivalence, and recording integration

---

## [0.5.2] - 2026-03-01

### Fixed
- Expression commands now work correctly from TCP client — resolved Python `__main__` vs module
  name circular import issue where `command_handler.py` imported `Expression` as a second class
  instance, causing enum equality checks to silently fail
- Happy and sad mouth curves were visually swapped — corrected sine curve sign in `_get_mouth_points`
  (pygame Y increases downward; smile needs `+`, frown needs `-`)
- TCP recv deadlock in `client_example.py` — added `socket.shutdown(SHUT_WR)` after send so the
  server's blocking `recv()` unblocks for no-response commands (blink, roll, gaze, etc.)

---

## [0.5.1] - 2026-03-01

### Added
- Version management via VERSION file for centralized version control

### Changed
- Replaced hardcoded version string with dynamic version loading from VERSION file
- Squad upgraded from v0.5.3 to v0.5.4

---

## [0.5.0] - 2026-02-27

### 🎃 Major Features

**WebSocket Dual-Protocol Support**
- Added WebSocket server on port 5001 running parallel to TCP server (port 5000)
- Both protocols share unified CommandRouter for protocol-agnostic command execution
- Browser client support via standard JavaScript WebSocket API
- Zero breaking changes — fully backward compatible with existing TCP clients

### Added

- **WebSocket Server**: Asyncio-based WebSocket server runs in daemon thread alongside TCP server
- **CommandRouter**: Extracted 660-line command routing logic into shared `command_handler.py` module
- **Browser Test Client**: `websocket-test-client.html` for interactive WebSocket validation
  - Connection status monitoring with automatic fallback
  - Quick test buttons for common commands
  - Timeline upload testing (multi-line JSON)
  - Full event logging with timestamps
- **Integration Tests**: 27 comprehensive tests validating dual-protocol behavior
  - Identical response verification across protocols
  - Protocol switching and concurrent command execution
  - Error handling consistency
  - State synchronization (recordings, playback, expressions)
  - Connection resilience and large payload handling
  - Stress testing (50 rapid alternating commands)

### Architecture

**Milestone Implementation**:
- **M1**: Command router extraction (660-line refactor, 403/403 tests passing)
- **M2**: WebSocket server setup (asyncio daemon thread, port 5001)
- **M3**: Browser test client (HTML/JS validation tool)
- **M4**: Integration testing (27 comprehensive test scenarios)
- **M5**: Production release (v0.5.0 tagging and documentation)

### Performance

- **Zero Regressions**: All 403 existing tests continue to pass
- **New Test Coverage**: 430 total tests (403 existing + 27 new integration tests)
- **Sub-millisecond Overhead**: Command routing overhead negligible
- **Concurrent Client Support**: Multiple TCP and WebSocket clients simultaneously

### Documentation

- Updated README with complete WebSocket usage examples
- Documented all 27 integration test scenarios
- Added browser test client documentation
- Installation instructions unchanged (no new dependencies beyond `websockets` package)

### Breaking Changes

**None** — This release is fully backward compatible. Existing TCP clients work without modification.

### Upgrade Path

No migration required. Simply update to v0.5.0:

```bash
git pull origin main
pip install -r requirements.txt  # Installs websockets package
python pumpkin_face.py           # Both TCP and WebSocket servers start automatically
```

### Contributors

- **Vi**: Backend architecture (CommandRouter extraction, WebSocket server implementation)
- **Mylo**: Integration test suite (27 comprehensive test scenarios, browser client validation)
- **Jinx**: Milestone coordination, architectural review, release management

---

## [0.4.1] - 2026-02-26

### Added
- Recording file upload with validation (#44)
- Download timeline command handler
- Playback controls and recording/list bug fixes (#42)

### Changed
- Systematic race condition delays in recording tests
- Updated documentation for recording file structure

### Fixed
- Recording upload validation
- Playback control edge cases

---

## Earlier Versions

See git history for releases prior to 0.4.1.
