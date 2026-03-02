### 2026-03-02: Issue #33 Auto-Update Test Suite

**By:** Mylo  
**Status:** ✅ Complete — All 32 tests passing  
**File:** `tests/test_auto_update.py`

---

## Summary

Created comprehensive test suite for auto-update logic per Jinx's architecture specification. Tests validate the core logic that will be embedded in `update.sh` and `update.ps1` scripts.

**Test Coverage:** 32 tests across 5 test classes

---

## Test Results

```
================================================= test session starts =================================================
platform win32 -- Python 3.13.12, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\_projects\mr-pumpkin
collected 32 items

tests/test_auto_update.py::TestVersionComparison (11 tests) ..................... PASSED
tests/test_auto_update.py::TestGitHubApiParsing (6 tests) ........................ PASSED
tests/test_auto_update.py::TestZipValidation (8 tests) .......................... PASSED
tests/test_auto_update.py::TestFileOperations (4 tests) ......................... PASSED
tests/test_auto_update.py::TestEdgeCases (3 tests) .............................. PASSED

================================================= 32 passed in 0.39s ==================================================
```

---

## Test Classes & Coverage

### 1. TestVersionComparison (11 tests)
Validates semantic version comparison logic (major.minor.patch).

**Key scenarios:**
- ✅ Older minor/patch/major versions trigger update
- ✅ Same version or newer local version = no update
- ✅ Handles 'v' prefix in version tags (v0.5.4)
- ✅ Strips whitespace from version strings
- ✅ Multi-digit version numbers (0.5.9 vs 0.5.10 - NOT string comparison)
- ✅ Invalid format detection (raises ValueError)

**Example:** `should_update("v0.5.4", "0.6.0")` → `True`

### 2. TestGitHubApiParsing (6 tests)
Validates JSON parsing for GitHub releases API response.

**Key scenarios:**
- ✅ Extracts `tag_name` from release JSON
- ✅ Strips 'v' prefix from tags
- ✅ Handles tags with/without 'v' prefix
- ✅ Detects missing `tag_name` field (raises ValueError)
- ✅ Detects malformed JSON (raises JSONDecodeError)
- ✅ Strips whitespace from tag values

**Example:** `{"tag_name": "v0.6.0"}` → `"0.6.0"`

### 3. TestZipValidation (8 tests)
Validates ZIP file integrity and required file checking.

**Required files:** `pumpkin_face.py`, `VERSION`, `requirements.txt`

**Key scenarios:**
- ✅ Valid ZIP with all required files passes
- ✅ Missing any required file fails validation
- ✅ Empty ZIP fails
- ✅ Corrupted ZIP file fails
- ✅ Non-existent file path fails
- ✅ Handles subdirectory structure (extracts basenames)

**Logic:** `validate_zip(path)` → `True/False`

### 4. TestFileOperations (4 tests)
Validates temp directory creation and file deployment logic.

**Key scenarios:**
- ✅ Temp directory created with unique name
- ✅ Deployment copies required files to install dir
- ✅ **Preserves user data:** timeline_*.json files NOT overwritten when `preserve_configs=True`
- ✅ All files copied when preservation disabled

**Logic:** `deploy_files(source, dest, preserve_configs=True)` → list of copied files

### 5. TestEdgeCases (3 tests)
Documents limitations and validates edge case handling.

**Key scenarios:**
- ✅ Pre-release versions (0.6.0-beta.1) → raises ValueError (v1 limitation documented)
- ✅ Very large version numbers (99.99.99) handled correctly
- ✅ Deployment to non-existent directory raises FileNotFoundError

---

## Helper Functions (Python logic equivalents)

The test file defines Python helper functions that mirror the logic to be implemented in shell scripts:

```python
def parse_version(version_str):
    """Parse version string to (major, minor, patch) tuple."""
    
def should_update(local_version, remote_version):
    """Return True if remote > local (semantic versioning)."""
    
def extract_tag_from_release_json(json_str):
    """Extract version from GitHub API JSON response."""
    
def validate_zip(zip_path):
    """Validate ZIP contains required Mr. Pumpkin files."""
    
def create_temp_dir():
    """Create temporary directory for update operations."""
    
def deploy_files(source_dir, dest_dir, preserve_configs=True):
    """Deploy files from extracted ZIP to install directory."""
```

These functions serve as:
1. **Executable documentation** of expected behavior
2. **Reference implementation** for shell script logic
3. **Validation suite** for version comparison and file handling

---

## For Vi: Integration Notes

**Branch status:** Branch `squad/33-auto-update` does not exist yet.

**Action required:**
- Include `tests/test_auto_update.py` in your PR when you create the branch
- Shell scripts should implement logic that matches these test behaviors
- Version comparison in bash/PowerShell should mirror `should_update()` logic
- ZIP validation in scripts should check for same required files

**Test coverage gaps (intentional v1 limitations):**
- Pre-release versions (0.6.0-beta.1) not supported — will error
- Rollback mechanism not tested (not implemented in v1)
- Process detection/restart not tested (shell-specific, manual testing required)

**Shell script validation:**
Once scripts are implemented, these tests serve as acceptance criteria for the logic components.

---

## Learnings for Testing Auto-Update Logic

**Pattern: Test shell script logic via Python equivalents**
- Shell scripts are hard to unit test (bash/PowerShell syntax varies)
- Python helper functions validate core logic
- Tests serve as reference implementation for shell translation

**Pattern: Semantic version comparison**
- Parse version as tuple of integers: `(major, minor, patch)`
- Compare tuples directly (Python handles element-wise comparison)
- Strip 'v' prefix and whitespace before parsing

**Pattern: ZIP validation without extraction**
- Use `zipfile.ZipFile.namelist()` to read archive contents
- Check for basename matches (handles subdirectory structure)
- Validate ZIP integrity via `BadZipFile` exception

**Pattern: File deployment with preservation**
- Use explicit pattern matching: `item.startswith('timeline_') and item.endswith('.json')`
- Skip user data files during deployment
- Return list of copied files for verification

---

## Dependencies

**Standard library only** — no new dependencies added:
- `pytest` (already in requirements-dev.txt)
- `json`, `tempfile`, `zipfile`, `os`, `pathlib`, `shutil` (stdlib)
- `unittest.mock` (stdlib, not used in current version but imported for future)

---

**Next Steps:**
1. Vi creates `squad/33-auto-update` branch
2. Vi implements `update.sh` and `update.ps1` following Jinx's spec
3. Vi includes this test file in the PR
4. Scripts implement logic that matches test behavior
5. Manual platform testing (Linux, Windows, Pi) by Mylo after script implementation
