# Vi combine dev changes

- **Date:** 2026-03-13
- **Decision:** Combine the current release-recovery follow-up work into one local `dev` commit and do not push as part of this step.

## Why

- The current worktree already contains one coherent set of backend, test, and squad-documentation changes tied to release recovery and CLI/socket reliability.
- A single local commit keeps the audit trail clean while avoiding any accidental promotion beyond `dev`.
- The request asked to combine the work on `dev`, not to publish it.
