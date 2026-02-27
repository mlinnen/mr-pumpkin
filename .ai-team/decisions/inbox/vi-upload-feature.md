# Recording File Upload Implementation

**Date:** 2026-02-25  
**Decision Owner:** Vi (Backend Dev)  
**Issue:** #44 - Allow users to upload recording files with validation

## What

Implemented `upload_timeline` socket command that allows clients to upload JSON recording files to the server with full validation.

## Why

Users need a way to programmatically upload pre-recorded or externally-generated timeline files. The implementation leverages the existing `FileManager` validation infrastructure to ensure only valid timeline files are accepted.

## Design Decisions

### 1. Multi-line JSON Protocol (READY/END_UPLOAD Handshake)

**Decision:** Use explicit READY and END_UPLOAD markers rather than expecting JSON on a single line.

**Rationale:**
- Timeline JSON files can be multi-line for readability
- Socket protocol is line-based, but JSON may contain newlines
- Handshake approach is explicit and prevents accidental data truncation
- Easy for clients to implement: read READY, send JSON, send END_UPLOAD marker

**Pattern:**
```
Client: upload_timeline <filename>
Server: READY
Client: <json content (multiple lines)>
Client: END_UPLOAD
Server: OK Uploaded <filename>.json
```

### 2. Leverage Existing FileManager Validation

**Decision:** Use `FileManager.upload_timeline()` which already validates JSON structure.

**Rationale:**
- DRY principle - validation logic already exists and is tested
- Consistent error messages across all upload paths
- Simplifies socket handler to focus on protocol, not validation logic
- FileManager already handles file system operations and collision detection

### 3. Add FileManager to PumpkinFace Initialization

**Decision:** Create `self.file_manager = FileManager()` in `__init__`.

**Rationale:**
- Consistent with existing patterns (timeline_playback, recording_session)
- Single instance reused across all socket commands
- Centralized file management state (if needed for future features)

### 4. Include upload_timeline in Timeline Commands List

**Decision:** Add "upload_timeline" to the list of commands that don't pause playback.

**Rationale:**
- Uploading a file is a file management operation, not an expression/animation command
- User might want to prepare a recording while playback is active
- Consistent with other timeline management commands (list, rename, delete)

## Implementation Details

### Error Handling

All errors return explicit messages to help clients debug:
- Missing filename: `ERROR Missing filename`
- Path traversal attempt: `ERROR Invalid filename: path separators not allowed`
- File collision: `ERROR File already exists: <filename>`
- Invalid JSON: `ERROR Invalid timeline: <error details>`
- Connection loss: `ERROR Connection lost while reading JSON`

### Client-Side Implementation

Added `upload_timeline(filename, json_file_path)` to client_example.py:
1. Validates local file exists
2. Reads file contents
3. Connects to server
4. Sends command, waits for READY
5. Transmits JSON content
6. Sends END_UPLOAD marker
7. Displays server response

### Security Considerations

- Path separator validation prevents directory traversal (e.g., `../../etc/passwd`)
- No shell commands or file operations beyond .json reading
- FileManager ensures only valid timeline structure is saved
- File permissions handled by OS filesystem

## Testing

- All 362 existing tests pass (no regressions)
- Protocol validated with client_example.py example
- Error paths covered (invalid JSON, file exists, missing args)
- Integration with existing recording/playback/file management infrastructure verified

## Future Extensions

- Support for gzip compression (large timeline files)
- Batch upload (multiple files in one connection)
- Streaming large files (don't read entire file into memory)
- Download/export timeline with validation
