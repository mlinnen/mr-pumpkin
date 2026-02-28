---
name: "relative-coordinate-clamping"
description: "Pattern for clamping child element coordinates relative to parents, not absolute screen positions"
domain: "graphics-rendering"
confidence: "low"
source: "earned"
---

## Context

When rendering hierarchical graphics where parent elements can be transformed (offset, scaled, rotated), child element position clamps must be relative to their parent's coordinate system, not absolute screen coordinates. Hardcoded absolute clamps break when the coordinate system shifts.

**Key Challenge:** Child elements (e.g., eyebrows) need bounds limits, but parent elements (e.g., face center) can be transformed (e.g., projection offset). Clamping child positions to absolute screen coordinates causes clipping when parent transforms are applied.

## Pattern

### Calculate Positions Relative to Parent

Child positions should be computed relative to parent element positions, which already include any transforms:

```python
# Parent position includes transform
eye_pos = calculate_eye_position(center_x + offset_x, center_y + offset_y)

# Child position computed relative to parent
eyebrow_y = eye_pos[1] + baseline_gap + user_offset - animation_lift
```

### Clamp Against True Boundaries, Not Arbitrary Values

When clamping, use actual rendering boundaries (screen edges, parent element bounds) rather than hardcoded coordinate values:

```python
# ✅ GOOD: Clamp against actual screen boundary
eyebrow_y = max(0, eyebrow_y)  # Don't render above screen top

# ❌ BAD: Hardcoded coordinate assumes no transform applied
eyebrow_y = max(350, eyebrow_y)  # Breaks when face offset moves eyes to y=200
```

### Use Relative Collision Detection

Collision/proximity detection between related elements should use relative distances:

```python
# ✅ GOOD: Relative distance check
eye_top = eye_pos[1] - eye_radius
eyebrow_bottom = eyebrow_y + thickness // 2
gap = eye_top - eyebrow_bottom
if gap < MIN_GAP:
    skip_rendering()

# ❌ BAD: Absolute coordinate check
if eyebrow_y > 400:  # Arbitrary threshold breaks with offset
    skip_rendering()
```

## Bug Example: Eyebrow Clipping

**Scenario:** Pumpkin face projection can be jogged ±500 pixels for physical alignment. When jogged upward (negative Y offset), eyebrows disappeared while eyes remained visible.

**Root Cause:**

```python
# Eyebrows positioned relative to eyes (which include offset)
eyebrow_y = eye_pos[1] + baseline_gap + user_offset

# But then clamped to ABSOLUTE coordinate
eyebrow_y = max(350, eyebrow_y)  # ❌ Hardcoded screen coordinate
```

When projection offset moved eyes from y=550 to y=250, eyebrow calculation gave y=195, but clamp forced it to y=350 (below the eyes), causing clipping.

**Fix:**

```python
# Clamp to actual screen boundary, not arbitrary value
screen_top = 0  # True rendering boundary
eyebrow_y = max(screen_top, eyebrow_y)  # ✅ Relative to screen edge
```

Now eyebrows move with eyes at any offset, clamped only against the actual screen top edge.

## When to Apply

This pattern applies whenever:
- Child elements are positioned relative to parent elements
- Parent elements can be transformed (offset, scaled, rotated)
- Child positions need bounds checking or collision detection
- Multiple coordinate systems exist in the same rendering pipeline

## Examples

### UI Elements in Scrollable Container

```python
class ScrollableList:
    def __init__(self):
        self.scroll_offset_y = 0
        self.item_height = 50
    
    def render_item(self, item_index, surface):
        # Item position includes scroll offset
        item_y = item_index * self.item_height + self.scroll_offset_y
        
        # ✅ Clamp against container bounds, not screen coords
        container_top = self.container_y
        container_bottom = self.container_y + self.container_height
        
        if container_top <= item_y <= container_bottom:
            draw_item(surface, item_y)
```

### Articulated Character Limbs

```python
class Character:
    def render_hand(self, surface):
        # Hand positioned relative to elbow (which includes shoulder offset)
        elbow_x, elbow_y = self.get_elbow_position()  # Includes shoulder transform
        hand_x = elbow_x + arm_length * cos(elbow_angle)
        hand_y = elbow_y + arm_length * sin(elbow_angle)
        
        # ✅ Collision with ground is relative distance check
        ground_y = self.get_ground_level()  # Ground can move (platform, slope)
        if hand_y > ground_y:
            hand_y = ground_y  # Clamp to ground surface
        
        # ❌ NOT this: if hand_y > 500
```

### Camera Culling in 2D Game

```python
class Camera:
    def is_visible(self, entity_world_x, entity_world_y):
        # Convert world coordinates to screen coordinates
        screen_x = entity_world_x - self.camera_offset_x
        screen_y = entity_world_y - self.camera_offset_y
        
        # ✅ Culling against screen viewport bounds (relative to camera)
        return (0 <= screen_x <= self.screen_width and 
                0 <= screen_y <= self.screen_height)
        
        # ❌ NOT this: return entity_world_y < 1000  # Ignores camera position
```

## Anti-Patterns

### ❌ Hardcoded Absolute Clamps

```python
# BAD: Assumes elements are always at specific screen coordinates
if eyebrow_y < 300 or eyebrow_y > 700:
    skip_rendering()
```

### ❌ Mixing Coordinate Systems

```python
# BAD: Parent in world coords, child clamped in screen coords
parent_pos = transform_to_world(parent)
child_pos = parent_pos + offset
if child_pos.x > SCREEN_WIDTH:  # Wrong coordinate system!
    child_pos.x = SCREEN_WIDTH
```

### ❌ Early Clamping Before Transform

```python
# BAD: Clamping before parent transform is applied
child_x = child_offset_x
child_x = max(0, min(screen_width, child_x))  # Clamp too early
final_x = parent_x + child_x  # Parent transform applied AFTER clamp
```

## Benefits

1. **Transform Tolerance:** Child elements work correctly regardless of parent transforms
2. **Coordinate System Independence:** Clamping logic doesn't assume specific coordinate values
3. **Maintainability:** No magic numbers tied to specific screen layouts
4. **Composability:** Multiple transform layers can be stacked without breaking clamps
5. **Scalability:** System works at any resolution or coordinate scale

## Related Skills

- `ui-transform-layering` — Applying transforms at rendering root for uniform effects
- `orthogonal-animation-state` — Separating coordinate transforms from animation state
- Coordinate space transformations (world → view → screen)

## Testing Strategy

Test clamping logic with:
1. Parent at default/centered position (baseline)
2. Parent at extreme offsets in all directions
3. Child at extreme positions relative to parent
4. Different screen resolutions/viewport sizes
5. Combined transforms (offset + scale + rotation)

Ensure child elements remain visible and correctly positioned across all scenarios.
