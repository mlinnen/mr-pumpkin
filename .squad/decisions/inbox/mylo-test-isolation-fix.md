# Test Isolation Fix — PR #96 (issue #86)

**Author:** Mylo (Tester)  
**Branch:** squad/86-save-pumpkin-position  
**Status:** Committed and pushed

---

## Problem

PR #96 introduced `_save_position()` calls in three places:
- `set_projection_offset()` — always saves
- `jog_projection(..., save=True)` — saves when flag is set
- `update()` animation loop — saves when head movement animation completes

Pre-existing tests in `test_head_movement.py` (and potentially other files) call `set_projection_offset()` and complete animations via `update()` **without patching `POSITION_FILE`**. This caused writes to `pumpkin_position.json` in the real working directory.

Example: `TestHeadMovementPerformance.test_offset_rendering_performance` calls `set_projection_offset(200, -100)`, writing `{"x": 200, "y": -100}` to CWD. When `test_rapid_direction_changes` or `test_frequent_offset_updates_stable` then creates a fresh `PumpkinFace()`, it loads `projection_offset_x=200` from disk instead of starting at 0, causing assertions like `assert 150 == 50` and `assert 200 <= 100` to fail.

## Investigation Finding

Contrary to the initial root-cause statement, `test_position_persistence.py` itself did **not** write to the CWD (its tests already correctly use `tmp_path` or patch `_save_position`). The contamination came from `test_head_movement.py`. The fix needed to be at the conftest level to cover all test files.

## Fix

Added an `autouse=True` fixture to `tests/conftest.py`:

```python
@pytest.fixture(autouse=True)
def isolate_position_file(tmp_path):
    pos_file = tmp_path / "pumpkin_position.json"
    with patch("pumpkin_face.POSITION_FILE", str(pos_file)):
        yield
```

This redirects all reads and writes of `POSITION_FILE` to a per-test temp directory for **every test function** in the suite. Tests that already patch `POSITION_FILE` with their own `tmp_path` value continue to work: the inner `with patch(...)` context overrides the outer autouse fixture for its duration.

## Why This Approach

| Option | Verdict |
|---|---|
| setUp/tearDown per class in test_position_persistence.py | ❌ Doesn't fix the actual leaking tests in test_head_movement.py |
| Add tmp_path patch to every test class in every file | ❌ Invasive, error-prone, incomplete |
| **autouse fixture in conftest.py** | ✅ Single point of defense; covers all current and future test files; zero test changes required |

## Verification

- `tests/test_position_persistence.py`: 46/46 pass
- `tests/test_head_movement.py`: 44/44 pass (was 8 failing)
- No `pumpkin_position.json` created in CWD after any test run
