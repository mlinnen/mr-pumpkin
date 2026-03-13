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

## Auto-Update

Mr. Pumpkin includes automated update scripts that check for new releases on GitHub and deploy them automatically.

### Usage

**Linux/macOS/Raspberry Pi:**
```bash
./update.sh
```

**Windows (PowerShell):**
```powershell
.\update.ps1
```

The update script will:
1. Check the current installed version against the latest GitHub release
2. Download the new release if available
3. Stop the running pumpkin_face.py process (if running)
4. Deploy the updated files
5. Restart pumpkin_face.py with the same arguments

### Scheduling Automatic Updates

**Linux/macOS/Raspberry Pi (crontab):**

Run daily at 3 AM:
```bash
crontab -e
```

Add this line:
```cron
0 3 * * * /absolute/path/to/mr-pumpkin/update.sh
```

**Windows (Task Scheduler):**

Create a scheduled task using PowerShell:
```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\path\to\mr-pumpkin\update.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "MrPumpkinAutoUpdate" -Description "Daily check for Mr. Pumpkin updates"
```

Or use Task Scheduler GUI:
1. Open Task Scheduler → Create Basic Task
2. Name: "Mr Pumpkin Auto Update"
3. Trigger: Daily at 3:00 AM
4. Action: Start a program
5. Program: `powershell.exe`
6. Arguments: `-ExecutionPolicy Bypass -File C:\path\to\mr-pumpkin\update.ps1`

### Configuration

**Custom Installation Directory:**

Set the `INSTALL_DIR` environment variable to specify where Mr. Pumpkin is installed:

```bash
export INSTALL_DIR=/custom/path/to/mr-pumpkin
./update.sh
```

```powershell
$env:INSTALL_DIR = "C:\custom\path\to\mr-pumpkin"
.\update.ps1
```

### Log File

All update operations are logged to `mr-pumpkin-update.log` in the installation directory with timestamps.

For detailed setup and troubleshooting, see [docs/auto-update.md](docs/auto-update.md).

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

**Custom host and port:**
```bash
python pumpkin_face.py --host 0.0.0.0     # Listen on all network interfaces
python pumpkin_face.py --port 8080        # Listen on port 8080
python pumpkin_face.py --host 0.0.0.0 --port 8080  # Custom host and port
```

**Usage:**
```
python pumpkin_face.py [OPTIONS] [monitor_number]

Options:
  --window              Run in windowed mode (default: fullscreen)
  --fullscreen          Run in fullscreen mode
  --host HOST           IP address or hostname to bind to (default: localhost)
  --port PORT           Port number to listen on (default: 5000)
  -h, --help            Show this help message
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


### WebSocket Interface (Browser Clients)

The pumpkin face server also provides a WebSocket interface on **port 5001** for browser-based control panels and real-time communication.

**Via JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:5001');

ws.onopen = () => {
  ws.send('happy');
  ws.send('blink');
  ws.send('timeline_status');
};

ws.onmessage = (event) => {
  console.log('Response:', event.data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

**WebSocket protocol:**
- Each command is sent as a plain text message (same format as TCP)
- Responses are sent back immediately as text messages
- Empty responses (for animations) are not sent
- Connection can be reused for multiple commands
- Server handles concurrent WebSocket clients simultaneously

**Simple HTML test client:**
```html
<!DOCTYPE html>
<html>
<head>
  <title>Mr. Pumpkin WebSocket Client</title>
</head>
<body>
  <h1>Mr. Pumpkin Control</h1>
  <input type="text" id="command" placeholder="Enter command">
  <button onclick="send()">Send</button>
  <div id="response"></div>
  
  <script>
    const ws = new WebSocket('ws://localhost:5001');
    const responseDiv = document.getElementById('response');
    
    function send() {
      const cmd = document.getElementById('command').value;
      if (cmd) {
        ws.send(cmd);
      }
    }
    
    ws.onmessage = (event) => {
      responseDiv.innerHTML = '<p>' + event.data + '</p>';
    };
  </script>
</body>
</html>
```

**Port allocation:**
- **TCP (port 5000):** Text-based commands, command-line clients, legacy support
- **WebSocket (port 5001):** Browser clients, real-time dashboards, concurrent connections

Both protocols support the same commands and are always available when the server runs.

**Full-featured test client:**
For comprehensive testing and debugging, open `websocket-test-client.html` in your browser. This client includes:
- Connection status monitoring with automatic fallback
- Quick test buttons for common commands
- Timeline upload testing (multi-line JSON)
- Full event logging with timestamps
- Error handling and diagnostics

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

## Skill CLI Tools

The `skill/` package provides three command-line tools:
- `mr-pumpkin-record` — generate and upload a timeline from a natural-language prompt
- `mr-pumpkin-lipsync` — generate a lip-synced timeline from an audio file
- `mr-pumpkin-list-models` — inspect live Gemini/OpenAI model IDs available to your configured account

The generation tools require a `GEMINI_API_KEY` environment variable by default (and optionally `OPENAI_API_KEY` when using the OpenAI provider). The model-listing tool requires the provider-specific API key for the provider you query.

### mr-pumpkin-record

Translates a **natural language prompt** into a timeline animation and uploads it to the Mr. Pumpkin server.

```
usage: mr-pumpkin-record prompt -f FILENAME [--host HOST] [--tcp-port N]
                                [--ws-port N] [--protocol {tcp,ws}]
                                [--dry-run] [--provider PROVIDER]
```

**Arguments**

| Argument | Default | Description |
|---|---|---|
| `prompt` | *(required)* | Natural language description of the desired animation |
| `-f` / `--filename` | *(required)* | Name to store the timeline as on the server (no `.json` extension) |
| `--host` | `localhost` | Mr. Pumpkin server hostname |
| `--tcp-port` | `5000` | TCP port |
| `--ws-port` | `5001` | WebSocket port |
| `--protocol` | `tcp` | Upload protocol: `tcp` or `ws` (WebSocket) |
| `--provider` | `gemini` | LLM provider (currently only `gemini` is supported) |
| `--dry-run` | — | Generate and print the timeline without uploading |

**Environment variables**

- `GEMINI_API_KEY` — required when using the default Gemini provider

**Exit codes:** `0` success · `1` generation/upload error · `2` argument error

**Examples**

```bash
# Generate and upload a surprised/blinking animation
python -m skill.cli "make the pumpkin look surprised then blink" -f my_show

# Generate and upload via WebSocket to a remote host
python -m skill.cli "wave hello" -f wave --host 192.168.1.10 --protocol ws

# Preview the generated timeline without uploading
python -m skill.cli "pumpkin laughs heartily" -f laugh --dry-run
```

---

### mr-pumpkin-lipsync

Generates a **lip-synced** Mr. Pumpkin animation from an audio file using a two-pass pipeline: audio analysis (Gemini multimodal) followed by LLM choreography generation.

```
usage: mr-pumpkin-lipsync audio_file [-f FILENAME] [--prompt PROMPT]
                                     [--host HOST] [--tcp-port N] [--ws-port N]
                                     [--protocol {tcp,ws}]
                                     [--audio-provider PROVIDER]
                                     [--provider PROVIDER] [--model MODEL]
                                     [--audio-model AUDIO_MODEL]
                                     [--api-key KEY] [--dry-run]
```

**Arguments**

| Argument | Default | Description |
|---|---|---|
| `audio_file` | *(required)* | Path to audio file (`.mp3`, `.wav`, `.ogg`) |
| `-f` / `--filename` | audio file stem | Name to store the recording as on the server |
| `--prompt` | — | Artistic guidance for the animation (e.g., `"pumpkin sings this joyfully"`) |
| `--host` | `localhost` | Mr. Pumpkin server hostname |
| `--tcp-port` | `5000` | TCP port |
| `--ws-port` | `5001` | WebSocket port |
| `--protocol` | `tcp` | Upload protocol: `tcp` or `ws` (WebSocket) |
| `--audio-provider` | `gemini` | Provider for audio analysis |
| `--provider` | `gemini` | LLM provider for timeline generation (`gemini` or `openai`) |
| `--model` | — | Override the default LLM model (e.g., `gpt-4o`, `gemini-1.5-pro`) |
| `--audio-model` | — | Override the default audio analysis model |
| `--api-key` | — | API key override (supersedes `GEMINI_API_KEY` / `OPENAI_API_KEY` env vars) |
| `--dry-run` | — | Analyze and generate, print JSON, do NOT upload |

**Environment variables**

- `GEMINI_API_KEY` — required for Gemini provider (default)
- `OPENAI_API_KEY` — required when using `--provider openai`

**Exit codes:** `0` success · `1` generation/analysis/upload error · `2` argument error

**Examples**

```bash
# Basic lip-sync from an MP3 file
python -m skill.lipsync_cli song.mp3 -f my_song

# Add artistic direction and test without uploading
python -m skill.lipsync_cli speech.wav -f story \
  --prompt "pumpkin tells this story with wide-eyed wonder" --dry-run

# Use OpenAI for timeline generation with a specific model
python -m skill.lipsync_cli song.mp3 -f dance \
  --provider openai --model gpt-4o
```

---

### mr-pumpkin-list-models

Lists the live model IDs exposed by Gemini or OpenAI so you can choose valid values for `--model` and related overrides before generating animations.

```
usage: mr-pumpkin-list-models [--provider PROVIDER] [--filter TEXT]
                              [--all] [--api-key KEY]
```

**Arguments**

| Argument | Default | Description |
|---|---|---|
| `--provider` / `-p` | `gemini` | Provider to query: `gemini` or `openai` |
| `--filter` / `-f` | — | Case-insensitive substring filter applied to model IDs |
| `--all` / `-a` | — | Query all supported providers and print grouped results |
| `--api-key` | — | Override the provider API key instead of reading environment variables |

**Environment variables**

- `GEMINI_API_KEY` or `GOOGLE_API_KEY` — required for Gemini queries
- `OPENAI_API_KEY` — required for OpenAI queries

**Exit codes:** `0` success · `1` provider/API/import error · `2` argument error

**Examples**

```bash
# List all Gemini models visible to the configured account
python -m skill.list_models

# Show only OpenAI models containing "gpt-4o"
python -m skill.list_models --provider openai --filter gpt-4o

# Query both providers in one pass
python -m skill.list_models --all
```

---

## Testing

Run the test suite to validate projection mapping and other features:

```bash
# Install development dependencies (if not already installed)
pip install -r requirements-dev.txt

# Run all tests (430+ tests)
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

### Integration Tests

The project includes comprehensive integration tests for dual-protocol operation (TCP + WebSocket):

```bash
# Run integration tests only
pytest tests/test_integration_dual_protocol.py -v

# Run TCP integration tests
pytest tests/test_tcp_integration.py -v
```

**Dual-Protocol Integration Tests** (`test_integration_dual_protocol.py`) validate:

1. **Identical Responses** (5 tests)
   - Both TCP and WebSocket return identical responses for the same commands
   - Status queries (timeline_status, recording_status) return consistent JSON
   - List operations return matching results

2. **Protocol Switching** (3 tests)
   - Commands work when alternating between TCP and WebSocket
   - No state corruption when switching protocols mid-session
   - 10+ command sequences alternating protocols

3. **Concurrent Commands** (2 tests)
   - Multiple concurrent commands from both protocols execute correctly
   - Concurrent status queries from both protocols

4. **Error Handling Consistency** (3 tests)
   - Invalid commands return errors on both protocols
   - Malformed commands handled gracefully
   - Nonexistent file errors consistent across protocols

5. **Timeline Upload/Download** (3 tests)
   - Upload timeline via TCP, verify via WebSocket
   - Upload timeline via WebSocket, verify via TCP
   - Download same timeline via both protocols yields identical results

6. **State Synchronization** (3 tests)
   - Recording state visible from both protocols
   - Playback state visible from both protocols
   - Expression changes propagate across protocols

7. **Connection Resilience** (2 tests)
   - TCP disconnect doesn't affect WebSocket
   - WebSocket disconnect doesn't affect TCP

8. **Large Payloads** (2 tests)
   - Large timelines (>100KB JSON, 200+ commands) work on both protocols

9. **Stress Testing** (1 test)
   - 50 rapid commands alternating TCP/WebSocket

10. **Playback Integration** (2 tests)
    - Start playback on one protocol, control via the other
    - Cross-protocol pause/resume/stop

11. **Clean Shutdown** (1 test)
    - Graceful disconnect on both protocols without orphaned resources

**Total:** 27 integration tests covering all critical dual-protocol scenarios.

## Development

Mr. Pumpkin was built using [**Squad**](https://github.com/bradygaster/squad) — an agentic coding solution created by [Brady Gaster](https://github.com/bradygaster) that orchestrates a team of specialized AI agents to collaboratively design, build, test, and document software.

### The Squad Team

The following AI agents collaborated to develop Mr. Pumpkin, drawn from the **Arcane** universe:

| Agent | Role | Responsibility |
|-------|------|----------------|
| 🏗️ **Jinx** | Lead | Architecture, scope decisions, code review |
| ⚛️ **Ekko** | Graphics Dev | 2D rendering, animations, facial expressions |
| 🔧 **Vi** | Backend Dev | Network socket server, command handling, timeline playback |
| 🧪 **Mylo** | Tester | Test suite, quality assurance, edge cases |
| 📋 **Scribe** | Memory & Logging | Decisions, session logs, cross-agent context |
| 🔄 **Ralph** | Work Monitor | Work queue, backlog tracking, issue triage |

> Want to build your own project with an AI team like this? Check out [Brady Gaster's Squad](https://github.com/bradygaster/squad).

## License

MIT
