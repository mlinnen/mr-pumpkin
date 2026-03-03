# Decision: Recording Chaining Test Patterns

**Date:** 2026-03-02  
**Author:** Mylo (Tester)  
**Status:** Proposed  
**Context:** Issue #55 - Recording chaining feature tests

## Summary

Established test patterns for nested/recursive playback behavior in timeline engine. The recording chaining feature allows one timeline to embed another via `play_recording` command, with stack-based state management.

## Test Patterns Established

### 1. Stack-Based State Testing
- Verify stack depth via `get_status()["stack_depth"]`
- Test stack push on `play_recording` execution
- Test stack pop when sub-recording completes
- Test stack clear on `stop()` called mid-playback

### 2. Command Execution Order Verification
- Use mock callbacks to track command dispatch sequence
- Verify parent-before → sub → parent-after ordering
- Assert `play_recording` is NOT dispatched (internal-only command)
- Check callback receives commands FROM sub-recording, not the play_recording command itself

### 3. Depth Limit Testing
- Create chain of N+1 recordings (where N = max_depth)
- Verify error message contains "Maximum nesting depth"
- Assert stack never exceeds `_max_depth` (5)
- Confirm playback continues (doesn't crash) at limit

### 4. Error Resilience Testing
- Missing sub-recording file should log error, not stop parent
- Empty filename in play_recording should skip gracefully
- Verify playback state remains PLAYING after sub-recording load failure

### 5. Time-Based Playback Simulation
- Use incremental `update(dt_ms)` calls to control progression
- Advance past command timestamps to trigger execution
- Simulate sub-recording completion by advancing to sub's duration_ms
- Test position restoration when popping back to parent

## Key Insights

1. **Position tracking is cumulative**: When popping from sub back to parent, parent position advances by time spent in sub-recording
2. **play_recording is special**: Not dispatched to callback, handled internally by playback engine
3. **Stack is implementation detail**: Exposed via status query for debugging, but not part of public API
4. **Resilient by design**: Errors in sub-recording load don't cascade to parent playback

## Recommendation

- **Adopt these patterns** for future nested/recursive behavior testing
- Test helper functions (`make_timeline`, `save_timeline`) reduce boilerplate
- Mock callbacks provide deterministic verification without actual command execution
- Incremental time advancement gives precise control over playback progression

## Related Files

- `tests/test_recording_chaining.py` - 11 comprehensive tests
- `timeline.py` - Playback engine with stack-based chaining (lines 189-375)
- `skill/generator.py` - _VALID_COMMANDS includes play_recording (line 142)
