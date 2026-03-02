# Mr. Pumpkin — Documentation

Mr. Pumpkin is an animated 2D pumpkin face that can be controlled remotely via TCP or WebSocket commands. Designed for projection mapping onto 3D surfaces, it renders expressive faces using high-contrast black-and-white graphics optimized for real-world projection scenarios.

## User Guides

### [Getting Started: Installation](installation.md)
How to install Mr. Pumpkin and set it up to run automatically as a system service on Linux (systemd) or Windows (Task Scheduler/NSSM).

### [Keeping Mr. Pumpkin Updated](auto-update.md)
Automated update scripts for keeping your Mr. Pumpkin installation current with the latest releases from GitHub.

### [Building a Client](building-a-client.md)
Developer guide for creating client applications that send commands to Mr. Pumpkin via TCP (port 5000) or WebSocket (port 5001).

### [Recording Skill](recording-skill.md)
Describe an animation in plain English and have it automatically generated and uploaded to your pumpkin server using an LLM (Google Gemini).

### [Timeline JSON Schema](timeline-schema.md)
Reference for the timeline JSON format: top-level structure, full command vocabulary, timing guidelines, and validation rules.

## Quick Start

Once installed, run Mr. Pumpkin with:

```bash
# Fullscreen on default monitor (projection mapping)
python pumpkin_face.py

# Windowed mode (testing)
python pumpkin_face.py --window

# Fullscreen on specific monitor (multi-display setups)
python pumpkin_face.py 1
```

Send commands via TCP on port 5000 or WebSocket on port 5001. See the [client guide](building-a-client.md) for examples.

Press **ESC** to exit.
