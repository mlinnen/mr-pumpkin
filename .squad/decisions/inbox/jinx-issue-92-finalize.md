# Jinx — Issue #92 finalization

## Decision

Keep Raspberry Pi unattended updates non-root by default: `update.sh` must skip apt-managed dependency refresh unless `MR_PUMPKIN_ALLOW_PI_APT_UPDATE=1` is explicitly set, and Unix shell scripts should stay LF-terminated in git so the updater remains valid on Raspberry Pi and other Unix hosts.

## Why

- `install.sh` can own the apt-managed package setup on Raspberry Pi because first-time install is already the bootstrap step that may require elevated privileges.
- `update.sh` is part of the unattended maintenance path, so its default behavior must remain cron-safe and password-prompt free.
- This rescue pass showed that line endings are part of the contract too: a correct updater design still fails if `update.sh` is committed with CRLF and cannot pass `bash -n`.

## Evidence

- `update.sh` now leaves `python3-pygame`, `python3-websockets`, and `python3-mutagen` behind an explicit opt-in path.
- `README.md` and `docs/auto-update.md` explain the install-vs-update split and the `MR_PUMPKIN_ALLOW_PI_APT_UPDATE=1` override.
- `python -m pytest -q tests/test_pi_install_scripts.py tests/test_auto_update.py`, `bash -n install.sh`, and `bash -n update.sh` all passed.

## Follow-through

1. Keep future Raspberry Pi updater changes aligned with the least-privilege contract.
2. Preserve LF endings for `.sh` files so Windows worktrees do not silently break Unix lifecycle scripts.
