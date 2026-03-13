---
name: "release-packaging"
description: "Validate the Mr. Pumpkin release ZIP contract"
domain: "release-packaging"
confidence: "high"
source: "issue-90"
---

## Context

Mr. Pumpkin ships as a GitHub release ZIP, not as a pip-installed package. The archive itself is the deployment contract, so packaging regressions directly affect installation and update workflows.

## Patterns

### Required lifecycle scripts

Every generated release archive should include all four platform entrypoints at the top level of the versioned folder:

- `install.sh`
- `install.ps1`
- `update.sh`
- `update.ps1`

If one of these is missing, the release is incomplete for at least one supported lifecycle path.

### Test the real archive

Prefer an automated test that imports `scripts/package_release.py`, builds the ZIP from the repository root, opens the produced archive, and asserts exact members. This catches regressions in the actual packaging script rather than only validating simplified helper logic.

### Keep generated archives ephemeral

Release ZIPs are build artifacts. Create them for validation, inspect them, then delete them so generated binaries do not enter source control.

## Examples

```python
module = load_package_release_module()
module.create_release_package()

with zipfile.ZipFile(archive_path, "r") as zf:
    assert f"{folder_name}/update.sh" in zf.namelist()
    assert f"{folder_name}/update.ps1" in zf.namelist()
```

## Anti-Patterns

- **Checking only helper logic** — A basename-only ZIP validator can miss omissions in `scripts/package_release.py`.
- **Committing release ZIPs** — Generated artifacts create noisy diffs and should remain untracked.
