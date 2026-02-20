# History — Ekko

### Project Learnings (from import)

**Project:** Animated 2D Graphics Pumpkin Face (Python)  
**Owner:** Mike Linnen  
**Stack:** Python, 2D graphics, animation  
**Key domains:** Graphics/animation rendering, command parsing & state management, expression logic  
**Team composition:** Jinx (Lead), Ekko (Graphics), Vi (Backend), Mylo (Tester), Scribe, Ralph  

---

## Learnings

📌 Team update (2026-02-19): Projection mapping color scheme and test strategy finalized — decided by Ekko, Mylo

### Projection Mapping Graphics

**File:** `pumpkin_face.py`
- Primary rendering logic for animated pumpkin face
- PyGame-based 2D vector graphics rendering
- Fullscreen display with multi-monitor support
- 6 expression states: neutral, happy, sad, angry, surprised, scared

**Projection Mapping Pattern:**
- Black background (0,0,0) prevents light bleed when projecting
- White features (255,255,255) for maximum contrast and projection brightness
- Remove decorative elements (pumpkin body, ridges) - projector maps onto physical object
- Thicker line weights (8px) improve visibility at projection distances
- Inverted pupils (black on white) maintain facial depth perception

**Graphics Architecture:**
- `draw()` - Main rendering loop, fills background and calls feature rendering
- `_get_eye_positions()` - Calculates dynamic eye placement per expression
- `_get_mouth_points()` - Generates mouth curve geometry for each emotion
- `_draw_eyes()` - Renders filled circles for eyes with centered pupils
- `_draw_mouth()` - Handles both line-based (smile/frown) and shape-based (surprised/scared) mouths

**Animation System:**
- Expression transitions use `transition_progress` (0.0 to 1.0)
- Smooth interpolation at 60 FPS via `transition_speed`
- State machine pattern: `current_expression` → `target_expression`

### Sleeping Expression Implementation (Issue #4)

**Eye Rendering for Closed Eyes:**
- `_draw_eyes()` checks for `Expression.SLEEPING` before rendering standard circle eyes
- Closed eyes rendered as horizontal white lines (60px width, 8px thickness)
- Early return pattern prevents rendering open eye circles when sleeping
- Uses same projection mapping contrast: white lines on black background

**Pattern for Adding New Expressions:**
1. Add enum value to `Expression` class
2. Update rendering logic in appropriate method (`_draw_eyes()`, `_draw_mouth()`, `_get_eye_positions()`)
3. Add keyboard mapping in `_handle_keyboard_input()`
4. Socket server automatically handles new enum values via `Expression(data)` pattern

**Architectural Insight:**
- Expression-specific rendering uses conditional checks within draw methods
- Socket server's enum-based parsing means no server code changes needed for new expressions
- Projection mapping constraints (black/white, thick lines) guide all visual design choices
