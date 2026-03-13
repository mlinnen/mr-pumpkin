# Mylo Release Verdict — v0.5.15

**Date:** 2026-03-13  
**Requested by:** Mike Linnen  
**Role:** Mylo (Tester)

## Verdict

**Reject** — do not promote `v0.5.15` on `main` yet.

## Release-validation result

I ran the current main release validation gate in repo terms: the workflow-equivalent `python -m pytest -q` step from `squad-release.yml` / `squad-preview.yml`.

Result:
- **682 passed**
- **42 skipped**
- **11 failed**

Because the release workflow runs tests before packaging, the release path is currently blocked at the test step.

## Precise blockers

### 1) CLI startup coverage is still not stable in the full suite
- `tests/test_cli_options.py::TestPortOption::test_port_option_does_not_bind_default_5000`
- `tests/test_cli_options.py::TestCLIValidation::test_invalid_host_malformed`

Observed failure mode: port `5000` still appears reachable during scenarios where it should not be, so the CLI host/port behavior is not release-safe under full-suite conditions.

### 2) TCP/WebSocket parity is broken in integration coverage
These tests failed during release validation:
- `tests/test_integration_dual_protocol.py::TestIdenticalResponses::test_blink_command_both_protocols`
- `tests/test_integration_dual_protocol.py::TestIdenticalResponses::test_expression_command_both_protocols`
- `tests/test_integration_dual_protocol.py::TestIdenticalResponses::test_timeline_status_both_protocols`
- `tests/test_integration_dual_protocol.py::TestIdenticalResponses::test_recording_status_both_protocols`
- `tests/test_integration_dual_protocol.py::TestIdenticalResponses::test_list_recordings_both_protocols`
- `tests/test_integration_dual_protocol.py::TestProtocolSwitching::test_websocket_then_tcp_sequence`
- `tests/test_integration_dual_protocol.py::TestProtocolSwitching::test_alternating_protocols_10_commands`
- `tests/test_integration_dual_protocol.py::TestTimelineProtocols::test_download_via_both_protocols`
- `tests/test_integration_dual_protocol.py::TestStateSynchronization::test_change_expression_websocket_verify_tcp`

Observed failure mode: WebSocket requests returned connection/close-frame errors or `None` payloads while TCP continued to respond, so dual-protocol behavior is not currently release-ready.

## Additional release-state concern

The worktree is also not clean: `docs/what-is-new.md` is still in an unmerged (`UU`) state locally. Even aside from the failing test gate, this is not a clean promotion state for `main`.

## Required next step

Re-run release validation only after:
1. the CLI port/host failures are resolved under full-suite conditions,
2. the dual-protocol integration failures are cleared, and
3. the unmerged docs state is resolved.
