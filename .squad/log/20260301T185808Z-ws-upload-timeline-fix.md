# Session Log: WebSocket upload_timeline Fix

**Date:** 2026-03-01T18:58:08Z  
**Topic:** WebSocket handler for inline timeline uploads  
**Agent:** Vi (Backend Dev)

## Summary

Fixed `pumpkin_face.py` WebSocket handler to intercept `upload_timeline` commands and parse inline JSON format (`upload_timeline <filename> <json>`). Updated integration tests. Decision documented in decisions/inbox.

## Key Changes

- `_ws_handler()` now short-circuits `upload_timeline` before command routing
- Handles single-message format instead of multi-step TCP protocol
- Security: Path separators rejected, JSON validation in file_manager

## Outcome

Both WebSocket and TCP clients can now upload timelines with their respective protocol patterns.
