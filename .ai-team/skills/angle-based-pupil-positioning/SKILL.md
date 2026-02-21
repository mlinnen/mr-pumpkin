# Skill: Angle-Based Pupil Positioning for 2D Eye Animation

**Author:** Ekko (Graphics Dev)  
**Date:** 2026-02-20  
**Confidence:** Medium (validated in production)  
**Domain:** Graphics rendering, 2D animation, circular motion

---

## Problem

Fixed offset pupil positioning (e.g., `-10, -10` from eye center) works for static expressions but fails for dynamic animations requiring circular motion like rolling eyes, eye tracking, or "looking around" effects.

## Solution

Use trigonometric angle-based positioning where pupils are placed at a distance from eye center along a specified angle:

```python
angle_rad = math.radians(roll_angle)
pupil_offset_x = pupil_distance * math.sin(angle_rad)
pupil_offset_y = pupil_distance * -math.cos(angle_rad)
pupil_position = (eye_center_x + pupil_offset_x, eye_center_y + pupil_offset_y)
```

**Angle Convention:**
- 0° = top (12 o'clock)
- 90° = right (3 o'clock)
- 180° = bottom (6 o'clock)
- 270° = left (9 o'clock)

**Note:** Y-axis is negated (`-math.cos`) because screen coordinates increase downward, opposite of mathematical convention.

## Benefits

1. **Smooth circular motion** - Pupils can rotate 360° around eye center with uniform motion
2. **Directional control** - Any "look direction" can be achieved by setting a single angle value
3. **Animation-friendly** - Simple linear interpolation of angle produces smooth arcs
4. **Composability** - Works with scaling, blinking, winking (multiply distance by scale factor)

## Implementation Details

### Constants
- `pupil_distance = 10` - Radius of pupil orbit around eye center (pixels)
- `default_angle = 315.0` - Upper-left position (matches common diagonal offset aesthetic)

### Scaling Integration
For animations that scale eye height (blink, wink), multiply distance by scale factor:
```python
pupil_offset_x = pupil_distance * eye_scale * math.sin(angle_rad)
pupil_offset_y = pupil_distance * eye_scale * -math.cos(angle_rad)
```

### Projection Mapping Compliance
- Use integer pixel positions: `int(pupil_offset_x)`, `int(pupil_offset_y)`
- Avoids subpixel rendering and anti-aliasing
- Maintains pure black (0,0,0) pupils for maximum contrast

## Use Cases

1. **Rolling eyes animation** - Interpolate angle from 0° to 360° over time
2. **Eye tracking** - Set angle based on target position: `angle = atan2(target_y - eye_y, target_x - eye_x)`
3. **Looking around** - Animate angle through keyframes (e.g., look left → center → right)
4. **Surprise expression** - Pupils centered (distance = 0) or wide-eyed (distance increased)

## Limitations

- Circular orbit only - pupils cannot move closer/farther from center dynamically (unless distance is animated separately)
- Requires trigonometric functions (minimal performance impact at 60 FPS, but consider caching for hundreds of animated objects)
- Default angle selection matters for visual consistency across expressions

## Example: Rolling Eyes

```python
# Clockwise roll starting from upper-left (315°)
for progress in range(0, 101):
    roll_angle = (315.0 + progress / 100 * 360) % 360
    # render pupil at roll_angle
```

## Related Patterns

- **Orthogonal animation system** - Angle-based positioning composes well with independent animation flags (is_blinking, is_rolling)
- **Projection mapping constraints** - Integer positioning avoids gray pixels that fail at oblique projection angles

## Confidence Justification

**Medium** - Implemented and tested in rolling eyes feature (Issue #10, PR #15). Validated that 315° default matches original diagonal look. Not yet tested at scale with multiple simultaneous eye animations or performance-critical scenarios.
