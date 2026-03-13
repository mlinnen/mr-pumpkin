### 2026-03-12: Harden subprocess socket tests; do not mutate released v0.5.15 main

**By:** Vi

**What:** For CLI/server subprocess tests, verify that the spawned process owns the listening port instead of treating any open port as readiness. Also avoid changing `main` after the existing `v0.5.15` promotion/tag when recovery work only affects test reliability.

**Why:** Global port-open probes can pass against stale listeners and create order-dependent failures, especially when the server backlog is tiny and readiness checks consume the only pending connection slot. `origin/main` already points at the promoted `v0.5.15` merge/tag, so the safe recovery path is to fix validation reliability on `dev` and report that no further `main` mutation is required for this release cut.
