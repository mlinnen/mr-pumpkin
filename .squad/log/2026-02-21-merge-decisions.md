# Session Log — 2026-02-21: Merge Decisions

**Requested by:** Mike Linnen

## Summary

Scribe processed 8 pending decision files from the `.squad/decisions/inbox/` directory, merged them into the canonical `decisions.md` file, consolidated overlapping decisions into unified blocks, and deleted the inbox files after merge.

## Work Performed

### Decision Files Merged (8 total)

1. **copilot-directive-release-process.md** — Release workflow (dev → preview → main staging)
2. **ekko-gaze-coordinate-system.md** — Gaze coordinate system design with X/Y angles, default position (-45°, 45°)
3. **jinx-eye-direction-design.md** — Eye direction control design review decision (comprehensive feature spec)
4. **mylo-gaze-api-mismatch.md** — API mismatch between design spec and test suite
5. **release-process-directive.md** — Release process directive (VERSION file only, no auto-tags)
6. **vi-gaze-control-implementation.md** — Gaze control backend implementation (state variables, command parsing, rolling integration)
7. **vi-rolling-gaze-integration.md** — Bug fix for rolling eyes crashing with gaze control (AttributeError on read-only properties)
8. **vi-rolling-gaze-sequencing.md** — Bug fix for rolling animation not starting from current gaze position (timing/coordination issue)

### Consolidation Performed

**Overlapping decisions consolidated into 6 unified blocks:**

1. **Eye Direction Control Design (Issue #22)** — Consolidated 3 independent design documents (Jinx/Ekko/Vi) into single authoritative block covering: data model, coordinate system, rendering contract, socket command format, animation interaction, rationale, and trade-offs.

2. **Gaze Control Implementation (Vi)** — Captured backend implementation details (state variables, command handler, rendering logic, rolling integration).

3. **Gaze Coordinate System (Ekko)** — Captured graphics-specific design choices (coordinate origin, default position backward compatibility, angle-to-pixel conversion using sin()).

4. **Gaze API Mismatch (Mylo)** — Resolved: documented final API decision and test coverage (47 tests in `test_gaze_control.py`).

5. **Rolling Eyes Gaze Integration Fix (Vi)** — Critical bug fix capturing stale `pupil_angle` instead of converting gaze angles; AttributeError resolution.

6. **Rolling Eyes Gaze Sequencing Fix (Vi)** — Added `_gaze_to_angle()` helper to synchronize gaze and rolling coordinate systems for seamless animation continuity.

7. **Release Process Workflow** — Consolidated 2 directive files into single process definition (dev → preview → main, VERSION-only updates, automated squad-release).

### Key Decisions Made

- **Gaze control is orthogonal to expressions:** Persists across expression changes, pauses during rolling animations
- **Per-eye independent control:** Supports asymmetric/weird eye movements (user requirement)
- **Capture-restore pattern:** Gaze angles preserved before rolling, restored on completion (follows established pattern)
- **Default position (-45°, 45°):** Maintains backward compatibility with 43 existing projection mapping tests
- **Tuple-based storage:** Gaze stored as `pupil_angle_left`/`pupil_angle_right` tuples, exposed via read-only properties
- **Release staging process:** Always stage dev to preview before merging to main; no direct dev→main merges

## Files Changed

- `.squad/decisions.md` — Added 8 merged/consolidated decision blocks
- `.squad/decisions/inbox/` — Deleted all 8 files after merge

## Statistics

- **Decision blocks added:** 8
- **Duplicate blocks eliminated:** 0 (all had distinct authorship/perspective)
- **Overlapping blocks consolidated:** 3 (multiple authors on Issue #22 gaze control)
- **New decision areas opened:** Gaze control system, release process workflow
