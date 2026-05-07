---
name: "manual-release-recovery"
description: "Recover a skipped GitHub release from the exact promoted main content"
domain: "release-management"
confidence: "high"
source: "earned"
---

## Context

Use this when release metadata is already promoted to `main`, but the GitHub Release was never published because the normal `push`-triggered workflow did not fire.

## Patterns

### Publish from exact `main`

Create a temporary detached worktree at `origin/main` (or the verified promoted SHA) and do the manual release work there. This prevents accidental release from `dev`, a dirty checkout, or later local edits.

### Reuse workflow logic, not ad-hoc notes

Treat `.github/workflows/squad-release.yml` as the source of truth. Recreate its important behavior: read `VERSION`, extract that version's `CHANGELOG.md` section for release notes, build the ZIP with `scripts/package_release.py`, and publish the GitHub Release with the matching tag and asset.

### Verify the shipped archive before upload

Open the generated ZIP and confirm the release contract entries are present, especially lifecycle scripts and helper files needed outside a repo checkout. This is the highest-value manual check when the release problem is publication, not code readiness.

### Prefer recovery over workflow edits

If the current incident is only that automation did not trigger, do not patch committed workflows just to ship one release. Manual publication from the verified promoted tree is lower risk than introducing release-pipeline changes under pressure.

## Anti-Patterns

- Releasing from `dev` after `main` has already been promoted.
- Creating an extra `main` commit solely to retrigger release automation.
- Building the asset from a working tree with unrelated local modifications.
