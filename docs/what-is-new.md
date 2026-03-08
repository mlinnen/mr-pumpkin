---
layout: page
title: What's New
permalink: /what-is-new
description: Full release history — every version's added features, fixes, and changes.
---

# What's New in Mr. Pumpkin

All notable changes to Mr. Pumpkin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.14] - 2026-03-08

### Added
- **OpenAI provider** — Added OpenAI as an alternative provider for audio analysis and timeline generation (previously only Gemini was supported). PR #82.
- **`--model` and `--api-key` CLI parameters** for `lipsync_cli.py` — Users can now specify the model and API key directly on the command line instead of relying solely on environment variables. (Issue #77, PR #83)

### Fixed
- Lipsync pipeline fixes — Fixed duration calculation, timing alignment, phoneme mapping, and audio sync bugs in the lipsync pipeline.
- **GitHub Pages no longer deploys from the preview branch** — The `squad-docs.yml` workflow was incorrectly triggering a GitHub Pages deployment on every push to `preview`. It now only deploys from `main`. (Issue #78, PR #84)

---

## [0.5.13] - 2026-03-06

### Added
- Audio lip-sync recording tool (Issue #66) — analyze an audio file with Google Gemini and automatically generate a timeline with mouth viseme commands timed to speech.
  - `skill/lipsync_cli.py` — new CLI: `python -m skill.lipsync_cli audio.mp3 --filename my_recording`
  - `skill/audio_analyzer.py` — `GeminiAudioProvider` uploads audio to the Gemini File API, extracts per-word timing and emotion in two passes
  - Auto-generated timeline contains expression commands (from detected emotion) and mouth viseme commands (`mouth_open`, `mouth_wide`, `mouth_rounded`, `mouth_closed`, `mouth_neutral`) timed to individual words
  - Audio file is uploaded to the pumpkin server alongside the timeline — playback is fully synchronized
  - Supports `.mp3`, `.wav`, `.ogg`, `.m4a`, `.aac`, `.flac` for analysis; warns with `ffmpeg` hint for formats pygame cannot play back
  - `--dry-run` mode for preview without upload

### Fixed
- Gemini SDK v1.x API changes: `files.upload()` kwarg and `.uri` vs `.name` for `Part.from_uri()` calls in `audio_analyzer.py`
- Mouth viseme commands wired into `_execute_timeline_command()` in `pumpkin_face.py` (were in vocabulary but not dispatched during timeline playback)
- `wiggle_nose` timeline playback dispatch fixed (now aliases to `_start_nose_twitch`)
- `upload_audio` handlers in `pumpkin_face.py` and `timeline.py` now accept `.m4a`, `.aac`, `.flac`

---

## [0.5.12] - 2026-03-05

### Added
- Squad v0.8.20 upgrade — 12 new GitHub Actions workflow templates for squad automation (CI gating, label enforcement, branch protection, issue assignment, triage, preview/promotion/release pipelines, and label sync)
- `squad.config.ts` — project-level Squad configuration covering model tiers, routing rules, casting universe allowlist, and platform settings
- Blog post: *"Built With Squad: An Entire Creative Coding Project Delivered by an AI Team"* — the full development story of Mr. Pumpkin, including how parallel fan-out, reviewer gates, and persistent agent memory shaped the project. See [blog](/blog) for the full post.
- `docs/development-story.md` — narrative of how Mr. Pumpkin was built by the AI team, covering architectural milestones and squad collaboration patterns
- Updated squad identity, casting state, and project-conventions skill with session learnings

### Fixed
- `mouth_wide` viseme shape refined: increased grin upturn, curved arc distinct from neutral mouth, corrected width
- Documentation site blog listing broken due to missing `index.html` required by jekyll-paginate
- CI: added `x86_64-linux` platform to `Gemfile.lock` to resolve Linux build failures
- Docs site nav layout: corrected search bar width overflow and mobile hamburger menu display (#61, #62)

---

## [0.5.11] - 2026-03-04

### Added
- Mouth speech control (Issue #59) — independent viseme-based mouth animation orthogonal to face expressions. Send viseme commands at ~20Hz from audio analysis to drive lip sync.
  - 5 viseme shapes: `closed` (M/B/P sounds), `open` (AH/AA sounds), `wide` (EE/IH sounds), `rounded` (OO/OH sounds), `neutral` (releases back to expression-driven mouth)
  - 6 commands: `mouth_closed`, `mouth_open`, `mouth_wide`, `mouth_rounded`, `mouth_neutral`, and `mouth <viseme>` (parameterized form)
  - Smooth animated transitions between shapes at configurable speed
  - See [Timeline Schema](timeline-schema.md#mouth-speech-control) for full command reference.

---

## [0.5.10] - 2026-03-03

### Added
- Recording chaining via `play_recording` command (issue #55) — embed one recording inside another using stack-based nested playback; maximum nesting depth is 5 levels. See [Timeline Schema](timeline-schema.md#recording-chaining) for details.
- `help` command over TCP and WebSocket (issue #56) — returns a plain-text listing of all available commands with syntax; safe to call at any time including during timeline playback.

---

## [0.5.9] - 2026-03-02

### Added
- `docs/what-is-new.md` — full release history page linked from `docs/index.md`
- `docs/timeline-schema.md` — full reference for timeline JSON format, command vocabulary, and timing rules

### Fixed
- CI release workflow now extracts the current version's CHANGELOG section as the release notes body; falls back to `--generate-notes` if no entry found
- CI release workflow now patches pre-existing GitHub releases with updated notes via `gh release edit`
- CI release notes now correctly diff from the previous semver tag using `--notes-start-tag`

---

## [0.5.8] - 2026-03-02

### Added
- AI-powered recording skill (`skill/` package) — describe an animation in plain English and have it generated and uploaded automatically using Google Gemini
  - `skill/cli.py` — command-line interface (`python -m skill "make the pumpkin look confused"`)
  - `skill/generator.py` — LLM-backed timeline generation with pluggable provider interface
  - `skill/uploader.py` — TCP upload client with dry-run and validation support
  - `skill/timing_guidelines.md` — LLM-facing timing reference used during generation
- `docs/recording-skill.md` — user guide for the recording skill
- `docs/timeline-schema.md` — full reference for the timeline JSON format, command vocabulary, and timing rules
- Linked both new docs from `docs/index.md`

### Fixed
- TCP upload deadlock on Windows loopback — Nagle's algorithm was batching the JSON payload and `END_UPLOAD` sentinel into one TCP segment, causing the server's `recv` loop to miss the sentinel. Fixed with a line-buffered accumulation loop in `pumpkin_face.py`
- CI release workflow now handles pre-existing GitHub release tags — uses `gh release upload --clobber` instead of failing on duplicate `gh release create`
- CI release notes now correctly diff from the previous semver tag (not the previous tag on `main`) using `--notes-start-tag`

---

## [0.5.7] - 2026-03-03

### Added
- Expanded documentation coverage with WebSocket examples and detailed integration guide
- End-user documentation suite in `docs/` folder
  - `docs/index.md` — documentation hub and quick-start guide
  - `docs/installation.md` — running Mr. Pumpkin as a system service (Linux systemd, Windows Task Scheduler/NSSM)
  - `docs/building-a-client.md` — comprehensive client integration guide with TCP and WebSocket protocols, full command reference, Python/Node.js/C# examples, timeline format, and troubleshooting

## [0.5.6] - 2026-03-02

### Added
- End-user documentation in `docs/` folder (issue #53)
  - `docs/index.md` — documentation hub and quick-start guide
  - `docs/installation.md` — running Mr. Pumpkin as a system service (Linux systemd, Windows Task Scheduler/NSSM)
  - `docs/building-a-client.md` — comprehensive client integration guide with TCP and WebSocket protocols, full command reference, Python/Node.js/C# examples, timeline format, and troubleshooting

---

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
