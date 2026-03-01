# Skill — Command Routing Pattern

**Pattern Name:** Command Routing via CommandRouter  
**Domain:** Backend command handling  
**File:** `command_handler.py`

## Summary

Commands from network protocols (TCP/WebSocket) flow through `CommandRouter.execute()` which parses command strings and routes them to PumpkinFace methods. This pattern handles parameter extraction, recording capture, and method selection.

## Architecture

```
Network Protocol → CommandRouter.execute(command_str) → PumpkinFace method → State update
```

**Key components:**
1. **Protocol-agnostic routing:** Same router handles TCP and WebSocket commands
2. **String parsing:** Commands like "gaze 45 30" or "wiggle_nose 75" parsed into method calls
3. **Recording capture:** Commands captured during recording sessions before execution
4. **Public vs. private method selection:** Commands with parameters call private methods, simple commands call public API

## Pattern Details

### Zero-Parameter Commands

Commands with no arguments call public API methods:

```python
if data == "blink":
    if self.pumpkin.recording_session.is_recording:
        self.pumpkin._capture_command_for_recording(data)
    self.pumpkin.blink()
    print("Blink animation triggered")
    return ""
```

**Examples:** `blink`, `wink_left`, `roll_clockwise`, `center_head`, `eyebrow_reset`

### Parametric Commands

Commands with optional or required arguments call private methods directly to pass parameters:

```python
if data == "wiggle_nose" or data.startswith("wiggle_nose "):
    if self.pumpkin.recording_session.is_recording:
        self.pumpkin._capture_command_for_recording(data)
    try:
        parts = data.split()
        magnitude = float(parts[1]) if len(parts) > 1 else 50.0
        self.pumpkin._start_nose_twitch(magnitude)
        print(f"Wiggling nose (magnitude={magnitude})")
    except (ValueError, IndexError) as e:
        print(f"Error parsing wiggle_nose command: {e}")
    return ""
```

**Examples:** `gaze <x> <y>`, `wiggle_nose [magnitude]`, `turn_left [amount]`, `eyebrow <value>`

### Pattern Consistency

**Public API methods** (in `pumpkin_face.py`):
- Zero-parameter convenience wrappers
- Called by keyboard shortcuts and simple socket commands
- Example: `def twitch_nose(self):` calls `_start_nose_twitch()`

**Private methods** (prefixed with `_`):
- Accept parameters for customization
- Called by command router when parameters needed
- Called by timeline playback system with stored args
- Example: `def _start_nose_twitch(self, magnitude: float = 50.0):`

## Adding New Commands

### Step 1: Identify command type

- **Zero-parameter:** User invokes action with no arguments (e.g., "blink")
- **Fixed-parameter:** User provides specific values (e.g., "gaze 45 30")
- **Optional-parameter:** User may provide value or use default (e.g., "wiggle_nose" or "wiggle_nose 75")

### Step 2: Implement in pumpkin_face.py

Add private method with parameters (if needed):
```python
def _start_new_animation(self, magnitude: float = 50.0):
    """Initiate new animation with specified magnitude."""
    self.animation_state = magnitude
    self.is_animating = True
```

Add public wrapper (if zero-parameter form is useful):
```python
def new_animation(self):
    """Start new animation with default magnitude."""
    self._start_new_animation()
```

### Step 3: Add to command_handler.py

Insert in appropriate section (expression, animation, gaze, etc.):

```python
if data == "new_animation" or data.startswith("new_animation "):
    if self.pumpkin.recording_session.is_recording:
        self.pumpkin._capture_command_for_recording(data)
    try:
        parts = data.split()
        magnitude = float(parts[1]) if len(parts) > 1 else 50.0
        self.pumpkin._start_new_animation(magnitude)
        print(f"New animation triggered (magnitude={magnitude})")
    except (ValueError, IndexError) as e:
        print(f"Error parsing new_animation command: {e}")
    return ""
```

### Step 4: Add to timeline command execution

Update `_execute_timeline_command()` method (~line 970):

```python
elif command == "new_animation":
    magnitude = args.get("magnitude", 50.0)
    self._start_new_animation(magnitude)
```

### Step 5: Add to recording command capture

Update `_capture_command_for_recording()` method (~line 1210):

```python
elif cmd == "new_animation":
    magnitude = 50.0
    if len(parts) >= 2:
        try:
            magnitude = float(parts[1])
        except ValueError:
            pass
    self.recording_session.record_command(cmd, {"magnitude": magnitude})
```

### Step 6: Document in README.md

Add to appropriate command section with description:
```markdown
- `new_animation [magnitude]` - Trigger new animation (default magnitude: 50)
```

## Common Patterns

### Command Aliases

To create command aliases (multiple names for same behavior):

```python
# Add both command names with identical implementations
if data == "wiggle_nose" or data.startswith("wiggle_nose "):
    # ... implementation ...

if data == "twitch_nose" or data.startswith("twitch_nose "):
    # ... identical implementation ...
```

### Parameter Validation

Always wrap parameter parsing in try/except:
```python
try:
    parts = data.split()
    value = float(parts[1])
    self.pumpkin.set_something(value)
except (ValueError, IndexError) as e:
    print(f"Error parsing command: {e}")
```

### Recording Integration

All animation/state commands must check recording status:
```python
if self.pumpkin.recording_session.is_recording:
    self.pumpkin._capture_command_for_recording(data)
```

Timeline commands (record_start, play, pause, etc.) skip this check.

## Testing Checklist

- [ ] Command works via TCP socket (port 5000)
- [ ] Command works via WebSocket (port 5001)
- [ ] Command with default parameters works
- [ ] Command with custom parameters works
- [ ] Command is captured during recording
- [ ] Command executes correctly in timeline playback
- [ ] Error handling for malformed input
- [ ] README.md documents the command
- [ ] Command appears in client_example.py menu (if appropriate)

## Related Files

- `command_handler.py` - Main command routing logic
- `pumpkin_face.py` - Command implementation (public and private methods)
- `timeline.py` - Timeline playback system
- `README.md` - User-facing command documentation
- `client_example.py` - Interactive command client

## References

- Issue #50: wiggle_nose command alias added
- `.squad/agents/jinx/history.md`: Command router architecture decisions
