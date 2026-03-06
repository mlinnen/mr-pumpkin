# Orchestration: Vi (Agent-3)

**Timestamp:** 2026-03-06T02:16:29Z  
**Issue:** #67  
**Task:** Add upload_audio TCP/WS endpoint to pumpkin_face.py + FileManager + uploader client

## Completed

✅ pumpkin_face.py: added `upload_audio` command handler  
✅ FileManager.upload_audio(): stores raw bytes to `~/.mr-pumpkin/recordings/<filename>.mp3`  
✅ skill/uploader.py: added `upload_audio()` client function for TCP/WS  
✅ Multi-step handshake identical to `upload_timeline`:
  1. Client sends `upload_audio <filename>`
  2. Server ACKs with byte count prompt
  3. Client sends raw audio bytes
  4. Server ACKs, writes file, confirms success

✅ Directory creation: recordings dir auto-created if missing  
✅ Error handling: duplicate filename, I/O failures, socket errors  
✅ Logging: INFO for upload start/completion, ERROR for failures  

## Implementation Details

- Stores to `~/.mr-pumpkin/recordings/` (same pattern as timelines)
- Accepts MP3, WAV, OGG (configurable MIME hints)
- Chunked send for large files (>3MB)
- Filename validation: alphanumeric + underscore/dash

## Status: DONE

Audio pipeline complete. Ready for Mylo's test scaffold (#72) and integration tests.
