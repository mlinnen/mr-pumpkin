# Mylo release recommendation — v0.5.15

- **Date:** 2026-03-13
- **Decision:** Do not promote `dev` to `preview` or `main` for `v0.5.15` yet.

## Why

- The release flow is correctly wired for `dev -> preview -> main`, with test gates on CI/preview and CHANGELOG validation before main promotion.
- `VERSION` is `0.5.15` and `CHANGELOG.md` includes a matching `0.5.15` entry.
- `python scripts/package_release.py` succeeds and produces the expected release ZIP.
- However, the current release gate still fails on the full suite: `python -m pytest` fails in `tests/test_tcp_integration.py`.

## Blocker detail

- The failures are order-dependent and cascade after TCP integration coverage starts exercising recording/playback and nose command flows.
- Re-running isolated failing tests can pass, but full-order execution still wedges the TCP server and causes later connect timeouts on `localhost:5000`.
- Until that suite is green in full-order execution, promotion to `preview` or `main` would bypass the repo's intended quality bar.

## Recommended next step

Fix the TCP integration state-leak / server-wedge behavior first, then re-run the full pytest gate before promoting branches.
