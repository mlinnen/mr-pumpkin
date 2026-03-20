# Session: CI Fix - Test Isolation

**Timestamp:** 2026-03-20T15:31:21Z  
**Agent:** Mylo (Tester)  
**Status:** Complete

## Problem
PR #96 CI failure was caused by test isolation issue. The `set_projection_offset()` method (always-save path) was being called by test_head_movement.py tests, leaving `pumpkin_position.json` in the current working directory. Subsequent PumpkinFace() instances loaded this file and started with non-zero offsets, breaking assertions.

## Root Cause
- Tests did not isolate filesystem state
- Shared pumpkin_position.json file persisted across test runs
- PumpkinFace() constructor automatically loaded the position file if present

## Solution
Added autouse fixture in conftest.py that redirects POSITION_FILE to per-test tmp_path for the entire test suite.

## Results
- test_position_persistence.py: 46/46 tests pass ✓
- test_head_movement.py: 44/44 tests pass ✓
- CI isolation issue resolved

## Deliverables
- conftest.py fixture for test isolation
- All tests passing with clean isolation guarantees
