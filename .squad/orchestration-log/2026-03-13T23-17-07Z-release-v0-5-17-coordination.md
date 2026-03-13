# Release v0.5.17 Coordination Log

**Timestamp:** 2026-03-13T23:17:07Z  
**Topic:** Release v0.5.17 promotion and publication  
**Status:** Completed

## Activities

### Jinx (Lead) — Release Preparation & Promotion
- **Task:** Prepare and promote v0.5.17 release across dev→preview→main branch ladder
- **Outcome:** 
  - Updated VERSION file to 0.5.17
  - Updated CHANGELOG.md with release notes (Raspberry Pi install/update behavior focus)
  - Updated docs/what-is-new.md with user-facing changes
  - Promoted dev→preview (6b7911), preview→main (021f152)
  - Verified promoted heads: dev e6b7911, preview 021f152, main 6dc0c34
  - Status: Completed

### Automation Gap Identified — Release Publication
- **Issue:** squad-promote.yml push did not trigger squad-release.yml on main
- **Impact:** Expected automated release creation did not occur; manual intervention required
- **Action:** Coordinator (Mike Linnen) manually published release

### Mylo (Tester) — Integration Test Diagnostics
- **Task:** Diagnose pytest failure in temp-main worktree
- **Observation:** One full-suite run failed in tests/test_integration_dual_protocol.py::TestTimelineProtocols::test_upload_via_tcp_verify_via_websocket; same test passed on isolated rerun
- **Assessment:** Flakiness detected; likely timing/concurrency-related
- **Status:** In progress (no final summary provided by agent)

### Coordinator (Mike Linnen) — Manual Release Publication
- **Task:** Complete publication workflow when automation gap prevented squad-release.yml trigger
- **Outcome:**
  - Built mr-pumpkin-v0.5.17.zip from temp-main worktree
  - Created and pushed git tag v0.5.17
  - Published GitHub Release: https://github.com/mlinnen/mr-pumpkin/releases/tag/v0.5.17
  - Artifact included pre-built ZIP package for download
  - Status: Completed

## Team Learning

1. **Promotion automation reliability:** Branch promotion triggers are foundational; gap requires investigation into workflow event sequencing
2. **Flaky test pattern:** TCP/WebSocket dual-protocol test shows timeout/concurrency sensitivity; recommend test audit
3. **Decision canonicalization:** Release scope decision (exclude .squad/ churn from notes) executed correctly; product focus maintained

## Next Steps

- Investigate squad-release.yml trigger conditions (GitHub Actions event sequencing)
- Audit test_upload_via_tcp_verify_via_websocket for concurrency/timing sensitivity
