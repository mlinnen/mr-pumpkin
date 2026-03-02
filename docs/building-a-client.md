# Building a Client for Mr. Pumpkin

This guide explains how to build a client application to control Mr. Pumpkin remotely. Whether you're integrating it into a home automation system, building a Halloween display, or creating an interactive performance, this document will help you get started.

## Overview

Mr. Pumpkin is a controllable animated jack-o'-lantern face that listens for commands over a network connection. You can:

- **Set expressions** (happy, sad, angry, scared, surprised, neutral, sleeping)
- **Trigger animations** (blink, wink, eye rolls)
- **Control gaze direction** (where the eyes look)
- **Adjust eyebrows** (raise, lower, individual control)
- **Move the head** (turn left/right, tilt up/down)
- **Animate the nose** (wiggle, twitch, scrunch)
- **Record and playback sequences** (timeline system for complex performances)

All communication happens through simple text commands sent over TCP sockets.

## Connection Basics

**Protocol:** TCP socket connection  
**Default Port:** 5000  
**Host:** `localhost` (or the IP address of the machine running Mr. Pumpkin)

### Connection Pattern

Each command follows this pattern:

1. **Connect** to the server
2. **Send** your command as UTF-8 text
3. **Signal end** of command (call `shutdown(SHUT_WR)` or close write side)
4. **Read** response (if any)
5. **Close** the connection

**Important:** Use one connection per command. Don't try to reuse connections.

## Quick Start

Here's a minimal Python example to send an expression:

```python
import socket

def send_command(command):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 5000))
    client.send(command.encode('utf-8'))
    client.shutdown(socket.SHUT_WR)  # Signal end of command
    response = client.recv(1024).decode('utf-8')
    client.close()
    return response

# Make the pumpkin happy
send_command('happy')
```

That's it! Five lines and you're controlling a pumpkin face.

## Command Reference

### Expression Commands

Set the overall facial expression. These commands return no response (fire-and-forget).

```python
send_command('neutral')     # Default neutral face
send_command('happy')       # Smiling
send_command('sad')         # Frowning
send_command('angry')       # Angry/scowling
send_command('surprised')   # Wide-eyed surprise
send_command('scared')      # Frightened expression
send_command('sleeping')    # Eyes closed, relaxed
```

### Animation Commands

Trigger short animations. These also return no response.

```python
send_command('blink')                   # Both eyes blink
send_command('wink_left')               # Left eye winks
send_command('wink_right')              # Right eye winks
send_command('roll_clockwise')          # Eyes roll clockwise
send_command('roll_counterclockwise')   # Eyes roll counter-clockwise
```

### Gaze Control

Control where the eyes look. Angles range from -90° to +90°.
- `0, 0` = straight ahead (center)
- Positive X = right, Negative X = left
- Positive Y = up, Negative Y = down

```python
# Both eyes look in the same direction
send_command('gaze 0 0')        # Look straight ahead
send_command('gaze 45 30')      # Look up and to the right
send_command('gaze -90 0')      # Look far left

# Independent eye control (cross-eyed, wall-eyed, etc.)
send_command('gaze -90 0 90 0')    # Left eye left, right eye right
send_command('gaze 0 45 0 -45')    # Left eye up, right eye down
```

### Eyebrow Control

Adjust eyebrow positions for added expression.

```python
# Preset movements
send_command('eyebrow_raise')         # Raise both eyebrows
send_command('eyebrow_lower')         # Lower both eyebrows
send_command('eyebrow_raise_left')    # Raise left eyebrow only
send_command('eyebrow_lower_left')    # Lower left eyebrow only
send_command('eyebrow_raise_right')   # Raise right eyebrow only
send_command('eyebrow_lower_right')   # Lower right eyebrow only
send_command('eyebrow_reset')         # Reset both to neutral

# Precise numeric control
send_command('eyebrow 50')            # Set both eyebrows to offset +50
send_command('eyebrow_left -30')      # Set left eyebrow to offset -30
send_command('eyebrow_right 20')      # Set right eyebrow to offset +20
```

### Head Movement

Move or tilt the entire head.

```python
send_command('turn_left')        # Turn left by default amount (50px)
send_command('turn_right 100')   # Turn right by 100 pixels
send_command('turn_up 75')       # Tilt up by 75 pixels
send_command('turn_down')        # Tilt down by default amount
send_command('center_head')      # Return to center position
```

### Nose Animation

Animate the nose for extra character.

```python
send_command('wiggle_nose')          # Wiggle with default magnitude
send_command('twitch_nose 100')      # Twitch with magnitude 100
send_command('scrunch_nose 50')      # Scrunch with magnitude 50
send_command('reset_nose')           # Return nose to neutral
```

### Projection Offset

Fine-tune the projection alignment (useful for physical setup).

```python
send_command('projection_reset')     # Reset to default position
send_command('jog_offset 10 -5')     # Nudge projection by dx=10, dy=-5
send_command('set_offset 100 50')    # Set absolute offset x=100, y=50
```

### Recording Commands

Capture a sequence of commands to replay later.

```python
# Start recording
response = send_command('record start')
# Response: "OK Recording started"

# ... send commands to record ...
send_command('happy')
send_command('blink')
send_command('gaze 45 0')

# Stop and save
response = send_command('record stop my_sequence')
# Response: "OK Saved to my_sequence.json"

# Cancel recording without saving
response = send_command('record cancel')
# Response: "OK Recording cancelled"

# Check recording status
response = send_command('record status')
# Response: JSON like {"is_recording": true, "command_count": 3, "duration_ms": 1500}
```

### Playback Commands

Play back recorded sequences.

```python
# Play a recording
response = send_command('play my_sequence')
# Response: "OK Playing my_sequence.json (5000ms)"

# Control playback
response = send_command('pause')
# Response: "OK Paused at 1234ms"

response = send_command('resume')
# Response: "OK Resumed from 1234ms"

response = send_command('stop')
# Response: "OK Playback stopped"

# Seek to specific time
response = send_command('seek 2500')
# Response: "OK Seeked to 2500ms"

# Check playback status
response = send_command('timeline_status')
# Response: JSON with state, filename, position_ms, duration_ms, is_playing
```

### File Management

Manage your recorded timeline files.

```python
# List all recordings
response = send_command('list')
# Response: JSON array like [{"filename": "show.json", "command_count": 42, "duration_ms": 15000}, ...]

# Delete a recording
response = send_command('delete_recording old_sequence')
# Response: "OK Deleted old_sequence.json"

# Rename a recording
response = send_command('rename_recording old_name new_name')
# Response: "OK Renamed old_name.json to new_name.json"

# Download timeline as JSON
json_content = send_command('download_timeline my_sequence')
# Response: Raw JSON content of the timeline file

# Clear all state
response = send_command('reset')
# Response: "OK Reset complete"
```

### Upload Timeline

Upload a pre-made timeline file (multi-step protocol):

```python
import socket
import json

def upload_timeline(filename, json_content):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 5000))
    
    # Step 1: Send upload command
    client.send(f"upload_timeline {filename}\n".encode('utf-8'))
    
    # Step 2: Wait for READY signal
    response = client.recv(1024).decode('utf-8').strip()
    if response != "READY":
        raise Exception(f"Expected READY, got: {response}")
    
    # Step 3: Send JSON content
    client.send(json_content.encode('utf-8'))
    client.send(b"\n")
    
    # Step 4: Send end marker
    client.send(b"END_UPLOAD\n")
    
    # Step 5: Read final response
    response = client.recv(1024).decode('utf-8').strip()
    client.close()
    return response

# Usage
with open('my_timeline.json', 'r') as f:
    timeline_data = f.read()
response = upload_timeline('uploaded_show', timeline_data)
```

## Reading Responses

Commands return three types of responses:

### 1. No Response (Fire-and-Forget)
Expression and animation commands typically return empty strings. Just send and forget.

### 2. Text Response
Recording and playback commands return text status messages:
- `OK ...` — Command succeeded
- `ERROR ...` — Command failed with description

```python
response = send_command('play missing_file')
if response.startswith('ERROR'):
    print(f"Failed: {response}")
```

### 3. JSON Response
Status query commands return JSON data:

```python
import json

response = send_command('timeline_status')
data = json.loads(response)
print(f"State: {data['state']}")
print(f"Position: {data['position_ms']}ms")
print(f"Playing: {data['is_playing']}")
```

## Complete Python Example

The repository includes a complete working example: **`client_example.py`**

This interactive client demonstrates:
- All command types
- Response handling
- Timeline upload protocol
- User-friendly command-line interface

**Run it:**
```bash
python client_example.py
```

**Key snippet from `client_example.py`:**

```python
def send_command(command: str):
    """Send command and handle response"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5000))
        client.send(command.encode('utf-8'))
        client.shutdown(socket.SHUT_WR)
        
        # Read response for status commands
        if command in ["record status", "list", "timeline_status"]:
            response = client.recv(4096).decode('utf-8').strip()
            client.close()
            return json.loads(response)
        else:
            response = client.recv(1024).decode('utf-8').strip()
            client.close()
            return response
    except Exception as e:
        print(f"Error: {e}")
```

## Using Other Languages

Mr. Pumpkin speaks TCP, so any language with socket support works.

### Node.js Example

```javascript
const net = require('net');

function sendCommand(command) {
    return new Promise((resolve, reject) => {
        const client = net.createConnection({ port: 5000 }, () => {
            client.write(command);
            client.end();  // Signal end of command
        });
        
        let response = '';
        client.on('data', (data) => {
            response += data.toString();
        });
        
        client.on('end', () => {
            resolve(response);
        });
        
        client.on('error', reject);
    });
}

// Use it
sendCommand('happy').then(response => console.log(response));
```

### Bash / netcat Example

```bash
# Simple expression change
echo "happy" | nc localhost 5000

# Get status
echo "timeline_status" | nc localhost 5000

# Save to variable
RESPONSE=$(echo "record status" | nc localhost 5000)
echo $RESPONSE
```

### C# Example

```csharp
using System.Net.Sockets;
using System.Text;

string SendCommand(string command)
{
    using var client = new TcpClient("localhost", 5000);
    using var stream = client.GetStream();
    
    // Send command
    byte[] data = Encoding.UTF8.GetBytes(command);
    stream.Write(data, 0, data.Length);
    client.Client.Shutdown(SocketShutdown.Send);
    
    // Read response
    data = new byte[1024];
    int bytes = stream.Read(data, 0, data.Length);
    return Encoding.UTF8.GetString(data, 0, bytes);
}

// Use it
SendCommand("happy");
```

## Advanced: Timeline Files

Timeline files are JSON documents that store recorded command sequences with precise timing.

### Timeline Format

```json
{
  "version": "1.0",
  "created_at": "2024-01-15T10:30:00Z",
  "duration_ms": 5000,
  "commands": [
    {
      "timestamp_ms": 0,
      "command": "happy"
    },
    {
      "timestamp_ms": 1000,
      "command": "blink"
    },
    {
      "timestamp_ms": 2500,
      "command": "gaze 45 30"
    }
  ]
}
```

### Creating Timelines Programmatically

You can create timeline files without recording:

```python
import json
from datetime import datetime

timeline = {
    "version": "1.0",
    "created_at": datetime.utcnow().isoformat() + "Z",
    "duration_ms": 5000,
    "commands": [
        {"timestamp_ms": 0, "command": "neutral"},
        {"timestamp_ms": 500, "command": "eyebrow_raise"},
        {"timestamp_ms": 1000, "command": "happy"},
        {"timestamp_ms": 2000, "command": "blink"},
        {"timestamp_ms": 3000, "command": "gaze 45 0"},
        {"timestamp_ms": 5000, "command": "neutral"}
    ]
}

# Save and upload
with open('custom_sequence.json', 'w') as f:
    json.dump(timeline, f, indent=2)

# Upload to server
upload_timeline('custom_sequence', json.dumps(timeline))
```

### Use Cases

- **Home Automation:** Trigger expressions based on doorbell, weather, or time
- **Halloween Displays:** Synchronized shows with music and lighting
- **Interactive Performances:** React to audience input or sensor data
- **Testing:** Automated test sequences for development
- **Art Installations:** Looping ambient behaviors

## Troubleshooting

### Connection Refused

**Problem:** `Connection refused` error when trying to connect.

**Solutions:**
- Verify Mr. Pumpkin is running: `python pumpkin_face.py`
- Check if port 5000 is open: `netstat -an | grep 5000` (Linux/Mac) or `netstat -an | findstr 5000` (Windows)
- If connecting remotely, use the correct IP address instead of `localhost`
- Check firewall settings

### Port Already in Use

**Problem:** Mr. Pumpkin won't start because port 5000 is busy.

**Solutions:**
- Find what's using port 5000: `lsof -i :5000` (Linux/Mac) or `netstat -ano | findstr :5000` (Windows)
- Kill the conflicting process or change Mr. Pumpkin's port in `pumpkin_face.py`

### No Response Received

**Problem:** Command sent but no response received.

**Solutions:**
- Expression/animation commands intentionally return no response—this is normal
- Make sure you called `shutdown(SHUT_WR)` or closed the write side to signal end of command
- Some commands are fire-and-forget; only status/playback commands return responses
- Check if the command is valid (typos will be silently ignored for some commands)

### Invalid Command

**Problem:** Command doesn't work as expected.

**Solutions:**
- Check spelling and case (commands are case-insensitive, but be careful with arguments)
- Verify command syntax matches the reference above
- For gaze/eyebrow/numeric commands, ensure values are in valid ranges
- Check Mr. Pumpkin's console output for error messages

### Timeline Playback Issues

**Problem:** Timeline won't play or plays incorrectly.

**Solutions:**
- Verify the file exists: `list` command should show it
- Check JSON syntax if you created the file manually
- Ensure timeline version is "1.0"
- Verify `duration_ms` matches the longest `timestamp_ms` in commands
- Stop any active recording before playback: `record cancel` then `play <file>`

### Remote Connection Issues

**Problem:** Can't connect from another machine.

**Solutions:**
- Use the server's IP address instead of `localhost`
- Ensure the server is binding to `0.0.0.0` not just `127.0.0.1` (check `pumpkin_face.py`)
- Configure firewall to allow port 5000
- Verify both machines are on the same network (or proper routing exists)

---

## Next Steps

Now that you understand the protocol, you can:

1. **Experiment** with `client_example.py` to see all commands in action
2. **Build your integration** using the language of your choice
3. **Create timeline sequences** for complex performances
4. **Automate behaviors** based on external triggers (sensors, APIs, schedules)

Have fun bringing your pumpkin to life! 🎃
