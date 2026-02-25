---
name: "pygame-graphics-testing"
description: "Patterns for testing pygame-based graphics and visual output"
domain: "testing"
confidence: "low"
source: "earned"
---

## Context
When testing pygame-based graphics applications, pixel-perfect validation is needed but can be performance-intensive. These patterns enable efficient, reliable testing of visual output including colors, contrast, and feature presence.

## Patterns

### Fixture Pattern for Pygame Surface
Create a pytest fixture that initializes pygame, creates a surface, yields to the test, then cleans up. This ensures proper lifecycle management and prevents resource leaks.

```python
@pytest.fixture
def graphics_surface():
    pygame.init()
    surface = pygame.Surface((800, 600))
    yield surface
    pygame.quit()
```

### Sparse Pixel Sampling
Instead of checking every pixel (expensive), sample strategically:
- **Corners and edges** for background validation
- **Known feature locations** for presence checks
- **Every Nth pixel** (e.g., 20) for full-surface scans

```python
# Sample corners
test_points = [(10, 10), (790, 10), (10, 590), (790, 590)]
for point in test_points:
    color = surface.get_at(point)[:3]  # RGB only
    assert color == expected_color

# Sparse full scan
for x in range(0, width, 20):
    for y in range(0, height, 20):
        color = surface.get_at((x, y))[:3]
        # validate color
```

### Color Validation
Use `get_at()` to sample pixel colors, but extract only RGB (first 3 values) to ignore alpha:
```python
color = surface.get_at((x, y))[:3]  # (R, G, B) tuple
```

### Contrast Ratio Testing
Calculate luminance and contrast ratio using WCAG formulas:
```python
def luminance(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def contrast_ratio(color1, color2):
    lum1 = luminance(color1)
    lum2 = luminance(color2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)

# For projection mapping, require 15:1 minimum
assert contrast_ratio(bg_color, feature_color) >= 15.0
```

### Parametrized State Testing
When testing multiple states (expressions, modes, etc.), use pytest parametrize:
```python
@pytest.mark.parametrize("state", [State.A, State.B, State.C])
def test_all_states(graphics_surface, state):
    app.set_state(state)
    app.draw(graphics_surface)
    # validate rendering
```

### Feature Presence Detection
To verify a feature is visible, check for expected colors in the feature's region:
```python
# Check if mouth exists in expected region
has_feature = any(
    surface.get_at((x, y))[:3] == feature_color
    for x in range(x_start, x_end, 10)
    for y in range(y_start, y_end, 10)
)
assert has_feature, "Feature should be visible"
```

### Resolution Independence Testing
Test at multiple resolutions to ensure scaling works correctly:
```python
@pytest.mark.parametrize("resolution", [(800,600), (1920,1080), (640,480)])
def test_resolution(resolution):
    width, height = resolution
    surface = pygame.Surface((width, height))
    app = GraphicsApp(width=width, height=height)
    app.draw(surface)
    # validate corners are correct color
```

### Transition Testing
When testing animations or transitions, set progress directly to skip real-time waiting:
```python
app.set_state(new_state)
app.transition_progress = 0.5  # Mid-transition
app.draw(surface)
# Validate intermediate state
```

## Examples

### Complete Test Class Structure
```python
class TestGraphicsOutput:
    @pytest.fixture
    def app_surface(self):
        pygame.init()
        app = GraphicsApp(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield app, surface
        pygame.quit()
    
    def test_background_color(self, app_surface):
        app, surface = app_surface
        app.draw(surface)
        
        # Check corners
        for x, y in [(10,10), (790,10), (10,590), (790,590)]:
            color = surface.get_at((x, y))[:3]
            assert color == (0, 0, 0)
    
    @pytest.mark.parametrize("state", list(State))
    def test_all_states_render(self, app_surface, state):
        app, surface = app_surface
        app.set_state(state)
        app.current_state = state  # Skip transition
        app.draw(surface)
        
        # Verify render completed without errors
        assert surface is not None
```

## Anti-Patterns
- **Checking every pixel** — Use sparse sampling instead (every 10th or 20th pixel)
- **Forgetting pygame.quit()** — Always clean up in fixture teardown
- **Including alpha in color checks** — Use `[:3]` to get RGB only
- **Waiting for real-time transitions** — Set progress directly in tests
- **Hardcoded coordinates** — Calculate based on resolution when possible

## When to Apply
- Testing pygame graphics applications
- Validating color schemes (e.g., projection mapping, accessibility)
- Testing visual state machines (expressions, animations)
- Verifying contrast ratios and color accuracy
- Testing resolution independence
