# SKILL: Adding a Help Command to CommandRouter

**Domain:** Backend / Command Parsing  
**Applies to:** `command_handler.py` — `CommandRouter.execute()`

---

## Pattern

Add a `help` command to a text-based command router that returns a plain-text listing of all commands.

### Placement rule
Insert the `help` handler in the **status/query section** of `execute()`, **before** the `is_timeline_command` guard and before the expression fallback. This ensures:
- `help` never captures into a recording session
- `help` never pauses active timeline playback
- `help` returns immediately like other read-only queries

### Return format
Return a **plain-text** multi-line string, NOT JSON.

```python
if data == "help":
    help_text = (
        "Commands:\n"
        "  <command> [<args>]   - <description>\n"
        ...
    )
    return help_text
```

**Why plain text:** `help` is human-readable discovery, not a machine-parseable data response. JSON is reserved for structured state data that callers parse programmatically.

### Checklist when updating help
When adding a new command to `CommandRouter`, also update the `help` handler with:
- Command name (exact string as sent over TCP/WebSocket)
- Arguments in `<required>` / `[optional]` notation
- One-line description of what it does
- Any aliases on a separate line with `Alias for ...`

---

## Example (mr-pumpkin)

- File: `command_handler.py`  
- Issue: #56  
- All 554 existing tests continue to pass after adding this handler — zero behavior change for existing commands.
