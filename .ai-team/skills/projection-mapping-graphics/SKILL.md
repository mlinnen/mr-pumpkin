---
name: "projection-mapping-graphics"
description: "Patterns for designing graphics optimized for physical projection mapping"
domain: "graphics"
confidence: "low"
source: "earned"
---

## Context
Projection mapping differs fundamentally from standard display graphics. When projecting 2D images onto 3D physical objects, the graphics must be optimized for light behavior, contrast, and spatial mapping rather than traditional aesthetic presentation.

## Patterns

### Inverted Color Scheme
For projection onto light-colored objects (foam, white surfaces):
- **Background:** Pure black (0, 0, 0) - prevents light emission where no features should appear
- **Features:** Pure white (255, 255, 255) - maximum brightness for projected illumination
- **Contrast ratio:** Aim for 21:1 (black-to-white) for cleanest projection

```python
# Standard colors for projection mapping
BACKGROUND_COLOR = (0, 0, 0)      # Black - no light
FEATURE_COLOR = (255, 255, 255)   # White - maximum brightness
```

### Minimalist Feature Design
Remove decorative elements that exist on the physical object:
- If projecting onto a carved pumpkin, don't render the pumpkin body
- Only render features that should illuminate (eyes, nose, mouth)
- Let the physical object provide form; projection provides expression

**Before (display graphics):**
```python
# Draw pumpkin body
pygame.draw.circle(surface, ORANGE, center, radius)
# Draw ridges
for i in range(8):
    pygame.draw.circle(surface, BROWN, ridge_pos, 20, 2)
```

**After (projection mapping):**
```python
# Black background only - physical pumpkin IS the body
surface.fill(BACKGROUND_COLOR)
# Only draw animated features (eyes, mouth)
```

### Enhanced Line Weights
Projection distances require thicker strokes for visibility:
- Standard display: 2-4px lines
- Projection mapping: 6-10px lines
- Scale based on projection distance and surface texture

```python
# Display graphics
pygame.draw.line(surface, color, p1, p2, 4)

# Projection mapping
pygame.draw.line(surface, FEATURE_COLOR, p1, p2, 8)
```

### Fill vs. Outline Strategy
Solid fills project better than thin outlines:
- **Prefer:** Filled shapes (`pygame.draw.circle(surface, color, pos, radius)`)
- **Avoid:** Thin outlines (`pygame.draw.circle(surface, color, pos, radius, 2)`)
- Exception: Thick outlines (6px+) can work for specific effects

```python
# Good for projection - filled circle
pygame.draw.circle(surface, FEATURE_COLOR, eye_pos, 40)

# Poor for projection - thin outline
pygame.draw.circle(surface, FEATURE_COLOR, eye_pos, 40, 2)
```

### Inverted Details
When features need internal detail (pupils, highlights):
- Use background color (black) for details within white features
- Creates silhouette effect that reads well at distance

```python
# White eye with black pupil
pygame.draw.circle(surface, FEATURE_COLOR, eye_pos, 40)  # White eye
pygame.draw.circle(surface, BACKGROUND_COLOR, pupil_pos, 15)  # Black pupil
```

### Resolution Considerations
Projection resolution often differs from source resolution:
- Design at target resolution (e.g., 1920x1080 for HD projector)
- Test feature visibility at actual projection scale
- Avoid sub-pixel details that disappear when projected

## Examples

### Complete Projection-Mapped Renderer

```python
class ProjectionRenderer:
    def __init__(self, width=1920, height=1080):
        self.width = width
        self.height = height
        self.BACKGROUND = (0, 0, 0)
        self.FEATURE = (255, 255, 255)
    
    def draw(self, surface):
        # Black background - no light emission
        surface.fill(self.BACKGROUND)
        
        center_x = self.width // 2
        center_y = self.height // 2
        
        # White filled eyes (solid for projection)
        eye_radius = 40
        left_eye = (center_x - 100, center_y - 50)
        right_eye = (center_x + 100, center_y - 50)
        
        pygame.draw.circle(surface, self.FEATURE, left_eye, eye_radius)
        pygame.draw.circle(surface, self.FEATURE, right_eye, eye_radius)
        
        # Black pupils within white eyes
        pupil_radius = 15
        pygame.draw.circle(surface, self.BACKGROUND, 
                          (left_eye[0] - 10, left_eye[1] - 10), pupil_radius)
        pygame.draw.circle(surface, self.BACKGROUND,
                          (right_eye[0] - 10, right_eye[1] - 10), pupil_radius)
        
        # Thick white smile curve
        mouth_points = self._generate_smile_curve(center_x, center_y + 80)
        for i in range(len(mouth_points) - 1):
            pygame.draw.line(surface, self.FEATURE, 
                           mouth_points[i], mouth_points[i+1], 8)
```

### Testing Projection Graphics

```python
def test_projection_contrast(projection_renderer, surface):
    projection_renderer.draw(surface)
    
    # Verify pure black background
    bg_color = surface.get_at((10, 10))[:3]
    assert bg_color == (0, 0, 0), "Background must be pure black"
    
    # Verify white features
    feature_color = surface.get_at((center_x, center_y))[:3]
    assert feature_color == (255, 255, 255), "Features must be pure white"
    
    # Verify maximum contrast ratio
    def luminance(rgb):
        r, g, b = [x / 255.0 for x in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    bg_lum = luminance(bg_color)
    feat_lum = luminance(feature_color)
    contrast = (feat_lum + 0.05) / (bg_lum + 0.05)
    
    assert contrast >= 21.0, f"Need 21:1 contrast for projection, got {contrast:.1f}:1"
```

## Anti-Patterns
- **Using grayscale gradients** — Projectors lose subtle shading; use solid white
- **Decorative backgrounds** — Any non-black pixels will project unwanted light
- **Thin outlines (< 4px)** — Invisible at projection distances
- **Subtle color tints** — Stick to pure black (0,0,0) and white (255,255,255)
- **Rendering the physical object** — The object itself provides form

## When to Apply
- Projecting animations onto physical objects (props, buildings, sculptures)
- Mapping facial expressions onto masks or statues
- Architectural projection mapping
- Interactive installations with projected elements
- Any scenario where 2D graphics illuminate 3D surfaces

## Related Skills
- `pygame-graphics-testing` — Testing patterns for validating projection graphics
- Color contrast validation for accessibility (adapted for projection needs)
