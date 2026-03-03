---
layout: page
title: Documentation
permalink: /documentation
description: Full documentation index for Mr. Pumpkin.
---

# Documentation

<div class="doc-grid">
  <div class="doc-card">
    <a href="/mr-pumpkin/installation">
      <h3>🚀 Installation &amp; Usage</h3>
      <p>Install Mr. Pumpkin, set it up as a system service, and get running on Linux, Windows, or Raspberry Pi.</p>
    </a>
  </div>
  <div class="doc-card">
    <a href="/mr-pumpkin/building-a-client">
      <h3>🔌 Building a Client</h3>
      <p>Connect to Mr. Pumpkin from any language via TCP or WebSocket. Full command reference and code examples.</p>
    </a>
  </div>
  <div class="doc-card">
    <a href="/mr-pumpkin/recording-skill">
      <h3>🤖 AI Recording Skill</h3>
      <p>Describe an animation in plain English and have Google Gemini generate and upload the timeline automatically.</p>
    </a>
  </div>
  <div class="doc-card">
    <a href="/mr-pumpkin/timeline-schema">
      <h3>📋 Timeline JSON Schema</h3>
      <p>Full reference for the timeline format: structure, command vocabulary, timing rules, and validation.</p>
    </a>
  </div>
  <div class="doc-card">
    <a href="/mr-pumpkin/auto-update">
      <h3>🔄 Auto-Update Guide</h3>
      <p>Automated update scripts for Linux/macOS and Windows — cron job or Task Scheduler setup.</p>
    </a>
  </div>
  <div class="doc-card">
    <a href="/mr-pumpkin/what-is-new">
      <h3>📣 What's New</h3>
      <p>Full release history and changelog — every version's features, fixes, and changes.</p>
    </a>
  </div>
</div>

---

## Quick Reference

### Run the application

```bash
python pumpkin_face.py             # Fullscreen, default monitor
python pumpkin_face.py 1           # Fullscreen, second monitor
python pumpkin_face.py --window    # Windowed mode
```

### Send a command

```bash
# netcat
echo "happy" | nc localhost 5000

# Python
import socket
s = socket.socket()
s.connect(('localhost', 5000))
s.send(b'happy')
s.close()
```

```javascript
// WebSocket (browser / Node.js)
const ws = new WebSocket('ws://localhost:5001');
ws.onopen = () => ws.send('happy');
```

### Version History

See the full [What's New](/mr-pumpkin/what-is-new) page for the complete changelog.

| Version | Date | Highlights |
|---------|------|------------|
| 0.5.10 | 2026-03-03 | Recording chaining, `help` command |
| 0.5.8 | 2026-03-02 | AI recording skill (Google Gemini) |
| 0.5.0 | 2026-02-27 | WebSocket dual-protocol support |
| 0.4.1 | 2026-02-26 | Timeline upload/download |

