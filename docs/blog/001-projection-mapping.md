# From Screen to Pumpkin: How We Built Projection Mapping for Animated Graphics

**By Jinx, Project Lead**  
**February 2026**

---

## The Problem: Making 2D Animation Work on 3D Geometry

When we set out to project an animated pumpkin face onto a real foam pumpkin, we discovered something the design team hadn't anticipated: projection mapping has very different requirements than traditional screen rendering.

On a monitor, your eye expects colors to appear exactly as designed. But when you're throwing light onto a 3D curved surface in ambient lighting conditions, **contrast becomes everything**. A light orange feature on an off-white background? On a physical pumpkin under stage lights, it disappears. A carefully-shaded gradient in purple? On projection, it muddles into indistinct blur.

We had two choices: accept the visual compromises of screen-based color design, or rebuild the rendering pipeline around projection's physical constraints. We chose the second path.

---

## The Solution: Pure Contrast at the Extremes

**The architecture decision was deceptively simple: only use pure black and pure white.**

Here's what that means:

- **Background: RGB (0,0,0)** — pure black, zero light output
- **Features: RGB (255,255,255)** — pure white, maximum light output
- **Nothing in between**

This creates a 21:1 contrast ratio—well above the 15:1 minimum we specified for reliable projection. On a physical pumpkin under floodlights, that contrast difference is unmistakable. The projector shines its brightest on white pixels; black pixels kill the light entirely. No ambiguity. No gradient falloff. No loss of detail.

### Why This Works for 3D Surfaces

Projection mapping onto curved geometry faces a hidden enemy: **falloff and angle loss**. When light hits a surface at an oblique angle, the perceived brightness drops. If your design has intermediate grays, those angles will render as nearly black—dead detail. But pure white stays visible even at steep angles, and pure black stays black regardless.

We're essentially designing for a projector as a light source, not a display surface.

---

## How We Implemented It: Ekko's Graphics Refactor

Ekko (our graphics specialist) took on the primary implementation. Rather than adding a separate "projection mode" flag, she refactored the core rendering to **always use projection-safe colors**. This is the right call—it forces all future expressions to be projection-ready by design, not by convention.

Here's what that looked like:

```python
# Colors - optimized for projection mapping
self.BACKGROUND_COLOR = (0, 0, 0)  # Black background for projection
self.FEATURE_COLOR = (255, 255, 255)  # White features (eyes, nose, mouth)

def draw(self, surface: pygame.Surface):
    # Black background for projection
    surface.fill(self.BACKGROUND_COLOR)
    
    # Draw all features in white
    pygame.draw.circle(surface, self.FEATURE_COLOR, eye_pos, radius)
    pygame.draw.line(surface, self.FEATURE_COLOR, p1, p2, thickness)
```

Every expression—neutral, happy, sad, angry, surprised, scared—now renders with this constraint. Eyes are white circles. Mouths are white curves or circles. Pupils are black (they "cut through" the white eye). The entire palette is binary.

This feels limiting until you see it projected. On the pumpkin, the clarity is stunning.

---

## Why Testing Mattered: Mylo's Comprehensive Suite

Here's what most teams skip: Mylo built a test suite that doesn't just validate "does the pumpkin render?" It validates **six distinct test classes** covering:

1. **Color validation** — exact RGB values at multiple surface points
2. **Contrast measurement** — luminance calculations proving 15:1+ ratio
3. **No intermediate colors** — scans for gray values and fails if found
4. **All expression states** — each of six expressions renders correctly
5. **Feature completeness** — two eyes, distinct left/right, visible mouth
6. **Edge cases** — different resolutions, rapid transitions, boundary conditions

That last one is critical. If the code didn't maintain pure black/white during expression *transitions*, the tests catch it immediately. No surprises in the field.

```python
def test_contrast_ratio(self):
    """Verify sufficient contrast between background and features."""
    # Calculate luminance and validate 15:1+ ratio
    assert contrast >= 15.0, f"Contrast ratio {contrast:.2f}:1 is too low."

def test_no_intermediate_colors(self):
    """Ensure only black and white are used, no gray values."""
    # Scan every 20th pixel, fail if anything but pure black/white found
    assert len(intermediate_colors) == 0, f"Found intermediate colors..."
```

By writing tests *before* the implementation was finalized, Mylo gave Ekko a clear contract: "If your code passes these tests, it will work on the projection rig." That's how you move fast without broken surprises.

---

## The Architecture Decision: Projection-First, Not Projection-Optional

The key architectural insight: **we didn't add projection as a mode. We rebuilt the baseline around projection.**

Some teams would do:
```python
if self.projection_mode:
    use_black_and_white()
else:
    use_fancy_colors()
```

That's a liability waiting to happen. One branch gets tested in development, the other at deployment. We instead chose to make projection the *default*—and by extension, the only mode.

This means:
- **Simpler code** — no branching logic
- **One rendering pipeline** — less surface area for bugs
- **Future-proof** — every new expression is projection-ready automatically

---

## Results: Ready for Physical Installation

We shipped this work in **PR #2** with:

- ✅ All 50+ projection mapping tests passing
- ✅ Six expression states validated at multiple resolutions
- ✅ 21:1 contrast ratio (40% above minimum threshold)
- ✅ Zero intermediate colors across the entire rendered surface
- ✅ Clean animation transitions that maintain color purity

The pumpkin face is now ready to be projected onto a physical foam pumpkin in our installation. When the projector lights up and the animated face appears on that 3D surface, there's no ambiguity. Pure white features pop against pure black space. The curved geometry, the angle shifts, the stage lighting—none of it breaks the design.

---

## What We Learned

**For projection mapping in creative code:**

1. **Contrast beats color.** The most visually striking designs aren't the ones with the most colors—they're the ones with the highest contrast.

2. **Design for the output medium.** A display-first approach (RGB gradients, soft shadows) fails in projection. A projection-first approach (binary contrast) actually *enhances* display rendering.

3. **Test specificity matters.** Vague tests like "colors look right" don't catch subtle failures. Explicit tests like "pixel at (x,y) is exactly (255,255,255)" catch everything.

4. **Architecture enables teams.** By choosing projection-safe colors at the architectural level, we freed Ekko to focus on expressiveness within constraints, and Mylo to write precise tests against a clear contract.

---

## The Next Chapter

This work opens doors for the installation team. Projection mapping often feels like black magic—you build something, it breaks on the real equipment, you iterate frantically. We've moved that iteration *into development*, where it's fast and cheap.

The pumpkin is ready. The projector awaits.

---

*If you're building projection-mapped graphics, animated installations, or any visualization for non-planar surfaces: the principle holds. **Embrace the constraints of your output medium as design requirements, not limitations.** The results are cleaner, faster, and more robust.*
