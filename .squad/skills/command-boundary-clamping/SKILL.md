---
name: "command-boundary-clamping"
description: "Pattern for safely clamping user-supplied numeric parameters to prevent extreme/invalid values"
domain: "input-validation"
confidence: "low"
source: "earned"
---

## Context

When implementing command handlers that accept numeric parameters (offsets, angles, scales, etc.), you need to prevent users from supplying extreme or invalid values that could break rendering, cause crashes, or produce unusable results.

**Key Challenge:** Balance flexibility (allowing wide range of values) with safety (preventing breakage). Hard constraints should be reasonable for the domain.

## Patterns

### 1. Inline Clamp Helper
Define a small helper function that clamps to min/max bounds:
```python
def set_projection_offset(self, x: int, y: int):
    """Set absolute projection offset. Clamped to [-500, +500]."""
    def clamp(v): return max(-500, min(500, int(v)))
    self.projection_offset_x = clamp(x)
    self.projection_offset_y = clamp(y)
```

**Why inline:** Clamp logic is usually specific to each parameter (different bounds). Inline helper is concise and co-located with the constraint documentation.

### 2. Symmetric Bounds for Bidirectional Parameters
Use symmetric bounds (e.g., ±500, ±90°) for parameters that have no inherent bias:
```python
# GOOD: Symmetric bounds for X/Y offset
self.projection_offset_x = clamp_to(-500, 500, x)
self.projection_offset_y = clamp_to(-500, 500, y)

# GOOD: Symmetric bounds for gaze angles
self.pupil_angle_x = clamp_to(-90, 90, angle_x)
```

**Why symmetric:** Makes behavior intuitive. User doesn't need to remember that "left is -300 but right is +500" — both directions have equal range.

### 3. Document Bounds in Docstrings
Always document the clamping range in method docstrings:
```python
def set_eyebrow(self, left: float, right: float = None):
    """Set eyebrow offsets. Negative = raise, positive = lower. Clamped to [-50, +50].
    
    Args:
        left: Offset for left eyebrow (if right not provided, applies to both)
        right: Offset for right eyebrow (optional)
    """
```

**Why document:** Callers (including UI code) need to know the valid range to display sliders, validate input fields, etc.

### 4. Clamp on Both Relative and Absolute Operations
Clamp both when setting absolute values AND when applying deltas:
```python
def jog_projection(self, dx: int, dy: int):
    """Adjust by delta. Clamped to [-500, +500]."""
    def clamp(v): return max(-500, min(500, int(v)))
    self.projection_offset_x = clamp(self.projection_offset_x + dx)  # Clamp result
    self.projection_offset_y = clamp(self.projection_offset_y + dy)
```

**Why clamp both:** Prevents accumulation. Without clamping, repeated small deltas could push state beyond bounds.

### 5. Silent Clamping vs. Error Reporting
For rendering/display parameters, silently clamp to bounds. For semantic violations, raise errors:
```python
# GOOD: Silent clamp for rendering parameters
self.projection_offset_x = max(-500, min(500, x))  # Just clamp

# GOOD: Raise error for semantic violations
if frame_count < 0:
    raise ValueError("frame_count must be non-negative")
```

**Why silent for rendering:** Users jogging controls near bounds don't want error messages. Just stop at the limit.

## Choosing Bounds

### Strategy 1: Physical Domain Constraints
Base bounds on physical reality:
- Projection offset: ±500px allows significant realignment without features disappearing on 1920x1080 display
- Gaze angle: ±90° matches human eye range-of-motion
- Eyebrow offset: ±50px prevents eyebrows from colliding with eyes or leaving visible area

### Strategy 2: Safety Margin Above "Usable" Range
Set bounds above typical use but below breakage:
```python
# Typical use: ±200px
# Breakage: Features disappear off-screen at ±960px (1920/2)
# Chosen bound: ±500px (2.5× typical, well below breakage)
```

### Strategy 3: Power-of-10 or Round Numbers
Use round numbers for discoverability:
```python
# GOOD: ±500px (round number, easy to remember)
# WORSE: ±473px (arbitrary, looks like it has deep meaning when it doesn't)
```

## Examples

**Projection Offset** (pumpkin_face.py):
- Bounds: ±500 pixels
- Rationale: Allows significant adjustment without causing features to disappear on standard displays
- Clamped on: `jog_projection`, `set_projection_offset`

**Eyebrow Offset** (pumpkin_face.py):
- Bounds: ±50 pixels
- Rationale: Prevents eyebrows from colliding with eyes or moving off-screen
- Clamped on: `set_eyebrow`, `raise_eyebrows`, `lower_eyebrows`, per-eyebrow methods

**Gaze Angle** (pumpkin_face.py):
- Bounds: ±90 degrees
- Rationale: Matches human eye range-of-motion (0° = straight ahead)
- Clamped on: `set_gaze`, `gaze` method

## Anti-Patterns

### ❌ No Bounds (Trusting User Input)
```python
# BAD: No clamping
def set_offset(self, x, y):
    self.offset_x = x  # User could pass 999999, crash rendering
```

### ❌ Asymmetric Bounds Without Rationale
```python
# BAD: Asymmetric without reason
self.offset_x = max(-300, min(500, x))  # Why different left/right limits?
```

### ❌ Magic Numbers (Undocumented Bounds)
```python
# BAD: No documentation
def set_offset(self, x, y):
    self.offset_x = max(-500, min(500, x))  # Why ±500? Caller doesn't know
```

### ❌ Only Clamping Absolute, Not Relative
```python
# BAD: set_offset clamps, but jog_offset doesn't
def jog_offset(self, dx, dy):
    self.offset_x += dx  # Could accumulate beyond bounds
```

Clamp consistently, document clearly, choose bounds based on domain understanding.
