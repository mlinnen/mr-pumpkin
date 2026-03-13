---
date: 2026-03-13
owner: Vi
subject: Raspberry Pi dependency planning helper for lifecycle scripts
issue: 92
---

## Context

Issue #92 required Raspberry Pi-aware dependency installation without regressing the existing Unix release flow. The repository ships a release ZIP, so both `install.sh` and `update.sh` need the same dependency split logic and the packaged archive must include any new helper that those scripts depend on.

## Decision

Use a shared helper, `scripts/unix_dependency_plan.py`, to classify Raspberry Pi dependencies into:

1. **apt-managed packages** currently mapped to `python3-pygame`, `python3-websockets`, and `python3-mutagen`
2. **pip-managed packages** for everything else, preserving requirement specifiers

`install.sh` applies the apt-first strategy directly on Raspberry Pi. `update.sh` uses the same plan, but only performs apt installs when root or passwordless sudo is already available; otherwise it logs a warning and falls back to pip so unattended cron-style updates do not hard-fail on privilege prompts.

## Why

- **Single source of truth:** The planner avoids drifting package maps between install and update paths.
- **Pi compatibility:** Known Raspberry Pi OS packages move off the problematic pip path.
- **Release safety:** Because `scripts/package_release.py` whitelists files, the helper must be explicitly packaged and tested.
