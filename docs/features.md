---
layout: page
title: Features
permalink: /features
description: Key capabilities of Mr. Pumpkin — the animated projection-mapping pumpkin face.
---

# Features

Mr. Pumpkin is a fully-featured animated pumpkin face built for real-world projection installations.

<div class="features-grid">
  <div class="feature-card">
    <span class="feature-icon">😄</span>
    <h3>7 Facial Expressions</h3>
    <p>Neutral, happy, sad, angry, surprised, scared, and sleeping — all with smooth animated transitions.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">🔌</span>
    <h3>Dual Protocol Control</h3>
    <p>TCP socket on port 5000 and WebSocket on port 5001 — control from any language or browser simultaneously.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">🎥</span>
    <h3>Record & Playback</h3>
    <p>Record command sequences with millisecond timing, save as JSON timelines, and replay frame-accurately.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">🤖</span>
    <h3>AI Recording Skill</h3>
    <p>Describe an animation in plain English — Google Gemini generates a full timeline JSON and uploads it automatically.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">👁️</span>
    <h3>Gaze & Eye Control</h3>
    <p>Point both eyes or each eye independently at any angle. Blink, wink, and roll eyes via single commands.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">🎃</span>
    <h3>Projection-Optimised</h3>
    <p>Pure black background (0,0,0) and white features (255,255,255) deliver 21:1 contrast for reliable projection.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">🖥️</span>
    <h3>Multi-Monitor</h3>
    <p>Fullscreen or windowed on any connected monitor. Pixel-level projection alignment with arrow-key jog controls.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">🔄</span>
    <h3>Auto-Update</h3>
    <p>Shell and PowerShell scripts check GitHub Releases, download, and hot-deploy updates automatically.</p>
  </div>
  <div class="feature-card">
    <span class="feature-icon">🧪</span>
    <h3>430+ Tests</h3>
    <p>Comprehensive test suite: projection colours, contrast ratios, all expressions, dual-protocol, stress tests.</p>
  </div>
</div>

## Full Capabilities

### Expressions
- `neutral` · `happy` · `sad` · `angry` · `surprised` · `scared` · `sleeping`
- Smooth animated transitions between all states

### Animation Commands
- `blink` — blink both eyes
- `wink_left` / `wink_right` — single-eye winks
- `roll_clockwise` / `roll_counterclockwise` — eye roll animations
- `raise_eyebrows` / `lower_eyebrows` — symmetric eyebrow control
- `raise_left_eyebrow` / `lower_left_eyebrow` — individual eyebrow control
- `raise_right_eyebrow` / `lower_right_eyebrow`
- `wiggle_nose` / `reset_nose` — nose animation

### Gaze Control
```
gaze <x> <y>               # Both eyes — degrees (-90 to +90)
gaze <x1> <y1> <x2> <y2>  # Left and right eyes independently
```

### Recording & Playback
- `record_start` / `record_stop <name>` / `record_cancel`
- `list_recordings` · `play <name>` · `pause` · `resume` · `stop`
- `seek <position_ms>` — jump to any point
- `download_timeline <name>` · `upload_timeline <name> <json_file>`
- `play_recording` inside timelines — embed one recording inside another (up to 5 levels deep)

### Network Protocols
- **TCP (port 5000)** — plain-text commands, works with netcat, PowerShell, any language
- **WebSocket (port 5001)** — browser-native, real-time dashboards, concurrent clients
- Both protocols share the same command set and return identical responses

### Keyboard Shortcuts (local)
`1`–`7` for expressions · `B` blink · `L`/`R` wink · `C`/`X` roll eyes · `U`/`J` eyebrows · Arrow keys for projection alignment · `ESC` to exit
