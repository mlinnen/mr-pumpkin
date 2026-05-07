---
name: "shell-stdout-stderr-contracts"
description: "Guard shell helpers that return values through command substitution"
domain: "testing"
confidence: "high"
source: "earned"
---

## Context

Use this when a shell function is called with command substitution like `value=$(helper)` and the helper also logs progress.

## Pattern

1. Treat stdout as the function's machine-readable return channel.
2. Send human-readable logs to stderr (`>&2`) or another non-captured sink.
3. Prefer `printf '%s\n' "$value"` for the returned value so the output contract is explicit.
4. Add a regression test that checks both sides of the contract: the caller uses command substitution and the helper keeps logs off stdout.

## Why it matters

If logs and returned values share stdout, the caller can receive a multi-line blob instead of a path, version, or token. In update/install scripts, that commonly surfaces as tools like `unzip`, `tar`, or `cp` failing with file-not-found errors against a log-prefixed pseudo-path.

## Minimal regression check

- Assert the script still contains the command substitution site (for example `local zip_path=$(download_release "$latest_version")`).
- Assert logging is redirected away from stdout.
- Assert the helper emits the returned value with a single stdout-only `printf`.
