---
name: "release-validation-triage"
description: "How to assess release readiness when a full suite fails but isolated tests pass"
domain: "testing"
confidence: "medium"
source: "earned"
---

## Context

Use this pattern when a release candidate appears healthy on targeted checks, but the full validation gate still fails. This is common in integration-heavy suites with shared sockets, files, or long-lived subprocesses.

## Pattern

1. Run the repo's real release gate first, not a reduced substitute.
2. If the full gate fails, re-run the failing file and then the smallest failing test in isolation.
3. Classify the result:
   - **Fails in isolation:** product bug or deterministic test bug.
   - **Passes in isolation but fails in suite order:** state leakage, resource contention, or teardown/reset weakness.
4. Treat order-dependent failures as release blockers anyway if the official gate is the full suite.

## Useful checks

- Re-check listeners or temp artifacts after failure when tests use sockets, subprocesses, or filesystem state.
- Compare full-suite behavior with isolated `pytest path::test_name -vv -s` runs.
- Note whether a single failure cascades into many later timeouts; that usually means the shared test fixture or server got wedged.

## Release recommendation rule

If the repository's official release validation command is red, the candidate is **not** promotion-ready, even when packaging succeeds and isolated tests pass. Report both the deterministic facts (which command failed) and the likely class of issue (for example: TCP server state leakage across tests).
