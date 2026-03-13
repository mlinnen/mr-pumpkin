# Jinx Decision Inbox — Issue #90 PR

- **Issue:** #90 — release package omitted `update.sh` and `update.ps1`
- **Decision:** Treat the release ZIP as the full deployment contract for cross-platform lifecycle scripts. Both install scripts and both update scripts must be present in every generated archive.
- **Why:** End users deploy from the release ZIP, and auto-update is part of the supported operational path documented in the README. Omitting the updater scripts creates an incomplete distribution and prevents future update workflow parity after deployment.
- **Validation:** Added an automated packaging test that builds the ZIP and asserts `update.sh` and `update.ps1` are present under the versioned top-level release folder.
