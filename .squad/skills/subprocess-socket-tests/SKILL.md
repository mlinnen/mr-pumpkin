---
name: "subprocess-socket-tests"
description: "Reliable pattern for testing spawned TCP servers"
domain: "testing"
confidence: "high"
source: "observed"
---

## Context
Use this skill when tests spawn `pumpkin_face.py` or another TCP server in a subprocess and need deterministic readiness/cleanup across repeated runs.

## Patterns
- Treat **process-owned listening state** as readiness: poll the child PID's listening ports instead of assuming "some process is listening" means the spawned server is ready.
- For command sockets that often return no payload, `sendall()` then `shutdown(SHUT_WR)` so the server sees EOF and the client does not sit on a timeout waiting for an empty response.
- Centralize teardown in a helper (`stop_server`) so every test path terminates the spawned process the same way.
- Avoid readiness probes that consume the only pending TCP slot on a single-threaded server; if you must probe connectivity, do it after ownership is established or widen the server backlog.
- When a spawned-server test times out waiting for `localhost:5000` or `5001`, inspect existing listeners before blaming the new build; stale `python pumpkin_face.py` processes can create a false failure even when the child would otherwise start correctly.

## Anti-Patterns
- Polling `localhost:5000` until it opens without checking which PID owns the port.
- Duplicating ad hoc `terminate()/wait()/kill()` blocks in every test.
- Expecting no-response commands to complete quickly while keeping the write side of the socket open.
- Treating a bind-timeout failure as a product regression before ruling out leaked listeners from prior manual runs or interrupted test sessions.
