### 2026-03-13: Release Promotion Pattern for v0.5.15
**By:** Jinx  
**Issue:** Release v0.5.15  
**What:** For this repository, a safe release from `dev` to `preview` to `main` requires all release metadata to land on `dev` first: bump `VERSION`, add the matching `CHANGELOG.md` entry, update user-facing docs for any new CLI surface, then push `dev` before promoting downstream branches.  
**Why:** `squad-promote.yml` reads the current `VERSION` and `squad-release.yml` validates that `CHANGELOG.md` already contains the matching section before the `preview` to `main` promotion is considered release-ready. Treating release metadata as part of the `dev` source-of-truth keeps preview validation and final main promotion deterministic.  
**Impact:** Future release coordinators should not promote unpublished local-only `dev` commits or defer changelog/docs updates until after `preview`; the release branch chain should propagate one coherent versioned state.
