---
layout: page
title: Timeline JSON Schema
permalink: /timeline-schema
description: Reference for the timeline JSON format used by Mr. Pumpkin's recording system.
---

# Timeline JSON Schema

A timeline is a JSON file that drives Mr. Pumpkin's animations. It defines a sequence of timed commands that control expressions, eye movements, eyebrows, head position, and more.

---

## Top-Level Structure

```json
{
  "version": "1.0",
  "duration_ms": 3500,
  "audio_file": "my_song.mp3",
  "commands": [...]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | ✓ | Format version — must be exactly `"1.0"` |
| `duration_ms` | integer | ✓ | Total animation length in milliseconds; must be ≥ last command's `time_ms` |
| `audio_file` | string | ✗ | Filename of audio to play in sync with the animation, relative to `~/.mr-pumpkin/recordings/`. When present, the playback engine auto-starts audio at t=0. Audio errors are non-fatal — a warning is logged and animation continues. |
| `commands` | array | ✓ | Ordered list of command objects; must contain at least one command |

---

## Command Object

```json
{
  "time_ms": 500,
  "command": "set_expression",
  "args": { "expression": "happy" }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `time_ms` | integer | ✓ | Timestamp from timeline start in milliseconds; must be non-negative and in ascending order |
| `command` | string | ✓ | Command name (see vocabulary below) |
| `args` | object | ✗ | Command arguments; omit if command takes no args |

---

## Command Vocabulary

### Expression

| Command | Args | Description |
|---------|------|-------------|
| `set_expression` | `expression`: `neutral` \| `happy` \| `sad` \| `angry` \| `surprised` \| `scared` \| `sleeping` | Set facial expression |

Always open an animation with `set_expression` to establish a base state. Allow 300–600ms between expression changes.

---

### Eyes

| Command | Args | Description |
|---------|------|-------------|
| `blink` | — | Both eyes blink |
| `wink_left` | — | Left eye wink |
| `wink_right` | — | Right eye wink |
| `gaze` | `x`, `y` (both eyes) **or** `lx`, `ly`, `rx`, `ry` (independent) | Rotate eyes in degrees; range −90 to +90; ±45° natural, ±60° dramatic |
| `roll_clockwise` | — | Both eyes roll clockwise (~1000ms) |
| `roll_counterclockwise` | — | Both eyes roll counterclockwise (~1000ms) |

---

### Eyebrows

| Command | Args | Description |
|---------|------|-------------|
| `eyebrow_raise` | — | Raise both eyebrows |
| `eyebrow_lower` | — | Lower both eyebrows |
| `eyebrow_raise_left` | — | Raise left eyebrow |
| `eyebrow_lower_left` | — | Lower left eyebrow |
| `eyebrow_raise_right` | — | Raise right eyebrow |
| `eyebrow_lower_right` | — | Lower right eyebrow |
| `eyebrow_reset` | — | Return eyebrows to neutral |
| `eyebrow` | `value` (both) **or** `left`, `right` (independent) | Set eyebrow offset in pixels; typical range −50 to +50 |

---

### Head

| Command | Args | Description |
|---------|------|-------------|
| `turn_left` | `amount` (px, default 50) | Shift head left |
| `turn_right` | `amount` (px, default 50) | Shift head right |
| `turn_up` | `amount` (px, default 50) | Shift head up |
| `turn_down` | `amount` (px, default 50) | Shift head down |
| `center_head` | — | Return head to neutral position |

Typical `amount` range: 50–150 px. Allow 300–500ms between head movements.

---

### Nose

| Command | Args | Description |
|---------|------|-------------|
| `twitch_nose` | `magnitude` (float, default 50.0) | Quick nose twitch |
| `wiggle_nose` | `magnitude` (float, default 50.0) | Nose wiggle |
| `scrunch_nose` | `magnitude` (float, default 50.0) | Scrunch nose |
| `reset_nose` | — | Return nose to neutral |

---

### Mouth

| Command | Args | Description |
|---------|------|-------------|
| `mouth_closed` | — | Lips together (M, B, P sounds) |
| `mouth_open` | — | Open jaw (AH, AA sounds) |
| `mouth_wide` | — | Wide spread lips (EE, IH sounds) |
| `mouth_rounded` | — | Rounded lips (OO, OH sounds) |
| `mouth_neutral` | — | Release mouth to expression-driven control |
| `mouth` | `viseme`: `closed` \| `open` \| `wide` \| `rounded` \| `neutral` | Set mouth by viseme name |

Use mouth commands to synchronize facial animation with speech synthesis. Viseme-based mouth shapes support natural lip-sync during dialogue.

---

### Chaining / Sub-Recordings

| Command | Args | Description |
|---------|------|-------------|
| `play_recording` | `filename` (string, recording name) | Load and play another recording to completion, then resume the parent timeline |

See [Recording Chaining](#recording-chaining) below for full details.

---

### Projection

These commands adjust display alignment and are not normally used in performative animations.

| Command | Args | Description |
|---------|------|-------------|
| `set_offset` | `x`, `y` (int) | Set absolute projection offset |
| `jog_offset` | `dx`, `dy` (int) | Adjust projection offset by delta |
| `projection_reset` | — | Reset projection to origin |

---

## Timing Guidelines

| Action | Duration | Safe gap after |
|--------|----------|----------------|
| Expression transition | 400–600ms | 300–500ms |
| Blink / wink | 200–300ms | 100–300ms |
| Eye gaze | 200–800ms | 50–100ms |
| Eye roll | ~1000ms | ≥500ms |
| Eyebrow movement | 150–400ms | 100–200ms |
| Head turn | 300–600ms | 300–500ms |
| Nose animation | 200–600ms | 100–200ms |
| Projection command | ~50ms | — |

**Key rules:**
- Default safe gap between any two commands: 100–150ms minimum
- Expression commands need the most breathing room (300–500ms apart)
- Eye movements can chain faster (50–100ms)
- Head movements are exclusive — wait 300–600ms before layering other major movements

---

## Recording Chaining

A timeline can embed another recording using `play_recording`. When the playback engine encounters this command it:

1. **Pushes** the current timeline state (position, progress) onto an internal stack.
2. **Loads** the named sub-recording from the recordings directory (`.json` extension is optional).
3. **Plays** the sub-recording to completion.
4. **Pops** the parent state and resumes from the point immediately after the `play_recording` command.

**Nesting depth:** Up to **5 levels** of nesting are supported. If a `play_recording` command is encountered when the stack is already at depth 5 it is silently skipped and an error is logged; parent playback continues uninterrupted.

**Missing files:** If the named recording file cannot be found or loaded, the error is logged and the `play_recording` command is skipped. Playback of the parent timeline continues normally.

**Stopping:** Calling `stop` clears the entire stack — all nested contexts are abandoned and playback halts immediately.

The pumpkin face never sees the `play_recording` command. It is intercepted and handled entirely by the playback engine before any callback to the face renderer.

---

## Validation Rules

1. `version` must be exactly `"1.0"`
2. `time_ms` values must be non-negative integers in **strictly ascending order**
3. `duration_ms` must be ≥ the last command's `time_ms` plus its execution duration
4. `commands` array must be non-empty
5. All `command` names must be from the vocabulary above
6. `args` must only include valid keys for the given command
7. `play_recording` args must include a non-empty `filename` key

---

## Example

```json
{
  "version": "1.0",
  "duration_ms": 3500,
  "commands": [
    {"time_ms": 0,    "command": "set_expression", "args": {"expression": "neutral"}},
    {"time_ms": 500,  "command": "blink"},
    {"time_ms": 1000, "command": "set_expression", "args": {"expression": "happy"}},
    {"time_ms": 1600, "command": "gaze",            "args": {"x": 30, "y": 0}},
    {"time_ms": 2100, "command": "eyebrow_raise"},
    {"time_ms": 2600, "command": "wink_right"},
    {"time_ms": 3200, "command": "gaze",            "args": {"x": 0, "y": 0}}
  ]
}
```

### Example with Recording Chaining

```json
{
  "version": "1.0",
  "duration_ms": 5000,
  "commands": [
    {"time_ms": 0,    "command": "set_expression", "args": {"expression": "neutral"}},
    {"time_ms": 500,  "command": "play_recording",  "args": {"filename": "slow_blink"}},
    {"time_ms": 1000, "command": "set_expression", "args": {"expression": "happy"}},
    {"time_ms": 1500, "command": "play_recording",  "args": {"filename": "excited_wiggle"}},
    {"time_ms": 4500, "command": "set_expression", "args": {"expression": "neutral"}}
  ]
}
```

In this example, `slow_blink` plays to completion before the expression switches to `happy`, and then `excited_wiggle` plays in full before the final neutral expression. Each sub-recording's duration determines when the parent timeline resumes.
