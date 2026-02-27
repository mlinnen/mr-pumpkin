# Mr. Pumpkin - Fullscreen Pumpkin Face Renderer

A standalone Python program that renders an animated pumpkin face on fullscreen and responds to network commands to change facial expressions.

## Features

- **Fullscreen rendering** with 2D vector graphics
- **7 facial expressions**: neutral, happy, sad, angry, surprised, scared, sleeping
- **Smooth animations** between expression transitions
- **Network socket server** on port 5000 for receiving commands
- **Keyboard shortcuts** for quick testing (1-7 keys for expressions, arrow keys for alignment, B/L/R for animations, U/J for eyebrows, [ ] for individual eyebrows, C/X for eye rolling)
- **Customizable appearance** (colors, sizes, animation speeds)
- **Command recording & playback**: Record command sequences and replay them with frame-accurate timing
  - Record commands into timelines with automatic timestamping
  - Play, pause, resume, stop, and seek through recorded sequences
  - List, delete, and rename recorded timelines
- **Gaze control**: Direct eye positioning with individual eye control
- **Eye animations**: Blink, wink, and roll eyes
- **Eyebrow control**: Raise, lower, and control individual eyebrows

## Installation

### Option 1: Download Release Package (Recommended)

1. **Download the latest release** from [GitHub Releases](https://github.com/mlinnen/mr-pumpkin/releases)
2. **Extract the ZIP file:**
   ```bash
   unzip mr-pumpkin-v0.1.0.zip
   cd mr-pumpkin-v0.1.0
   ```
3. **Run the install script:**
   
   **Linux/macOS/Raspberry Pi:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
   
   **Windows (PowerShell):**
   ```powershell
   .\install.ps1
   ```

The install script will:
- Install SDL2 system dependencies (Linux/Raspberry Pi only)
- Install Python dependencies via pip
- Provide usage instructions

### Option 2: Install from Source

1. Clone the repository and install dependencies:
```bash
git clone https://github.com/mlinnen/mr-pumpkin.git
cd mr-pumpkin
pip install -r requirements.txt
```

**Note:** On Raspberry Pi or Linux, you may need to install SDL2 system libraries first:
```bash
sudo apt-get update
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
```

### Development Setup

To set up a development environment with testing capabilities:

```bash
pip install -r requirements-dev.txt
```

This installs all production dependencies plus pytest for running the test suite.

## Usage

### Run the pumpkin face application:

**Fullscreen (default on monitor 0):**
```bash
python pumpkin_face.py
```

**Fullscreen on specific monitor:**
```bash
python pumpkin_face.py 0      # First monitor
python pumpkin_face.py 1      # Second monitor
python pumpkin_face.py 2      # Third monitor
```

**Windowed mode:**
```bash
python pumpkin_face.py --window           # Windowed on monitor 0
python pumpkin_face.py 1 --window         # Windowed on monitor 1
```

**Usage:**
```
python pumpkin_face.py [monitor_number] [--window|--fullscreen]
```

The program will list available monitors and run on your selected output. Press ESC to exit.

### Send commands via network socket:

**Using the example client (interactive menu):**
```bash
python client_example.py
```

This provides an interactive menu with commands for:
- Changing expressions (neutral, happy, sad, angry, surprised, scared, sleeping)
- Animation controls (blink, roll eyes, control eyebrows)
- Gaze control (point eyes at angles)
- Recording and playback:
  - `record start` - Begin recording
  - `record stop <filename>` - Save a recording
  - `record cancel` - Discard recording
  - `record status` - Check recording state
  - `list` - View all recordings
  - `download_timeline <filename>` - Download a recording file as JSON
  - `play <filename>` - Play a recording
  - `upload_timeline <filename> <json_file>` - Upload a recording file from disk
  - `pause` / `resume` / `stop` - Control playback
  - `seek <position_ms>` - Jump to position
  - `timeline_status` - Check playback state

**Via Python:**
```python
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 5000))
client.send(b'happy')
response = client.recv(1024)  # Some commands return responses
client.close()
```

**Via command line (netcat/nc):**
```bash
echo "happy" | nc localhost 5000
echo "record start" | nc localhost 5000
echo "record stop my_recording" | nc localhost 5000
echo "play my_recording" | nc localhost 5000
echo "timeline_status" | nc localhost 5000
```

**Via PowerShell:**
```powershell
$socket = New-Object System.Net.Sockets.TcpClient
$socket.Connect('localhost', 5000)
$stream = $socket.GetStream()
[byte[]]$bytes = [System.Text.Encoding]::ASCII.GetBytes("happy")
$stream.Write($bytes, 0, $bytes.Length)
$stream.Close()
```

## Supported Commands

### Expressions
- `neutral` - Default expression
- `happy` - Smiling face
- `sad` - Frowning face
- `angry` - Angry eyes and mouth
- `surprised` - Wide eyes, open mouth
- `scared` - Frightened expression
- `sleeping` - Eyes closed (sleeping)

### Recording & Playback
- `record_start` or `record start` - Begin recording commands
- `record_stop <filename>` or `record stop <filename>` - Stop recording and save with filename
- `record_cancel` or `record cancel` - Discard current recording without saving
- `recording_status` or `record status` - Show recording state (is_recording, command_count, duration_ms)
- `list_recordings` or `list` - Show all available recordings
- `delete_recording <filename>` - Remove a saved recording
- `rename_recording <old_name> <new_name>` - Rename a saved recording
- `upload_timeline <filename> <json_file>` - Upload a recording file from disk (filename: name to store as, json_file: local path to JSON file)
- `download_timeline <filename>` - Download a recording file as JSON string (filename: name of recording to download)
- `play <filename>` - Start playing a recorded timeline
- `pause` - Pause current playback
- `resume` - Resume from paused state
- `stop` - Stop playback and return to start
- `seek <position_ms>` - Jump to specific position in recording
- `timeline_status` - Show current playback state (state, filename, position, duration, is_playing)

### Animation Controls
- `blink` - Blink both eyes
- `wink_left` - Wink left eye only
- `wink_right` - Wink right eye only
- `roll_clockwise` - Roll eyes clockwise
- `roll_counterclockwise` - Roll eyes counter-clockwise
- `raise_eyebrows` - Raise both eyebrows
- `lower_eyebrows` - Lower both eyebrows
- `raise_left_eyebrow` - Raise left eyebrow only
- `lower_left_eyebrow` - Lower left eyebrow only
- `raise_right_eyebrow` - Raise right eyebrow only
- `lower_right_eyebrow` - Lower right eyebrow only

### Gaze Control
- `gaze <x> <y>` - Point both eyes at angle (x, y in degrees, -90 to +90)
- `gaze <x1> <y1> <x2> <y2>` - Point left and right eyes independently

### Nose Animation
- `wiggle_nose` - Animate nose wiggle
- `reset_nose` - Stop nose animation and return to neutral

## Recording Storage

### Recording File Format

Recordings are stored as JSON files in the user's home directory. Each recording contains:

**File location:** `~/.mr-pumpkin/recordings/{filename}.json`

**File structure:**
```json
{
  "version": "1.0",
  "duration_ms": 5230,
  "commands": [
    {
      "time_ms": 0,
      "command": "happy"
    },
    {
      "time_ms": 500,
      "command": "blink"
    },
    {
      "time_ms": 2000,
      "command": "roll_clockwise"
    }
  ]
}
```

**Field descriptions:**
- `version` - Format version for future compatibility (currently "1.0")
- `duration_ms` - Total duration of the recording in milliseconds
- `commands` - Array of commands, each with:
  - `time_ms` - Timestamp in milliseconds from the start of the recording
  - `command` - The pumpkin command to execute at this time (e.g., "happy", "blink", "gaze")
  - `args` (optional) - Additional command arguments for commands that need them (e.g., gaze angles)

### Recording Directory

All recordings are stored in `~/.mr-pumpkin/recordings/`. The directory is created automatically when you save your first recording.

- **On Windows:** `C:\Users\{username}\.mr-pumpkin\recordings\`
- **On macOS/Linux:** `/Users/{username}/.mr-pumpkin/recordings/` or `~/.mr-pumpkin/recordings/`

You can browse recordings in this directory to:
- Back up important sequences
- Edit timeline files directly (JSON format is human-readable)
- Share recordings with others
- Delete old recordings manually if desired

## Keyboard Controls

While the application is running:
- `1` → Neutral
- `2` → Happy
- `3` → Sad
- `4` → Angry
- `5` → Surprised
- `6` → Scared
- `7` → Sleeping
- `ESC` → Exit fullscreen

**Projection Alignment (Jog Controls):**
- `Arrow Keys` → Nudge projection in any direction (5px steps)
- `0` → Reset projection offset to center

**Animation Controls:**
- `B` → Blink
- `L` → Wink left
- `R` → Wink right
- `C` → Roll eyes clockwise
- `X` → Roll eyes counter-clockwise
- `U` → Raise both eyebrows
- `J` → Lower both eyebrows
- `[` → Raise left eyebrow (Shift+[ to lower)
- `]` → Raise right eyebrow (Shift+] to lower)

## Customization

Edit `pumpkin_face.py` to customize:
- Colors: Modify `PUMPKIN_COLOR`, `EYE_COLOR`, `MOUTH_COLOR`, etc.
- Animation speed: Change `self.transition_speed`
- Face size: Adjust `pumpkin_radius`
- Socket port: Change the port in `_run_socket_server()`
- Recordings storage path: Modify the `recordings_dir` in the FileManager class

### Headless Mode

The application can run in headless mode (without a display) for automation and CI/CD environments. In this mode:
- The TCP socket server runs fully functional
- All commands work normally (expressions, animations, recording/playback)
- The pygame display is optional and gracefully skipped if unavailable
- Useful for running the pumpkin server on a headless Linux machine that communicates with a remote display

## Architecture

- **pumpkin_face.py**: Main application with rendering and network server
- **client_example.py**: Example client for sending commands
- **tests/**: Test suite directory with all test modules
- **requirements.txt**: Production dependencies (pygame only)
- **requirements-dev.txt**: Development dependencies (includes pytest for testing)

## Testing

Run the test suite to validate projection mapping and other features:

```bash
# Install development dependencies (if not already installed)
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run specific test file
pytest tests/test_projection_mapping.py -v

# Run specific test class
pytest tests/test_projection_mapping.py::TestProjectionMappingColors -v

# Run with detailed output
pytest -vv
```

The test suite validates:
- Black background (RGB 0,0,0) for projection mapping
- White features (RGB 255,255,255) for eyes, nose, mouth
- Minimum 15:1 contrast ratio for reliable projection
- All expression states render correctly
- Resolution independence
- Transition behavior

## License

MIT
