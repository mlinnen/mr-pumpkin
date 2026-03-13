---
date: 2026-03-13
owner: Jinx
subject: Raspberry Pi updater remains least-privilege by default
issue: 92
pr: 93
---

## Decision

Keep the Raspberry Pi hybrid dependency split, but restore `update.sh` to a non-root, cron-safe default.

## What that means

1. `install.sh` continues to use `apt` for the Raspberry Pi OS-managed Python packages (`python3-pygame`, `python3-websockets`, `python3-mutagen`) and `pip` for the remaining PyPI-only dependencies.
2. `update.sh` does not auto-run `apt-get` just because root or passwordless sudo is available.
3. On Raspberry Pi, the default update path refreshes only the pip-managed subset and logs guidance for the apt-managed packages.
4. APT refresh during update is allowed only behind an explicit opt-in environment variable: `MR_PUMPKIN_ALLOW_PI_APT_UPDATE=1`.

## Why

- The updater is designed for unattended execution, especially from cron, so its safe default must not depend on privilege escalation or passwordless sudo.
- Raspberry Pi dependency pain is real, but it belongs primarily to install-time bootstrap, not silent ongoing system package management during application updates.
- An explicit opt-in preserves flexibility for operators who do want the updater to touch apt-managed packages, without rewriting the contract for everyone else.
