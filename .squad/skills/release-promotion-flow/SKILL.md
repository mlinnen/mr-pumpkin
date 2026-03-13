---
name: "release-promotion-flow"
description: "How to cut a Mr. Pumpkin release from dev through preview to main"
domain: "release-management"
confidence: "high"
source: "observed"
---

## Context
Use this skill when coordinating a versioned release for Mr. Pumpkin. The repository has explicit branch roles (`dev`, `preview`, `main`) plus GitHub workflows that validate preview and create the release from `main`.

## Patterns
- Prepare the release on `dev` first: update `VERSION`, add the matching `CHANGELOG.md` section, and update any directly related user-facing docs before promoting anything downstream.
- Push `dev` before starting promotion if local `dev` is ahead of `origin/dev`; do not promote unpublished local commits.
- Promote in order: merge `dev` into `preview`, validate, then merge `preview` into `main`.
- Keep the release version string aligned everywhere: `VERSION`, `CHANGELOG.md`, `docs/what-is-new.md`, and any summary docs that mention new user-facing capabilities.
- Include release-packaging fixes in the same release cut when they affect what ships to end users.

## Examples
- `squad-promote.yml` promotes `dev → preview` and then `preview → main`, reading the current `VERSION` for merge messages.
- `squad-release.yml` expects the released version to already exist in `CHANGELOG.md` before `main` is promoted.

## Anti-Patterns
- Promoting `preview` or `main` before the release version exists in `CHANGELOG.md`.
- Leaving new CLI features undocumented in `README.md` while still cutting a release.
- Assuming local-only `dev` commits are safe to promote without first pushing or otherwise synchronizing them.
