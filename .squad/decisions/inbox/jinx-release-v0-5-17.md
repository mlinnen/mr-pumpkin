# Release v0.5.17 notes scope

## Decision

For `v0.5.17`, the release metadata should describe the shipped Raspberry Pi install/update/package behavior and exclude `.squad/` coordination churn from the changelog summary.

## Why

The `dev` branch delta includes substantial team-history and orchestration updates, but the product-facing change being promoted is the Raspberry Pi dependency-management fix. Release notes should track what end users and maintainers receive in the build, not internal coordination noise that happened alongside it.

## Affected files

- `VERSION`
- `CHANGELOG.md`
- `docs/what-is-new.md`
