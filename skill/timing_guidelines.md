# Animation Timing & Choreography Guidelines

This document specifies how long animations take and how to space them naturally. These guidelines are for AI-driven timeline generation. Follow these timings to create animations that feel smooth and believable.

---

## 1. Duration Guidelines Per Command

Each command has a recommended animation duration. This is how long the command "occupies" on the timeline before the next command should start.

| Command | Base Duration | Notes |
|---------|---|---|
| `blink` | 200–300ms | Full blink cycle (close + hold + open). Default 250ms. |
| `wink_left` / `wink_right` | 300–500ms | Single eye wink (asymmetrical blink). Default 400ms. |
| `set_expression` | 300–600ms | Smooth transition between expressions. Shorter for subtle shifts (neutral→happy: 300ms), longer for dramatic changes (neutral→scared: 600ms). |
| `eyebrow_raise` / `eyebrow_lower` | 200–400ms | Individual brow movements. Simple raise/lower: 250ms. Multi-step (both + offset): 400ms. |
| `eyebrow_raise_left` / `eyebrow_lower_left` / `eyebrow_raise_right` / `eyebrow_lower_right` | 150–300ms | Single-side brow. Usually 200ms. |
| `eyebrow_reset` | 200–300ms | Return to neutral after offsets. |
| `gaze` | 200–800ms | Depends on angle. Small shifts (±10°): 200ms. Medium (±30°): 400ms. Large (±60°): 600ms. Extreme (±80°): 800ms. |
| `roll_clockwise` / `roll_counterclockwise` | 1000–1500ms | Full 360° pupil rotation. Default 1000ms (1 second). |
| `turn_left` / `turn_right` / `turn_up` / `turn_down` | 300–600ms | Head movement. Small shifts (50px): 300ms. Medium (100px): 400ms. Large (150px+): 600ms. |
| `center_head` | 400–600ms | Return head to neutral. If coming from far offset: 600ms. From close: 300ms. |
| `twitch_nose` | 200–300ms | Rapid left-right sniffing. Default 250ms. |
| `wiggle_nose` | 400–600ms | Side-to-side wobble. Default 500ms. |
| `scrunch_nose` | 300–500ms | Vertical compression (disgust). Default 400ms. |
| `reset_nose` | Immediate | No animation; takes ~50ms. |
| `eyebrow` (numeric) | 200–400ms | Direct eyebrow position. |
| `jog_offset` / `set_offset` | Immediate | Instant projection shifts (for alignment, not animation). |
| `projection_reset` | Immediate | Instant return to center. |

---

## 2. Pacing Guidelines – Gaps Between Commands

Commands need time to complete before the next command starts. Too-small gaps cause visual glitches (overlapping animations); too-large gaps feel sluggish.

### Safe Gap Rules

1. **Default gap (most cases): 100–150ms**
   - Between any two sequential commands, leave at least 100ms for the previous command to finish rendering.
   - This is the "safety buffer."

2. **Expression transitions need breathing room: 300–500ms minimum**
   - After `set_expression`, wait 300–500ms before the next significant animation.
   - Expressions take 300–600ms to transition smoothly. Don't interrupt mid-transition.
   - Exception: Can layer `eyebrow` commands during expression transitions (they're orthogonal).

3. **Eye movements can chain faster: 50–100ms minimum**
   - `gaze`, `eyebrow_raise`, `eyebrow_lower` can follow each other with only 50–100ms gaps.
   - These are "quick" movements that don't conflict.
   - Example: gaze left (200ms) → gap 100ms → gaze up (200ms) → gap 100ms → gaze right (200ms).

4. **Blinks/winks are "safe interrupters": 100ms minimum after**
   - Blinks don't disrupt other animations. Safe to chain after any command.
   - Always wait ≥100ms after a blink/wink before starting a new major animation.

5. **Head turns need exclusive time: 300–600ms gap before other major movements**
   - Head movements are 3D-like projections. Don't overlap with gaze or eye rolls.
   - After a head turn finishes, wait 300ms before starting a `roll` or new `gaze`.

6. **Nose animations are quick and orthogonal: 100ms minimum after**
   - Nose can animate during other actions (blink, gaze).
   - Sequences of nose actions: 100–200ms gaps (e.g., `twitch` → 150ms → `wiggle`).

---

## 3. Natural Sequences – Combinations That Look Good

These choreography patterns feel emotionally cohesive:

### Surprise Sequence
```
set_expression neutral (t=0, duration 300ms)
├─ at t=300ms: eyebrow_raise (200ms)
├─ at t=400ms: set_expression surprised (400ms, overlaps with eyebrow — OK, they're orthogonal)
└─ at t=800ms: gaze 30 -30 (look upward-right, 400ms)
```
**Why:** Raising brows before switching to surprised expression emphasizes the shock. Upward gaze completes the "realization" look.

### Wink & Gaze
```
wink_right (t=0, 400ms)
├─ at t=450ms: gaze 30 0 (look right, 300ms)
└─ at t=800ms: set_expression happy (300ms)
```
**Why:** Wink then look at target. Smile (happy expression) acknowledges the person you winked at.

### Sleepy/Tired Sequence
```
eyebrow_lower (t=0, 250ms)
├─ at t=300ms: gaze 0 20 (look downward slightly, 300ms)
├─ at t=650ms: blink (250ms, slow blink effect)
└─ at t=950ms: set_expression sleeping (600ms transition)
```
**Why:** Lowered brows signal fatigue. Downward gaze + slow blink → falling asleep.

### Confused/Skeptical
```
eyebrow_raise_left (t=0, 200ms)
├─ at t=250ms: eyebrow_lower_right (200ms, creates asymmetric "one-brow raised" look)
├─ at t=500ms: gaze -20 0 (glance left, 300ms)
└─ at t=850ms: set_expression neutral (300ms)
```
**Why:** Asymmetric brows are classic skepticism. Glance to side adds doubt.

### Scared/Anxious Loop
```
set_expression scared (t=0, 500ms)
├─ at t=550ms: eyebrow_raise (200ms)
├─ at t=800ms: roll_clockwise (800ms, eyes darting around)
├─ at t=1650ms: gaze 0 -30 (look up, searching, 300ms)
└─ at t=2000ms: blink (250ms, nervous blink)
```
**Why:** Scared expression + raised brows + darting eyes + upward gaze = fear/panic.

### Looking Around (Exploration)
```
gaze 45 0 (t=0, look right, 400ms)
├─ at t=500ms: gaze 0 -45 (look up, 400ms)
├─ at t=950ms: gaze -45 0 (look left, 400ms)
├─ at t=1400ms: gaze 0 45 (look down, 400ms)
└─ at t=1900ms: gaze 0 0 (return center, 300ms)
```
**Why:** Smooth gaze sweeps create "taking in surroundings" impression. Chain gaze commands with 500–600ms gaps.

### Nose-Scrunch (Disgust)
```
set_expression angry (t=0, 400ms)
├─ at t=450ms: scrunch_nose (400ms)
├─ at t=900ms: eyebrow_lower (200ms)
└─ at t=1150ms: blink (250ms, "dismissive" blink)
```
**Why:** Angry expression + scrunched nose + lowered brows = disgust.

---

## 4. Things to Avoid – Anti-Patterns

These combinations look broken or wrong:

### ❌ Eye Rolls During Happy/Sad/Angry
**Bad:** `set_expression happy` followed by `roll_clockwise`  
**Why:** Rolling eyes conflicts with expression emotion. Happy + rolling = dismissive, not joyful. Angry + rolling = confused.  
**Fix:** Use `roll_clockwise` only during neutral, sleeping, or scared expressions (or standalone without expression context).

### ❌ Back-to-Back Expression Changes < 200ms Apart
**Bad:** `set_expression happy` (t=0) → `set_expression sad` (t=100)  
**Why:** Creates jarring visual flicker. Expressions don't have time to render before switching.  
**Fix:** Minimum 300ms between `set_expression` commands.

### ❌ Head Turns While Sleeping
**Bad:** `set_expression sleeping` → `turn_head_left`  
**Why:** Breaks immersion. Sleeping = eyes closed, but turning head looks like waking up mid-action.  
**Fix:** Only turn head during awake expressions (neutral, happy, sad, etc.). Exception: subtle shifts (25–50px) for "dreaming" effect.

### ❌ Gaze Angles > 70 Degrees Are Extreme
**Bad:** `gaze 80 85` (nearly looking behind)  
**Why:** Humans can't comfortably look that far sideways. Pupils maxing out looks unnatural and strains the eye.  
**Recommended range:** ±45° for normal glances, ±60° for exaggerated looks, ±70° only for dramatic "looking back."  
**Fix:** Keep gaze within ±45° for everyday feel, use ±60° for emphasis.

### ❌ Overlapping Blinks/Winks
**Bad:** `blink` (t=0) → `wink_left` (t=100)  
**Why:** Both affect eyes. Back-to-back causes rapid fluttering that looks like twitching, not natural blinking.  
**Fix:** Wait 400–600ms between `blink` and `wink_*` commands.

### ❌ Multiple Head Turns Without Settling
**Bad:** `turn_left 100` (t=0) → `turn_right 100` (t=100)  
**Why:** Head whips back and forth too fast. Looks jittery, not deliberate.  
**Fix:** After a head turn, wait 300–500ms before the next `turn_*` or `center_head`.

### ❌ Extreme Eyebrow Offsets (> ±50px)
**Bad:** `eyebrow_lower` several times in succession → eyebrows disappear  
**Why:** Eyebrows have a clamping range. Pushing them too far causes collision detection and clipping.  
**Fix:** Reset with `eyebrow_reset` after significant offsets.

### ❌ Gaze at Extreme Angles During Sad/Scared Expressions
**Bad:** `set_expression sad` → `gaze 70 70` (looking far sideways-down)  
**Why:** Sad/scared are inward emotions. Extreme gaze angles break the emotional logic.  
**Fix:** Keep gaze gentle (±20° to ±30°) during introspective expressions.

---

## 5. Total Duration Guidance – How Long Should a Full Animation Be?

The `duration_ms` field in timeline JSON should reflect the natural length of the animation.

### Categories
- **Short animations: 2–5 seconds (2000–5000ms)**
  - Simple sequences: blink + gaze + expression.
  - Example: Surprised reaction, simple acknowledgment.
  
- **Medium animations: 5–15 seconds (5000–15000ms)**
  - Multi-step sequences: expression change, several gazes, blink, head turn.
  - Example: Exploring a scene, complex emotion sequence.
  
- **Long animations: 15–30 seconds (15000–30000ms)**
  - Elaborate choreography: full loops (looking around), repeated nose actions, multiple head turns.
  - Example: "Pumpkin thinks hard," "pumpkin scans room," or performance piece.

### Rule of Thumb
**The generator should aim for `duration_ms` to equal or slightly exceed the time of the last command.** Don't leave large silent gaps at the end. If the last command starts at 12 seconds, set `duration_ms` to 12500–13000 (adds ~500ms for the last command to finish).

**Example:**
- Last command: `gaze 0 0` starts at t=12000ms, duration 300ms
- Set `duration_ms = 12500` (guarantees full animation completes within timeline)

---

## 6. Worked Examples – Three Complete Timeline Examples with Annotations

### Example 1: Simple Greeting (3 seconds)

```json
{
  "version": "1.0",
  "duration_ms": 3500,
  "commands": [
    {
      "time_ms": 0,
      "command": "set_expression",
      "args": { "expression": "neutral" }
    },
    {
      "time_ms": 500,
      "command": "blink",
      "args": {}
    },
    {
      "time_ms": 1000,
      "command": "wink_right",
      "args": {}
    },
    {
      "time_ms": 1500,
      "command": "set_expression",
      "args": { "expression": "happy" }
    },
    {
      "time_ms": 2100,
      "command": "gaze",
      "args": { "x": 30, "y": 0 }
    },
    {
      "time_ms": 2600,
      "command": "eyebrow_raise",
      "args": {}
    }
  ]
}
```

**Timing Annotations:**
- `t=0–500`: Set to neutral (500ms for expression render).
- `t=500`: Quick blink (200ms blink, 300ms wait before next action).
- `t=1000`: Wink right (400ms duration).
- `t=1500`: Transition to happy (400ms smooth transition).
- `t=2100`: Gaze right at +30° (300ms smooth gaze), 400ms gap from expression.
- `t=2600`: Raise brows for emphasis (200ms action).
- Total: 3500ms = last command finishes by 2800ms + safety margin.

**Feeling:** Friendly acknowledgment, genuine happiness.

---

### Example 2: Scared Reaction (5 seconds)

```json
{
  "version": "1.0",
  "duration_ms": 5500,
  "commands": [
    {
      "time_ms": 0,
      "command": "set_expression",
      "args": { "expression": "surprised" }
    },
    {
      "time_ms": 600,
      "command": "eyebrow_raise",
      "args": {}
    },
    {
      "time_ms": 900,
      "command": "set_expression",
      "args": { "expression": "scared" }
    },
    {
      "time_ms": 1500,
      "command": "roll_clockwise",
      "args": {}
    },
    {
      "time_ms": 2600,
      "command": "gaze",
      "args": { "x": 0, "y": -40 }
    },
    {
      "time_ms": 3100,
      "command": "blink",
      "args": {}
    },
    {
      "time_ms": 3500,
      "command": "eyebrow_reset",
      "args": {}
    },
    {
      "time_ms": 4000,
      "command": "gaze",
      "args": { "x": 0, "y": 0 }
    }
  ]
}
```

**Timing Annotations:**
- `t=0–600`: Surprised expression (600ms), then raise brows (300ms gap).
- `t=900`: Transition to scared (600ms smooth transition).
- `t=1500`: Eyes darting (roll clockwise, 1000ms full rotation) — gap of 600ms from scared expression to allow it to settle.
- `t=2600`: Look upward (-40°, 300ms gaze), 500ms gap from roll completion (allows eyes to settle).
- `t=3100`: Nervous blink (250ms).
- `t=3500`: Reset brows (200ms).
- `t=4000`: Return gaze to center (300ms).
- Total: 5500ms = ensures all animations complete.

**Feeling:** Moment of fear, panic, then recovering composure.

---

### Example 3: Thoughtful Exploration (8 seconds)

```json
{
  "version": "1.0",
  "duration_ms": 8500,
  "commands": [
    {
      "time_ms": 0,
      "command": "set_expression",
      "args": { "expression": "neutral" }
    },
    {
      "time_ms": 500,
      "command": "gaze",
      "args": { "x": 45, "y": 0 }
    },
    {
      "time_ms": 1000,
      "command": "gaze",
      "args": { "x": 0, "y": -45 }
    },
    {
      "time_ms": 1500,
      "command": "gaze",
      "args": { "x": -45, "y": 0 }
    },
    {
      "time_ms": 2000,
      "command": "gaze",
      "args": { "x": 0, "y": 45 }
    },
    {
      "time_ms": 2500,
      "command": "gaze",
      "args": { "x": 0, "y": 0 }
    },
    {
      "time_ms": 3000,
      "command": "eyebrow_lower",
      "args": {}
    },
    {
      "time_ms": 3300,
      "command": "blink",
      "args": {}
    },
    {
      "time_ms": 3700,
      "command": "turn_head_left",
      "args": { "amount": 75 }
    },
    {
      "time_ms": 4300,
      "command": "gaze",
      "args": { "x": 20, "y": 10 }
    },
    {
      "time_ms": 4800,
      "command": "center_head",
      "args": {}
    },
    {
      "time_ms": 5500,
      "command": "set_expression",
      "args": { "expression": "happy" }
    },
    {
      "time_ms": 6100,
      "command": "gaze",
      "args": { "x": 30, "y": -20 }
    }
  ]
}
```

**Timing Annotations:**
- `t=0–500`: Neutral expression established (500ms).
- `t=500–2500`: Gaze sequence (right → up → left → down → center), 500ms gaps = smooth "looking around" loop. Chained gaze commands with minimal gaps for fluid head movement simulation.
- `t=3000`: Lower brows (thoughtful, 250ms), 500ms gap after last gaze.
- `t=3300`: Blink (250ms, introspective moment).
- `t=3700`: Turn head left 75px (600ms animation, 300ms gap after blink).
- `t=4300`: Gaze right-up (+20, -10) while head is turned (300ms gaze).
- `t=4800`: Return head to center (500ms smooth transition, 300ms gap from gaze).
- `t=5500`: Happy expression (600ms transition from looking around + thinking).
- `t=6100`: Final gaze up-right as a "look of hope" (300ms).
- Total: 8500ms = all animations complete with safety margin.

**Feeling:** Pumpkin observes surroundings, thinks deeply, then comes to a happy realization.

---

## 7. Tips for LLM Timeline Generation

When an LLM generates animations using this guide:

1. **Always respect minimum gaps** — Never place commands < 100ms apart (except for intentional chaining).
2. **Name expressions explicitly** — Use exact enum names: `neutral`, `happy`, `sad`, `angry`, `surprised`, `scared`, `sleeping`.
3. **Bound gaze angles** — Keep gaze within ±60° for believability, ±45° for naturalism.
4. **Check emotional logic** — Does the animation tell a coherent story? (Scared + dancing = wrong. Scared + darting eyes = right.)
5. **Set duration_ms correctly** — Calculate as `max(all command time_ms) + estimated_final_command_duration + 100ms buffer`.
6. **Use "at rest" endpoints** — End animations with a settled expression/gaze, not mid-action.
7. **Interleave quick actions** — Blinks, eyebrow tweaks, and nose actions can co-exist with longer animations (expression transitions, gaze).
8. **Reset between major shifts** — After complex choreography, return to neutral expression and centered gaze before the next sequence.

---

## 8. Command Vocabulary Quick Reference for LLM

Use this table when generating `"command"` field values:

**Expression Commands:**
- `set_expression [neutral|happy|sad|angry|surprised|scared|sleeping]`

**Eye Commands:**
- `blink`, `wink_left`, `wink_right`
- `roll_clockwise`, `roll_counterclockwise`
- `gaze x:float y:float` or `gaze lx:float ly:float rx:float ry:float`

**Eyebrow Commands:**
- `eyebrow_raise`, `eyebrow_lower`
- `eyebrow_raise_left`, `eyebrow_lower_left`
- `eyebrow_raise_right`, `eyebrow_lower_right`
- `eyebrow_reset`
- `eyebrow value:float` or `eyebrow left:float right:float`

**Head Commands:**
- `turn_left [amount]`, `turn_right [amount]`
- `turn_up [amount]`, `turn_down [amount]`
- `center_head`

**Nose Commands:**
- `twitch_nose`, `wiggle_nose`, `scrunch_nose`, `reset_nose`

**Projection Commands (rarely used in performative animations):**
- `set_offset x:int y:int`, `jog_offset dx:int dy:int`
- `projection_reset`

---

## End of Guidelines

These timings are empirically derived from the graphics rendering system. Follow them for smooth, believable animations. When in doubt, err on the side of **longer gaps** (animations feel natural; gaps are invisible). Too-short gaps are the primary cause of visual artifacts.
