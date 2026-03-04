---
layout: default
title: Home
permalink: /
---

<div class="hero">
  <span class="hero-logo">🎃</span>
  <h1>Mr. Pumpkin</h1>
  <p class="tagline">Animate the darkness, project your face</p>
  <p class="description">
    An animated 2D pumpkin face that responds to network commands in real time.
    Designed for projection mapping onto 3D surfaces — pure black-and-white contrast,
    7 expressions, dual TCP/WebSocket control, and an AI recording skill.
  </p>
  <div class="hero-actions">
    <a href="/mr-pumpkin/installation" class="btn btn-primary">🚀 Get Started</a>
    <a href="https://github.com/mlinnen/mr-pumpkin" class="btn btn-outline" target="_blank" rel="noopener">⭐ GitHub</a>
  </div>
</div>

<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-number">7</div>
    <div class="stat-label">Expressions</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">2</div>
    <div class="stat-label">Protocols (TCP + WS)</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">430+</div>
    <div class="stat-label">Tests</div>
  </div>
  <div class="stat-card">
    <div class="stat-number">AI</div>
    <div class="stat-label">Recording Skill</div>
  </div>
</div>

<div class="demo-placeholder">
  <span class="demo-icon">🎃</span>
  <strong>Projection demo coming soon</strong><br>
  Screenshot / demo GIF will appear here
</div>

## About Mr. Pumpkin

Mr. Pumpkin is an animated 2D pumpkin face that can be controlled remotely via TCP or WebSocket commands. Designed for projection mapping onto 3D surfaces, it renders expressive faces using high-contrast black-and-white graphics optimized for real-world projection scenarios.

## What's New

### [What's New / Changelog](what-is-new.md)
Full release history — every version's added features, fixes, and changes.

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

## Behind the Scenes

### [Development Story](development-story.md)
How Mr. Pumpkin was built using [Brady Gaster's Squad](https://github.com/bradygaster/squad) agentic coding solution — meet the AI team (cast from the Arcane universe) that designed, built, and tested this project.

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
