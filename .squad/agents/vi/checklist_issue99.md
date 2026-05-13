# Vi — Implementation checklist for Issues #107 & #108 (squad/99-vi-engine)

- [x] Create branch `squad/99-vi-engine`
- [ ] Extract CommandRouter from existing handlers into engine/command_router.py
- [ ] Add WebSocket adapter and start/stop hooks (engine/websocket_adapter.py)
- [ ] Ensure CommandRouter.execute supports both text and JSON modes
- [ ] Port RecordingSession and Playback adapters to ensure serialization parity
- [ ] Implement upload_timeline WS inline JSON path and preserve TCP READY/END_UPLOAD
- [ ] Add tests for WS/TCP parity: recordings round-trip, play/seek/record behaviors
- [ ] Run full test-suite and fix regressions
- [ ] Document API/schema decisions in .squad/decisions/inbox/vi-issue99.md and notify Jinx

Notes: Prioritize backward compatibility: TCP must continue to behave unchanged. WebSocket should accept JSON messages like: {"command":"blink", "args":{}}.
