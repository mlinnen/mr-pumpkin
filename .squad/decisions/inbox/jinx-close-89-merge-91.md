---
date: 2026-03-13
owner: Jinx
subject: Manual issue closure after dev-branch merge
---

## Context

While completing issue/PR triage for #89, #90, and PR #91, PR #91 merged into `dev` with `Closes #90` in its body, but GitHub did not auto-close issue #90 after the merge.

## Decision

For dev-targeted PRs, the team should verify linked issue state after merge instead of assuming GitHub auto-close keywords will resolve the issue. If the issue remains open, close it explicitly with a short note referencing the merged PR or shipped version.

## Why

This keeps issue tracking accurate during the dev → preview → main promotion flow and avoids leaving completed work open simply because the merge landed on a non-default branch.
