---
name: "orthogonal-animation-state"
description: "Pattern for temporary animation overlays that preserve and restore origin state"
domain: "animation-state-machines"
confidence: "medium"
source: "earned"
---

## Context

When building animation systems that need to temporarily override visual state (blink, wink, roll eyes, nod, etc.) without disrupting core state machines (expression transitions, object position, etc.).

**Key Challenge:** Temporary animations must return to EXACT starting state, not a default/hardcoded state. Example: rolling eyes from 90° must return to 90°, not default 225°.

## Patterns

### 1. Orthogonal State Variables
Separate animation state from main state machine:
```python
# Main state machine
self.current_expression = Expression.NEUTRAL
self.transition_progress = 1.0

# Orthogonal animation state (blink example)
self.is_blinking = False
self.blink_progress = 0.0
self.pre_blink_expression = None

# Orthogonal animation state (rolling eyes example)
self.is_rolling = False
self.rolling_progress = 0.0
self.rolling_start_angle = None  # Captured starting position
```

### 2. Capture-on-Start Pattern
When animation begins, capture CURRENT state (don't assume defaults):
```python
def roll_clockwise(self):
    if not self.is_rolling:  # Non-interrupting guard
        self.is_rolling = True
        self.rolling_progress = 0.0
        self.rolling_start_angle = self.pupil_angle  # Capture current position
```

### 3. Restore-on-Complete Pattern
On completion, restore captured state, not hardcoded defaults:
```python
# Update loop
if self.rolling_progress >= 1.0:
    self.pupil_angle = self.rolling_start_angle  # Exact restoration
    self.rolling_start_angle = None  # Clear capture
    self.is_rolling = False
```

### 4. Progress-Based Animation
Use linear 0.0 → 1.0 progress tracking with speed/duration control:
```python
self.rolling_progress += delta_time / self.rolling_duration
# Then calculate visual state from progress:
angle = (start_angle + progress * 360 * direction) % 360
```

### 5. Non-Interrupting Guards
Prevent new animation from disrupting in-progress animation:
```python
if not self.is_rolling:  # Don't interrupt ongoing roll
    self.is_rolling = True
    # ... start new animation
```

### 6. Composition with Other Animations
Allow pause/resume when higher-priority animations occur:
```python
if self.is_rolling and not (self.is_blinking or self.is_winking):
    # Advance rolling animation
elif self.is_blinking or self.is_winking:
    # Rolling paused (progress frozen), resumes after blink/wink
```

## Examples

**Blink Animation** (pumpkin_face.py):
- State: `is_blinking`, `blink_progress`, `pre_blink_expression`
- Capture: Saves `current_expression` before closing eyes
- Restore: Returns to `pre_blink_expression` after opening

**Rolling Eyes Animation** (pumpkin_face.py):
- State: `is_rolling`, `rolling_progress`, `rolling_start_angle`
- Capture: Saves `pupil_angle` at start
- Restore: Returns to exact `rolling_start_angle` after 360°

**Wink Animation** (pumpkin_face.py):
- State: `is_winking`, `wink_progress`, `winking_eye`, `pre_wink_expression`
- Capture: Saves expression and which eye
- Restore: Both eyes return to full scale, expression restored

**Eyebrow Lift During Blink/Wink** (pumpkin_face.py):
- Pattern: Derived transient animation (no capture/restore needed)
- Blink lift: `8.0 * sin(blink_progress * π)` computed at render time
- Wink lift: `8.0 * (1.0 - eye_scale)` per eye, computed from wink state
- Key insight: These are rendering effects derived from existing animation progress vars, not separate animations with their own capture/restore cycle

## Anti-Patterns

### ❌ Hardcoded Return State
```python
# BAD: Always returns to default position
if self.rolling_progress >= 1.0:
    self.pupil_angle = 225.0  # Hardcoded default
```

### ❌ Modifying Main State Machine
```python
# BAD: Polluting Expression enum with animation states
class Expression(Enum):
    BLINKING = "blinking"  # This is animation, not expression
```

### ❌ Allowing Interruption
```python
# BAD: Starting new animation without checking
def blink(self):
    self.is_blinking = True  # Could interrupt ongoing blink
```

### ❌ State Coupling
```python
# BAD: Animation logic embedded in main state machine
if self.current_expression == Expression.NEUTRAL:
    if self.is_blinking:
        # Complex interleaved logic...
```

Keep animations orthogonal — independent state, independent update logic, composable via priority rules.
