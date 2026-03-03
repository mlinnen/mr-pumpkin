# Decision: help command returns plain text, not JSON

**By:** Vi  
**Issue:** #56  
**Date:** 2026-03-03

## Decision
The `help` command returns a plain-text formatted string, not JSON.

## Rationale
- Status/query commands (`timeline_status`, `recording_status`, `list_recordings`) return JSON because downstream code parses them.
- `help` is documentation for a human operator at a terminal or WebSocket client — plain text is more readable and requires no JSON parser.
- Consistent with the existing plain-text `OK ...` / `ERROR ...` response convention for non-data responses.

## Implications
- Clients that blindly attempt `json.loads()` on all responses will receive a parse error for `help`; they should handle non-JSON responses.
- This is not a concern in practice: `help` is an interactive discovery tool, not a programmatic query.
