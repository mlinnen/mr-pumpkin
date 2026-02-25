---
name: "smooth-state-animation"
description: "Pattern for smoothly animating state variable transitions with easing functions"
domain: "graphics, animation"
confidence: "high"
source: "earned"
---

## Context

When implementing animations that transition a state variable from one value to another, smooth interpolation with easing creates more natural, polished motion than instant jumps or linear transitions. This pattern applies to:

- Spatial position changes (coordinates, offsets)
- Angular rotations (degrees, radians)
- Scale/size transitions (zoom, scaling factors)
- Opacity/transparency fades
- Any numeric state that changes over time

This is distinct from cyclic animations (like blinking) or state machine transitions (like expression changes). It's for smoothly moving from point A to point B.

## Patterns

### 1. Animation State Variables

Define state for tracking animation progress:

```python
# Animation state
self.is_animating = False           # Animation active flag
self.animation_progress = 0.0       # 0.0 to 1.0
self.animation_duration = 0.5       # Duration in seconds
self.start_value = 0                # Starting value
self.target_value = 100             # Target value
```

### 2. Animation Trigger Method

Method to start animation captures current state and sets target:

```python
def start_animation(self, target):
    """Start smooth transition to target value."""
    self.is_animating = True
    self.animation_progress = 0.0
    self.start_value = self.current_value  # Capture current state
    self.target_value = clamp(target)       # Apply boundaries
```

### 3. Update Loop Integration

Update animation progress each frame (typically 60 FPS):

```python
def update(self):
    if self.is_animating:
        delta_time = 1.0 / 60.0  # Frame time
        self.animation_progress += delta_time / self.animation_duration
        
        if self.animation_progress >= 1.0:
            # Animation complete: set exact target
            self.current_value = self.target_value
            self.is_animating = False
            self.animation_progress = 0.0
        else:
            # Interpolate with easing
            t = self.animation_progress
            eased_t = ease_in_out_cubic(t)
            self.current_value = lerp(self.start_value, self.target_value, eased_t)
```

### 4. Easing Functions

Common easing functions for different motion feels:

```python
# Ease-in-out cubic: slow start, fast middle, slow end (natural)
def ease_in_out_cubic(t):
    return t * t * (3.0 - 2.0 * t)

# Linear: constant speed (mechanical)
def linear(t):
    return t

# Ease-out: fast start, slow end (arrives gently)
def ease_out(t):
    return 1.0 - (1.0 - t) * (1.0 - t)

# Ease-in: slow start, fast end (accelerates into target)
def ease_in(t):
    return t * t
```

### 5. Linear Interpolation

```python
def lerp(start, end, t):
    """Linear interpolation between start and end."""
    return start + (end - start) * t
```

For 2D coordinates:
```python
x = lerp(start_x, target_x, eased_t)
y = lerp(start_y, target_y, eased_t)
```

## Examples

### Example 1: Smooth Position Movement (2D)

```python
class AnimatedObject:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.is_moving = False
        self.move_progress = 0.0
        self.move_duration = 0.5
        self.start_x = 0
        self.start_y = 0
        self.target_x = 0
        self.target_y = 0
    
    def move_to(self, x, y):
        """Start smooth movement to target position."""
        self.is_moving = True
        self.move_progress = 0.0
        self.start_x = self.x
        self.start_y = self.y
        self.target_x = x
        self.target_y = y
    
    def update(self):
        if self.is_moving:
            self.move_progress += (1.0 / 60.0) / self.move_duration
            
            if self.move_progress >= 1.0:
                self.x = self.target_x
                self.y = self.target_y
                self.is_moving = False
            else:
                t = self.move_progress
                eased = t * t * (3.0 - 2.0 * t)
                self.x = self.start_x + (self.target_x - self.start_x) * eased
                self.y = self.start_y + (self.target_y - self.start_y) * eased
```

### Example 2: Head Movement Animation (from Issue #17)

```python
def turn_head_left(self, amount: int = 50):
    """Turn head left by animating projection offset."""
    target_x = self.projection_offset_x - amount
    self._start_head_movement(target_x, self.projection_offset_y)

def _start_head_movement(self, target_x: int, target_y: int):
    """Start smooth head movement animation."""
    self.is_moving_head = True
    self.head_movement_progress = 0.0
    self.head_start_x = self.projection_offset_x    # Capture current
    self.head_start_y = self.projection_offset_y
    self.head_target_x = clamp(target_x, -500, 500) # Apply limits
    self.head_target_y = clamp(target_y, -500, 500)

# In update() loop:
if self.is_moving_head:
    self.head_movement_progress += (1.0 / 60.0) / 0.5  # 0.5s duration
    
    if self.head_movement_progress >= 1.0:
        self.projection_offset_x = self.head_target_x
        self.projection_offset_y = self.head_target_y
        self.is_moving_head = False
    else:
        t = self.head_movement_progress
        eased = t * t * (3.0 - 2.0 * t)  # Ease-in-out cubic
        self.projection_offset_x = int(self.head_start_x + 
                                      (self.head_target_x - self.head_start_x) * eased)
        self.projection_offset_y = int(self.head_start_y + 
                                      (self.head_target_y - self.head_start_y) * eased)
```

## Anti-Patterns

### ❌ Don't hardcode starting position
```python
# BAD: Assumes always starting from 0
self.start_value = 0
self.target_value = 100
```

```python
# GOOD: Capture current state
self.start_value = self.current_value
self.target_value = 100
```

### ❌ Don't use linear interpolation for motion
```python
# BAD: Feels robotic and mechanical
t = self.progress
self.value = start + (target - start) * t
```

```python
# GOOD: Use easing for natural feel
t = self.progress
eased_t = t * t * (3.0 - 2.0 * t)  # Ease-in-out
self.value = start + (target - start) * eased_t
```

### ❌ Don't accumulate rounding errors
```python
# BAD: Interpolated value may not reach exact target
if self.progress >= 1.0:
    self.is_animating = False  # But value may be off by 0.001
```

```python
# GOOD: Set exact target on completion
if self.progress >= 1.0:
    self.value = self.target_value  # Exact value, no drift
    self.is_animating = False
```

### ❌ Don't interrupt ongoing animations without cleanup
```python
# BAD: Starting new animation mid-animation loses state
def move_to(self, target):
    self.target = target
    self.progress = 0.0  # Old animation state lost
```

```python
# GOOD: Either prevent interrupts or capture current position
def move_to(self, target):
    if self.is_animating:
        # Option 1: Reject new animation
        return
        
        # Option 2: Capture current interpolated position as new start
        self.start_value = self.current_value
    
    self.target_value = target
    self.progress = 0.0
    self.is_animating = True
```

### ❌ Don't mix update rates
```python
# BAD: Assumes fixed frame rate, breaks at different FPS
self.progress += 0.01  # Only correct at 60 FPS
```

```python
# GOOD: Use delta time relative to duration
delta_time = 1.0 / 60.0  # Or actual frame time
self.progress += delta_time / self.duration
```
