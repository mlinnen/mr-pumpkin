# History — Jinx

### Project Learnings (from import)

**Project:** Animated 2D Graphics Pumpkin Face (Python)  
**Owner:** Mike Linnen  
**Stack:** Python, 2D graphics, animation  
**Key domains:** Graphics/animation rendering, command parsing & state management, expression logic  
**Team composition:** Jinx (Lead), Ekko (Graphics), Vi (Backend), Mylo (Tester), Scribe, Ralph  

---

## Learnings

*Patterns, conventions, and decisions discovered during work.*

### Projection Mapping Architecture
- **Pure contrast design principle**: Projection mapping on 3D surfaces demands binary color schemes (black/white) rather than gradients or intermediate tones. Falloff at oblique angles eliminates gray values entirely.
- **Projection-first, not projection-optional**: Build the core rendering around projection constraints rather than adding a feature flag. Single pipeline reduces bugs and makes all future features projection-ready by design.
- **15:1 contrast as minimum threshold**: Our 21:1 ratio (RGB 0,0,0 to 255,255,255) provides 40% safety margin for real-world conditions (stage lighting, curved geometry, angle loss).

### Testing Patterns
- **Specificity beats coverage**: Tests that check "pixel at (x,y) equals (255,255,255)" catch subtle color drift that "colors look right" misses.
- **Proactive test-driven architecture**: Mylo's 6-class, 50+ test suite defined the contract before Ekko's implementation. This enabled parallel work and confidence in deployment.
- **Edge cases first**: Resolution independence, rapid transitions, and boundary conditions caught in development, not in the field.

### Team Workflow
- **Constraint-based design unlocks expressiveness**: By treating projection colors as architectural constraints, Ekko had clear boundaries for all expression designs (six states across multiple resolutions).
- **Architectural ownership by Lead**: Project lead (Jinx) establishes rendering pipeline constraints; domain specialists (Ekko, Mylo) execute within those constraints at high velocity.

### File References
- **pumpkin_face.py**: Core rendering with projection-safe colors (BACKGROUND_COLOR, FEATURE_COLOR) baked into base class
- **test_projection_mapping.py**: 6 test classes validating color purity, contrast, expressions, and edge cases
- **blog-post-projection-mapping.md**: Narrative explanation of projection mapping architecture for team + developer audience
