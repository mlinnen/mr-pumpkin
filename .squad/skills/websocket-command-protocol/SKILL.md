# WebSocket Command Protocol

## Overview

Mr. Pumpkin uses a text-based command protocol over WebSocket (port 5001) for remote control. Commands are sent as plain text strings, and responses are either text status messages or JSON data structures.

## Connection

**WebSocket URL:** `ws://localhost:5001`

**Protocol:** Text-based (UTF-8 encoded strings)

## Message Format

### Client → Server (Commands)

Commands are plain text strings. Examples:

```
happy
blink
gaze 45 30
eyebrow_raise
play demo
```

### Server → Client (Responses)

Responses come in three formats:

1. **Success/Error Messages** (text):
   ```
   OK Expression changed to happy
   ERROR Unknown expression: xyz
   OK Playing demo.json (5000ms)
   ```

2. **JSON Status** (for query commands):
   ```json
   {
     "state": "playing",
     "filename": "demo.json",
     "position_ms": 1234,
     "duration_ms": 5000,
     "is_playing": true
   }
   ```

3. **Base64 Data** (for export commands):
   ```
   RECORDINGS_ZIP:<base64-encoded-zip-data>
   ```

## Command Categories

### Expression Commands
`neutral`, `happy`, `sad`, `angry`, `surprised`, `scared`, `sleeping`

### Animation Commands
`blink`, `wink_left`, `wink_right`, `roll_clockwise`, `roll_counterclockwise`

### Gaze Commands
- `gaze <x> <y>` — Both eyes (x,y in -90 to +90°)
- `gaze <lx> <ly> <rx> <ry>` — Independent eyes

### Eyebrow Commands
`eyebrow_raise`, `eyebrow_lower`, `eyebrow_raise_left`, `eyebrow_lower_left`, `eyebrow_raise_right`, `eyebrow_lower_right`, `eyebrow_reset`, `eyebrow <value>`, `eyebrow_left <value>`, `eyebrow_right <value>`

### Mouth Commands
`mouth_closed`, `mouth_open`, `mouth_wide`, `mouth_rounded`, `mouth_neutral`, `mouth <viseme>`

### Recording/Playback
`record_start`, `record_stop [filename]`, `record_cancel`, `recording_status`, `play <filename>`, `pause`, `resume`, `stop`, `seek <ms>`, `timeline_status`

### File Management
`list_recordings`, `delete_recording <filename>`, `rename_recording <old> <new>`, `download_timeline <filename>`, `upload_timeline <filename> <json>`, `upload_audio <filename> <base64>`, `export_recordings`, `import_recordings <base64-zip>`

### Projection/Head
`turn_left [amount]`, `turn_right [amount]`, `turn_up [amount]`, `turn_down [amount]`, `center_head`, `jog_offset <dx> <dy>`, `set_offset <x> <y>`, `projection_reset`

### Nose
`wiggle_nose [magnitude]`, `twitch_nose [magnitude]`, `scrunch_nose [magnitude]`, `reset_nose`

## Related Files

- **Server:** `pumpkin_face.py` (WebSocket handler)
- **Router:** `command_handler.py` (CommandRouter)
- **Client:** `client_example.py` (Python reference)
- **PWA:** `webapp/MrPumpkin.Web/Services/PumpkinWebSocketService.cs`
