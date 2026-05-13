# Decision: Vi issue 99 — WebSocket & Timeline API choices

Date: 2026-05-13
Author: Vi (backend)

Decisions:
1. Transport: Dual-protocol approach. Continue TCP (port 5000) and add WebSocket (port 5001) to enable browser clients. WebSocket uses the `websockets` asyncio library when available; startup should degrade gracefully if unavailable.
2. Message schema (WebSocket): JSON object with shape:
   {
     "command": "<command_name>",
     "args": { /* optional dict of arguments */ },
     "meta": { /* optional: client_id, correlation_id */ }
   }
   Text/TCP transport remains backwards-compatible (single-line text commands). CommandRouter.execute must accept both string and parsed dict inputs and preserve semantics.
3. upload_timeline: For TCP, preserve READY/END_UPLOAD handshake. For WebSocket, use single-message inline JSON: {"command":"upload_timeline", "args": {"filename":"x.json","content":<object|string>} }.
4. Timeline serialization parity: Keep existing Timeline JSON schema (version 1.0) with fields: version, duration_ms, commands[] where each entry has time_ms, command, args.
5. Error/Response formats: For WebSocket, use JSON responses: {"status":"ok"/"error","message":"..."}. For TCP, retain text OK/ERROR lines for backward compatibility.

Action: Please review and ack. Requesting Jinx to confirm port 5001 and websockets dependency.
