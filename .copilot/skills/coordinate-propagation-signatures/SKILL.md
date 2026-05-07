---
name: "coordinate-propagation-signatures"
description: "Method signature pattern for propagating transformed coordinates through rendering hierarchy"
domain: "graphics-architecture"
confidence: "low"
source: "earned"
---

## Context

When coordinate transforms are applied at the rendering root (e.g., projection offset, camera position), child rendering methods must accept transformed coordinates as parameters rather than accessing raw screen dimensions directly. Failing to propagate coordinates through method signatures causes coordinate system mismatches where some features respect transforms and others ignore them.

**Key Challenge:** A graphics system applies transforms at the root (`center_x = screen_center + offset`), but child rendering methods need those transformed coordinates to render consistently. If methods access `self.width // 2` directly instead of using passed coordinates, they'll render at absolute screen positions that ignore the transform.

## Pattern

### Consistent Method Signature

All rendering methods that draw relative to the scene's coordinate origin should accept transformed center coordinates as parameters:

```python
class GraphicsSystem:
    def draw(self, surface):
        # Apply transform at root
        center_x = (self.width // 2) + self.projection_offset_x
        center_y = (self.height // 2) + self.projection_offset_y
        
        # Pass transformed coordinates to ALL rendering methods
        left_eye, right_eye = self._get_eye_positions(center_x, center_y)
        mouth_points = self._get_mouth_points(center_x, center_y)
        
        # Signature pattern: _draw_*(surface, ..., cx, cy)
        self._draw_eyes(surface, left_eye, right_eye)
        self._draw_eyebrows(surface, left_eye, right_eye)
        self._draw_mouth(surface, mouth_points, center_x, center_y)
    
    def _draw_mouth(self, surface, points, cx: int, cy: int):
        # ✅ GOOD: Use passed coordinates
        pygame.draw.circle(surface, COLOR, (cx, cy + 80), 30)
        
        # ❌ BAD: Access raw screen dimensions
        # pygame.draw.circle(surface, COLOR, 
        #                   (self.width // 2, self.height // 2 + 80), 30)
```

### Calculate Positions Relative to Parent

Position calculation methods accept transformed coordinates and return positions in the same coordinate space:

```python
def _get_eye_positions(self, cx: int, cy: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Calculate eye positions relative to transformed center."""
    eye_spacing = 100
    eye_y_offset = -50
    
    # Positions calculated relative to cx/cy (which already include offset)
    left = (cx - eye_spacing, cy + eye_y_offset)
    right = (cx + eye_spacing, cy + eye_y_offset)
    return (left, right)
```

### Avoid Raw Dimension Access in Rendering Methods

Rendering methods should not directly access `self.width`, `self.height`, or other raw screen dimensions when positioning elements:

```python
# ✅ GOOD: Accept and use coordinate parameters
def _draw_feature(self, surface, feature_points, cx: int, cy: int):
    for point in feature_points:
        # Use passed cx/cy, not self.width/height
        screen_x = cx + point.offset_x
        screen_y = cy + point.offset_y
        pygame.draw.circle(surface, COLOR, (screen_x, screen_y), 10)

# ❌ BAD: Access raw dimensions directly
def _draw_feature(self, surface, feature_points):
    for point in feature_points:
        # Ignores any transforms applied at root
        screen_x = self.width // 2 + point.offset_x
        screen_y = self.height // 2 + point.offset_y
        pygame.draw.circle(surface, COLOR, (screen_x, screen_y), 10)
```

## Bug Example: Mouth Clipping in Surprised/Scared Mode

**Scenario:** Graphics system with projection offset jog feature. Eyes, eyebrows, and most mouth expressions move correctly with offset, but surprised and scared expressions (circular/oval mouths) ignore offset and render at absolute screen center.

**Root Cause:**

The `draw()` method correctly propagates offset coordinates:

```python
def draw(self, surface):
    center_x = (self.width // 2) + self.projection_offset_x
    center_y = (self.height // 2) + self.projection_offset_y
    
    mouth_points = self._get_mouth_points(center_x, center_y)
    self._draw_mouth(surface, mouth_points)  # Only passes surface and points
```

But `_draw_mouth()` didn't accept `cx, cy` parameters for special-case rendering:

```python
def _draw_mouth(self, surface, points):
    if self.current_expression == Expression.SURPRISED:
        # ❌ Uses raw dimensions - ignores offset!
        pygame.draw.circle(surface, COLOR, 
                          (self.width // 2, self.height // 2 + 80), 30)
```

When projection offset = (0, -300), eyes rendered at y=250 (transformed), but mouth rendered at y=380 (absolute), appearing far below the face.

**Fix:**

```python
def draw(self, surface):
    center_x = (self.width // 2) + self.projection_offset_x
    center_y = (self.height // 2) + self.projection_offset_y
    
    mouth_points = self._get_mouth_points(center_x, center_y)
    self._draw_mouth(surface, mouth_points, center_x, center_y)  # Pass coordinates

def _draw_mouth(self, surface, points, cx: int, cy: int):
    if self.current_expression == Expression.SURPRISED:
        # ✅ Uses transformed coordinates
        pygame.draw.circle(surface, COLOR, (cx, cy + 80), 30)
```

Now mouth renders at y=-220 (transformed), staying aligned with face at any offset.

## When to Apply

This pattern applies whenever:
- Root-level coordinate transforms (offset, camera position, viewport transforms)
- Multiple rendering methods draw elements relative to a common origin
- Some elements position correctly with transforms while others ignore them
- Child elements need to maintain alignment with parent elements under transformation

## Examples

### Canvas Drawing System

```python
class Canvas:
    def render(self, surface):
        # Root transform: canvas pan/zoom
        origin_x = self.pan_x + self.canvas_origin_x * self.zoom
        origin_y = self.pan_y + self.canvas_origin_y * self.zoom
        
        # Propagate through all shape renderers
        for shape in self.shapes:
            self._draw_shape(surface, shape, origin_x, origin_y, self.zoom)
    
    def _draw_shape(self, surface, shape, ox: int, oy: int, zoom: float):
        # Use passed ox/oy, not self.canvas_origin_x/y directly
        screen_x = ox + shape.x * zoom
        screen_y = oy + shape.y * zoom
        pygame.draw.circle(surface, shape.color, (screen_x, screen_y), shape.radius * zoom)
```

### Articulated Character Rendering

```python
class Character:
    def render(self, surface, world_x, world_y):
        # Character root position (world coordinates)
        body_x, body_y = self._get_body_position(world_x, world_y)
        
        # Propagate body position to all limbs
        self._draw_head(surface, body_x, body_y)
        self._draw_left_arm(surface, body_x, body_y)
        self._draw_right_arm(surface, body_x, body_y)
    
    def _draw_head(self, surface, body_x: int, body_y: int):
        # Head position relative to body (body coords already include world transform)
        head_x = body_x
        head_y = body_y - self.neck_length
        pygame.draw.circle(surface, WHITE, (head_x, head_y), self.head_radius)
    
    def _draw_left_arm(self, surface, body_x: int, body_y: int):
        # Shoulder position relative to body
        shoulder_x = body_x - self.shoulder_width
        shoulder_y = body_y + self.shoulder_height
        
        # Elbow position relative to shoulder
        elbow_x = shoulder_x + arm_length * cos(self.left_arm_angle)
        elbow_y = shoulder_y + arm_length * sin(self.left_arm_angle)
        
        pygame.draw.line(surface, WHITE, (shoulder_x, shoulder_y), (elbow_x, elbow_y), 3)
```

## Anti-Patterns

### ❌ Accessing Raw Dimensions in Child Methods

```python
def _draw_eyes(self, surface, left_pos, right_pos):
    # BAD: left_pos/right_pos already transformed, but pupils use raw center
    pupil_orbit_center = (self.width // 2, self.height // 2)  # Wrong!
    # Should use eye position centers instead
```

### ❌ Inconsistent Signature Patterns

```python
# BAD: Some methods accept cx/cy, others don't
def _draw_eyes(self, surface, positions):  # No cx/cy
    ...

def _draw_mouth(self, surface, points, cx, cy):  # Has cx/cy
    ...

def _draw_nose(self, surface):  # No parameters at all
    nose_x = self.width // 2  # Ignores transform
```

### ❌ Partial Transform Application

```python
def _draw_feature(self, surface, cx, cy):
    # BAD: Uses cx (transformed) but accesses self.height directly (not transformed)
    x = cx + offset
    y = self.height // 2 + offset  # Mixed coordinate systems!
```

## Benefits

1. **Coordinate System Consistency:** All rendered elements respect root transforms uniformly
2. **Transform Composability:** Multiple transform layers can be stacked without breaking child rendering
3. **Maintenance Clarity:** Clear data flow from root transform → position calculation → rendering
4. **Bug Prevention:** Eliminates coordinate system mismatch bugs (features rendering at wrong positions)
5. **Testability:** Can test rendering methods with arbitrary coordinate inputs

## Related Skills

- `ui-transform-layering` — Applying transforms at rendering root (this skill implements the propagation)
- `relative-coordinate-clamping` — Clamping child positions relative to transformed parents
- `orthogonal-animation-state` — Separating coordinate transforms from animation state

## Implementation Checklist

When adding coordinate transforms to a graphics system:

1. ✅ Apply transform at root (`center_x = base + offset`)
2. ✅ Update ALL rendering methods to accept `cx, cy` parameters
3. ✅ Pass transformed coordinates to all child calculation methods
4. ✅ Eliminate raw `self.width/height` access in rendering methods
5. ✅ Test with extreme transform values to verify consistency
6. ✅ Check special-case rendering paths (expressions, states) use coordinates properly

## Testing Strategy

Test coordinate propagation by:
1. **Baseline:** Render with zero offset/transform - verify features appear correctly
2. **Extreme transforms:** Apply large offsets in all directions - all features should move together
3. **Special cases:** Test state-specific rendering (expressions, animations) with transforms applied
4. **Visual inspection:** Features should maintain relative positions regardless of transform

Signs of coordinate propagation bugs:
- Some features move with transform, others stay fixed
- Features appear at wrong positions only with non-zero transforms
- Special-case rendering (expressions, states) ignores transforms
- Elements clip or disappear at certain transform values while others remain visible
