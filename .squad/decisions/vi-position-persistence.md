# Decision: Position Persistence Storage Location (Issue #86)

**Author:** Vi  
**Date:** 2026-03-20  
**Issue:** #86

## Decision

`pumpkin_position.json` is stored in the **working directory** (project root), alongside `pumpkin_face.py` and other top-level project files.

## Rationale

1. **Consistency with existing data files:** The project has no `config/` or `data/` subdirectory. Timeline files and other runtime data are also handled relative to the working directory.
2. **Simplicity:** A single flat file at the root is easy to inspect, backup, or delete by the operator aligning the projector.
3. **Operator visibility:** Projector alignment is a hardware/setup concern. Keeping the file at the root makes it obvious and accessible without navigating subdirectories.
4. **No install-time configuration needed:** No path needs to be configured — it always lives next to the entry point.

## Alternatives Considered

- **`~/.mr-pumpkin/position.json`** (user home dir): Adds OS-specific path logic with no benefit for a single-user deployment on a Pi.
- **`config/position.json`** (config subdir): No `config/` dir exists; creating one for a single file adds unnecessary structure.

## Impact

- File is gitignored-by-convention (runtime state, not source). Teams should document this in README if the file needs to be excluded from version control explicitly.
- `POSITION_FILE` module constant allows tests to patch the path cleanly without touching instance state.
