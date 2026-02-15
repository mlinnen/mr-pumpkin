# Mr. Pumpkin - Fullscreen Pumpkin Face Renderer

A standalone Python program that renders an animated pumpkin face on fullscreen and responds to network commands to change facial expressions.

## Features

- **Fullscreen rendering** with 2D vector graphics
- **6 facial expressions**: neutral, happy, sad, angry, surprised, scared
- **Smooth animations** between expression transitions
- **Network socket server** on port 5000 for receiving commands
- **Keyboard shortcuts** for quick testing (1-6 keys)
- **Customizable appearance** (colors, sizes, animation speeds)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

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

**Using the example client:**
```bash
python client_example.py
```

**Via Python:**
```python
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 5000))
client.send(b'happy')
client.close()
```

**Via command line (netcat/nc):**
```bash
echo "happy" | nc localhost 5000
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

## Supported Expressions

- `neutral` - Default expression
- `happy` - Smiling face
- `sad` - Frowning face
- `angry` - Angry eyes and mouth
- `surprised` - Wide eyes, open mouth
- `scared` - Frightened expression

## Keyboard Controls

While the application is running:
- `1` → Neutral
- `2` → Happy
- `3` → Sad
- `4` → Angry
- `5` → Surprised
- `6` → Scared
- `ESC` → Exit fullscreen

## Customization

Edit `pumpkin_face.py` to customize:
- Colors: Modify `PUMPKIN_COLOR`, `EYE_COLOR`, etc.
- Animation speed: Change `self.transition_speed`
- Face size: Adjust `pumpkin_radius`
- Socket port: Change the port in `_run_socket_server()`

## Architecture

- **pumpkin_face.py**: Main application with rendering and network server
- **client_example.py**: Example client for sending commands
- **requirements.txt**: Python dependencies (pygame)

## License

MIT
