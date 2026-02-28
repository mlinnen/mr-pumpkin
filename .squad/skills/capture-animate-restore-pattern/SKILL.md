---
name: "capture-animate-restore-pattern"
description: "Pattern for temporary animations that must return to exact starting state"
domain: "animation, state-management"
confidence: "medium"
source: "earned"
---

## Context

When implementing animations that temporarily modify state but must return to the original state afterward (e.g., blink returns to original expression, rolling eyes return to starting angle, bounce returns to resting position).

This pattern applies when:
- Animation is a temporary "overlay" on persistent state
- The starting state is not predictable (user-controlled or affected by other animations)
- Exact restoration is required for visual continuity

## Patterns

### State Variables

Add three related state variables:
```python
self.is_{animation} = False           # Animation active flag
self.{animation}_progress = 0.0       # Progress through animation (0.0 to 1.0)
self.{animation}_start_state = None   # Captured starting state
```

### Trigger Method

Capture starting state when animation begins:
```python
def trigger_animation(self):
    if not self.is_{animation}:  # Guard against interrupts
        self.is_{animation} = True
        self.{animation}_progress = 0.0
        self.{animation}_start_state = self.current_state  # CAPTURE
```

### Update Logic

Animate relative to captured start state:
```python
if self.is_{animation}:
    self.{animation}_progress += self.{animation}_speed
    if self.{animation}_progress >= 1.0:
        # RESTORE to exact captured state
        self.current_state = self.{animation}_start_state
        self.is_{animation} = False
        self.{animation}_start_state = None  # Clean up
    else:
        # Animate relative to START state, not hardcoded default
        self.current_state = calculate_from(self.{animation}_start_state, 
                                            self.{animation}_progress)
```

## Examples

### Blink Animation (Expression Restoration)
```python
# Capture expression before closing eyes
self.pre_blink_expression = self.current_expression

# After animation completes
self.current_expression = self.pre_blink_expression  # Restore exact expression
```

### Rolling Eyes (Angle Restoration)
```python
# Capture current pupil angle (could be anywhere 0-360°)
self.rolling_start_angle = self.pupil_angle

# During animation: rotate 360° from captured position
self.pupil_angle = (self.rolling_start_angle + progress * 360) % 360

# On completion: return to EXACT captured angle
self.pupil_angle = self.rolling_start_angle
```

## Anti-Patterns

❌ **Hardcoding return state:**
```python
# BAD: Always return to default, ignoring where animation started
self.pupil_angle = 225.0  # Hardcoded default
```

❌ **Not capturing state:**
```python
# BAD: Animate from hardcoded position, causes "jump" at start
self.pupil_angle = (315.0 + progress * 360) % 360
```

❌ **Forgetting to clean up:**
```python
# BAD: Leaves start_state variable populated, causes memory bloat
# and makes debugging confusing
self.{animation}_start_state = ...  # Never set back to None
```

✅ **Correct approach:**
```python
# GOOD: Capture, animate relative to capture, restore exactly
start = self.current_state  # Capture
new_state = animate_from(start, progress)  # Relative animation
self.current_state = start  # Exact restoration
```

## Benefits

1. **Composability:** Animations can chain without state conflicts
2. **No visual discontinuities:** Eliminates "jumps" at animation boundaries
3. **Predictability:** Animation behavior is consistent regardless of starting state
4. **Maintainability:** Clear separation between temporary animation and persistent state
