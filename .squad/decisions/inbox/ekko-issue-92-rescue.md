# Ekko — Issue #92 rescue decision

- Preserve the already-approved Raspberry Pi updater contract in `update.sh`: non-root and cron-safe by default, with apt refresh only behind `MR_PUMPKIN_ALLOW_PI_APT_UPDATE=1`.
- Ship `.gitattributes` with `*.sh text eol=lf` so Bash lifecycle scripts stay LF-normalized even when edited from Windows worktrees.
- Validate the rescue with real Bash syntax checks plus the focused updater/install contract tests before shipping PR #93.
