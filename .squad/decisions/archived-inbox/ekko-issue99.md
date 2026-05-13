Ekko — Issue 99 (Scaffold Silk.NET renderer + expression adapter)

Date: 2026-05-13

Summary
- Created initial branch and scaffold for Silk.NET renderer adapter.
- Added expression event adapter contract: Python will emit simple events:
  - `target_changed`: { "target": "happy" }
  - `current_changed`: { "current": "happy" }

Architectural questions / decisions required from Jinx
1. IPC Mechanism: Recommend WebSocket (binary-safe, integrates with webapp) or TCP/Unix socket for simplicity. gRPC offers typed contracts but increases dependency complexity.
   - Preference: WebSocket for cross-process + webapp friendliness. Confirm?
2. Event Schema Versioning: Add a `version` field to events to support future evolution? (Recommended)
3. Rendering Library Choice: Silk.NET is acceptable for low-level GL access; SkiaSharp may be faster to implement for 2D vector rendering and maps well to current pygame code. Which do we prefer long-term?

Requested action
- Please advise on preferred IPC (WebSocket/TCP/gRPC/NamedPipe) and confirm whether SkiaSharp is acceptable instead of Silk.NET for 2D port.

Ekko
