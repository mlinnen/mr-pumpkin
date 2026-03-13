---
name: "shell-stdout-discipline"
description: "Keep stdout machine-readable when shell helpers are consumed by command substitution"
domain: "shell"
confidence: "high"
source: "earned"
---

## Context

Use this pattern when a shell function both reports progress and returns a value that another part of the script captures with `$(...)`.

## Pattern

1. Reserve stdout for the function's returned value only.
2. Send human-readable logs and progress messages to stderr.
3. If logs must also be persisted, use `tee -a logfile >&2`.
4. Prefer explicit value output such as `printf '%s\n' "$result"` for the returned data.

## Why it matters

Command substitution captures stdout verbatim. If logging shares that stream, the caller can receive a corrupted path, PID, version string, or JSON blob and fail later in a misleading place.

## Example

For `zip_path=$(download_release "$version")`, `download_release()` may log download progress, but only the final ZIP path should be emitted on stdout. Route logs to stderr so downstream commands like `unzip "$zip_path"` receive a valid filename.
