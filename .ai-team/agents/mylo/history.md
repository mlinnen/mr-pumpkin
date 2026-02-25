# History — Mylo

### Project Learnings (from import)

**Project:** Animated 2D Graphics Pumpkin Face (Python)  
**Owner:** Mike Linnen  
**Stack:** Python, 2D graphics, animation  
**Key domains:** Graphics/animation rendering, command parsing & state management, expression logic  
**Team composition:** Jinx (Lead), Ekko (Graphics), Vi (Backend), Mylo (Tester), Scribe, Ralph  

---

## Learnings

📌 Team update (2026-02-19): Projection mapping color scheme and test strategy finalized — decided by Ekko, Mylo

*Patterns, conventions, insights about testing, quality, and edge cases.*

### Test Infrastructure
- Created test_projection_mapping.py with comprehensive test suite for Issue #1
- Uses pytest framework with fixtures for pygame surface initialization
- Test classes organized by concern: Colors, Contrast, Expressions, Feature Completeness, Edge Cases

### Testing Patterns for Pygame Graphics
- Pixel sampling strategy: use sparse sampling (every 20th pixel) for performance
- Fixture pattern: init pygame, create surface, yield to test, quit pygame
- Color validation: use get_at() to sample specific coordinates
- Contrast testing: calculate luminance and ratio using WCAG formulas

### Projection Mapping Requirements (Issue #1)
- Background must be pure black (0,0,0) - no gray values
- Features (eyes, mouth) must be pure white (255,255,255)
- Minimum contrast ratio: 15:1 for reliable projection
- No intermediate colors allowed - binary black/white only
- All six expressions must work in projection mode

### Key Test Coverage Areas
- Color validation at multiple sample points (corners, edges, center)
- Contrast ratio calculation and validation (>15:1 required)
- All expression states (neutral, happy, sad, angry, surprised, scared)
- Expression transitions maintain projection colors
- Feature completeness (two eyes, mouth visible)
- Multiple resolutions (800x600, 1920x1080, 1024x768, 640x480)
- Rapid expression changes

### Test Implementation Notes
- Tests contain TODO markers for projection_mode flag (awaiting Ekko's implementation)
- Eye/mouth coordinate sampling uses approximate positions - may need adjustment
- Parametrized tests for all six expression states
- Edge case tests for resolution independence and rapid changes

### Sleeping Expression Tests (Issue #4) - 2026-02-19
**Proactive testing approach**: Wrote comprehensive test suite before implementation landed

**Patterns used from existing tests:**
- Fixture-based setup (pumpkin_projection) for consistent pygame initialization
- Pixel sampling strategy at specific coordinates to verify visual output
- Contrast ratio calculation using WCAG luminance formula (15:1 minimum)
- Binary color validation (only black 0,0,0 and white 255,255,255 allowed)
- Transition testing between all expression states
- Socket command and keyboard shortcut validation

**Edge cases discovered during test writing:**
- Closed eyes (horizontal lines) vs open eyes (circles) require different sampling strategy
  - Horizontal sampling along line for sleeping eyes
  - Vertical sampling to verify no circular pupil patterns
- Bidirectional transitions: both TO sleeping (from 6 expressions) and FROM sleeping (to 6 expressions)
- No pupils visible test distinguishes closed eyes from open eyes structurally
- Keyboard shortcut 7 mapping requires testing _handle_keyboard_input method directly

**Test structure for sleeping expression:**
1. Enum existence and value validation
2. Visual rendering (white horizontal lines)
3. Absence of pupils (structural difference from open eyes)
4. Projection mapping compliance (contrast + binary colors)
5. State transitions (6 to sleeping, sleeping to 6)
6. Command interfaces (socket "sleeping", keyboard 7)

**Collaboration notes:**
- Tests written while Ekko implements the feature (parallel development)
- May require minor coordinate adjustments once implementation details finalized
- Expression.SLEEPING enum and keyboard mapping (K_7) will need to be added by implementation

### Nose Movement Tests (Issue #19) - 2026-02-24
**Comprehensive test coverage**: 45 tests across 6 categories (state, animation, expression integration, commands, edge cases, rendering)

**Animation testing patterns learned:**
- **Frame progression testing:** Track `nose_animation_progress` from 0.0 to 1.0 over expected duration
  - Twitch: 30 frames at 60fps (0.5s) with tolerance of ±2 frames
  - Scrunch: 48 frames at 60fps (0.8s) with tolerance of ±2 frames
- **Deterministic state checks:** Verify state variables at specific animation progress points
  - Twitch oscillation: `offset_x = 8 * sin(progress * 2π * 5)` sampled at [0.0, 0.1, 0.25, 0.5, 1.0]
  - Scrunch phases: compress (0.0-0.35), hold (0.35-0.65), release (0.65-1.0) with scale validation
- **Easing validation:** Verify non-linear motion by checking delta variance (unique_deltas > 2)

**Edge case discovery:**
- **Non-interrupting guards:** Commands rejected during active animation (both same-type and cross-type)
  - `if not (is_twitching or is_scrunching):` prevents animation overlap
  - Reset command bypasses guard (immediate cancellation)
- **State composition:** Nose animation runs independently alongside:
  - Head movement (projection offset)
  - Expression transitions
  - Blink/wink animations
- **Auto-return behavior:** Animations auto-return to neutral (0, 0, 1.0) after completion
- **Timeout protection:** Animation completes and cleans up within expected duration (no hanging)

**Assertion patterns for animation state:**
- **Progress tracking:** Verify incremental progress with `assert progress > previous_progress`
- **Boundary clamping:** Test offset ranges (±30px) and scale ranges (0.5-1.2)
- **Easing curves:** Sample offset values at key progress points and validate against formula
- **State orthogonality:** Verify animation state preserved across expression changes and head movement

**Expression integration testing approach:**
- **State persistence:** Nose offset/scale values survive expression changes (tested across 6 expressions)
- **Animation continuity:** Mid-animation expression changes don't interrupt nose animation
- **Independent state machines:** Nose flags (`is_twitching`, `is_scrunching`) orthogonal to `current_expression`
- **Composition testing:** Verify both states (expression + nose animation) coexist without conflict

**Rendering validation patterns:**
- **Position verification:** Sample white pixels at expected nose position (center_y + 15)
- **Projection compliance:** Verify pure black/white colors only (no anti-aliasing)
- **Offset application:** Test nose follows projection offset (head position)
- **Animation visibility:** Verify twitch displacement (X-offset) and scrunch compression (Y-scale) in rendered frames
- **Geometry checks:** Sample vertical range adjusted for scale (50% scrunch = reduced sample range)

**Test organization:**
- **6 test classes:** StateManagement (8), Animations (10), ExpressionIntegration (7), CommandIntegration (6), EdgeCases (8), Rendering (6)
- **Fixtures:** `pumpkin` for state tests, `pumpkin_surface` for rendering tests
- **Parametrized approach:** Iterate through all expressions for persistence tests
- **Progressive complexity:** Start with initialization, then single animations, then composition, then edge cases

**Key testing insights:**
- Simulating update loop manually: `progress += delta_time / duration` in test loop
- Tolerance for frame counts: ±2 frames acceptable for 60fps timing (system variance)
- Rendering tests use sparse sampling (every 5-10 pixels) for performance
- Animation formula testing separated from integration testing (unit vs. integration)
