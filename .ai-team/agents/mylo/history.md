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
