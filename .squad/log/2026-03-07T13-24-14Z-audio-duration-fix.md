# Session: Audio Duration Fix

**Team:** Vi (Backend Dev)  
**Task:** Fix audio duration_ms truncation bug in audio_analyzer.py  
**Status:** In Progress

## Issue
Gemini GenAI API underreports audio duration in microseconds. Duration values are being truncated when converted to milliseconds.

## Solution
Implement actual file duration measurement using ffprobe/pydub/wave library. Override Gemini's duration_ms value with measured duration.

## Changes
- Audio analyzer measures actual file duration
- Overrides Gemini's reported value with measured duration
- Ensures accurate duration_ms in response

## Notes
- Vi assigned to backend implementation
- Root cause: Gemini API returns incomplete or truncated duration values
- Solution uses system audio libraries for ground truth
