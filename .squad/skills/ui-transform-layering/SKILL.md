---
name: "ui-transform-layering"
description: "Pattern for applying global UI transforms at rendering root for uniform effect"
domain: "graphics-architecture"
confidence: "low"
source: "earned"
---

## Context

When building graphics systems that need user-adjustable transformations (offset, scale, rotation) that apply uniformly to all rendered elements, applying the transform at the rendering root is cleaner than modifying every drawing call.

**Key Challenge:** User wants to "nudge" the entire rendered scene (e.g., projection alignment) without affecting animation logic or requiring changes to feature-specific rendering code.

## Pattern

### Apply Transform at Coordinate Origin

Transform the base coordinate system BEFORE calculating any feature positions:

```python
def draw(self, surface):
    surface.fill(BACKGROUND_COLOR)
    
    # Apply user transform to root coordinates
    center_x = (self.width // 2) + self.projection_offset_x
    center_y = (self.height // 2) + self.projection_offset_y
    
    # All features calculated from transformed center
    left_eye_pos, right_eye_pos = self._get_eye_positions(center_x, center_y)
    mouth_points = self._get_mouth_points(center_x, center_y)
    
    # Drawing methods automatically inherit the offset
    self._draw_eyes(surface, left_eye_pos, right_eye_pos)
    self._draw_mouth(surface, mouth_points)
```

### Orthogonal State Layer

Keep transform state separate from animation/expression state:

```python
def __init__(self):
    # Expression state machine
    self.current_expression = Expression.NEUTRAL
    
    # Animation state
    self.is_blinking = False
    
    # UI transform state (orthogonal to above)
    self.projection_offset_x = 0
    self.projection_offset_y = 0
```

### Incremental Adjustment Methods

Provide relative (jog/nudge) and absolute (set) methods:

```python
def jog_projection(self, dx: int, dy: int):
    """Relative adjustment - nudge by delta."""
    self.projection_offset_x += dx
    self.projection_offset_y += dy

def set_projection_offset(self, x: int, y: int):
    """Absolute positioning."""
    self.projection_offset_x = x
    self.projection_offset_y = y

def reset_projection_offset(self):
    """Return to neutral/centered position."""
    self.projection_offset_x = 0
    self.projection_offset_y = 0
```

### Bounds Clamping

Prevent extreme offsets that break rendering:

```python
def jog_projection(self, dx: int, dy: int):
    def clamp(v): return max(-500, min(500, int(v)))
    self.projection_offset_x = clamp(self.projection_offset_x + dx)
    self.projection_offset_y = clamp(self.projection_offset_y + dy)
```

## Benefits

1. **Uniform Application:** All rendered features automatically inherit the transform
2. **No Code Duplication:** Don't need to modify every draw call
3. **Animation Independence:** Transforms don't interfere with animations
4. **Composability:** Multiple transforms can be layered (offset, then scale, then rotate)
5. **State Persistence:** Offset survives expression changes, animations, etc.

## Examples

### Projection Alignment Jog (pumpkin_face.py)

Problem: Physical projector needs micro-adjustments to align projected face onto foam pumpkin.

```python
# State (orthogonal to expression/animation)
self.projection_offset_x = 0
self.projection_offset_y = 0
self.jog_step = 5  # pixels per keypress

# Keyboard controls
elif key == pygame.K_UP:
    self.jog_projection(0, -self.jog_step)
elif key == pygame.K_DOWN:
    self.jog_projection(0, self.jog_step)
elif key == pygame.K_LEFT:
    self.jog_projection(-self.jog_step, 0)
elif key == pygame.K_RIGHT:
    self.jog_projection(self.jog_step, 0)
elif key == pygame.K_0:
    self.reset_projection_offset()

# Rendering applies offset at root
center_x = (self.width // 2) + self.projection_offset_x
center_y = (self.height // 2) + self.projection_offset_y
```

Result: Arrow keys nudge entire face (eyes, mouth, eyebrows) as a unit. No feature-specific code changes needed.

### Camera Panning in Game Engine

```python
class Camera:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
    
    def pan(self, dx, dy):
        self.offset_x += dx
        self.offset_y += dy
    
    def world_to_screen(self, world_x, world_y):
        screen_x = world_x - self.offset_x
        screen_y = world_y - self.offset_y
        return (screen_x, screen_y)

# All game entities rendered through camera transform
def render_entities(entities, camera, surface):
    for entity in entities:
        screen_pos = camera.world_to_screen(entity.x, entity.y)
        entity.draw(surface, screen_pos)
```

## Anti-Patterns

### ❌ Modifying Every Draw Call

```python
# BAD: Adding offset to every feature individually
def _draw_eyes(self, surface, left_pos, right_pos):
    left_x = left_pos[0] + self.projection_offset_x  # Repeated
    left_y = left_pos[1] + self.projection_offset_y
    # ... same for right eye, mouth, nose, etc.
```

### ❌ Coupling Transform to Animation State

```python
# BAD: Offset logic mixed with expression logic
if self.current_expression == Expression.HAPPY:
    center_x = (width // 2) + self.projection_offset_x
    # Complex branching for each expression...
```

### ❌ No Bounds Checking

```python
# BAD: Unbounded offset can render features off-screen
self.projection_offset_x += dx  # Could go to +10000
```

## When to Apply

- Projection mapping alignment (physical world positioning)
- Camera panning/scrolling in 2D games
- UI viewport adjustments (pan, zoom)
- Multi-monitor offset corrections
- User-adjustable screen positioning
- Touch gesture transformations (pinch, pan)

## Related Skills

- `orthogonal-animation-state` — Pattern for separating animation state from main state machine
- Coordinate space transformations (world → view → screen)
- Matrix transformations for 2D graphics
