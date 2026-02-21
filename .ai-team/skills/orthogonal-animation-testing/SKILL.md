# Skill: Orthogonal Animation Testing

**Owner:** Mylo (Tester)  
**Created:** 2026-02-20  
**Context:** Testing temporary animations that overlay expression state (blink, wink, roll eyes)

## What is This?

A reusable testing pattern for animations that are **orthogonal** to the main state machine (expression transitions). These animations temporarily modify rendering without changing the underlying state, then restore the original state.

Examples: blink, wink, eye roll, nod, bounce

## When to Use

Use this pattern when testing animations that:
1. Are **temporary** (start, run, complete, restore)
2. **Don't change** the main state (expression remains the same)
3. **Overlay** existing rendering (eyes close during blink, but expression is still "happy")
4. Need to **pause** during other priority animations
5. Must **restore** exact original state after completion

## Key Testing Components

### 1. State Machine Validation

Test the animation lifecycle through **state flags**, not visual rendering.

```python
def test_animation_sets_flag(self, fixture):
    pumpkin.animate()  # wink_left(), roll_clockwise(), etc.
    
    assert pumpkin.is_animating is True, \
        "Animation should set is_animating flag"
```

**Required state variables:**
- `is_animating` (bool) - Animation active flag
- `animation_progress` (float 0.0-1.0) - Progress through animation
- `animation_speed` (float) - Progress increment per update()
- `pre_animation_state` - Original state to restore

**Optional state variables:**
- Direction/target (e.g., `winking_eye='left'`, `rolling_direction='clockwise'`)
- Pause flag (e.g., `animation_paused` for interrupt handling)

### 2. Progress Tracking

Test that `animation_progress` advances correctly from 0.0 to 1.0.

```python
def test_animation_progress_advances(self, fixture):
    pumpkin.animate()
    initial_progress = pumpkin.animation_progress
    
    pumpkin.update()  # Advance one frame
    
    assert pumpkin.animation_progress > initial_progress, \
        "update() should advance animation_progress"
```

**Calculate iteration count for completion:**
```python
# If animation_speed = 0.03
# Need: 1.0 / 0.03 = 33.3 updates
# Add margin: 40 updates
for _ in range(40):
    pumpkin.update()

assert pumpkin.is_animating is False, \
    "Animation should complete after sufficient updates"
```

### 3. State Restoration

Test that original state is **exactly** restored after animation completes.

```python
def test_animation_restores_original_state(self, fixture):
    pumpkin.current_expression = Expression.ANGRY
    
    pumpkin.animate()
    
    # Complete animation
    for _ in range(40):
        pumpkin.update()
    
    assert pumpkin.current_expression == Expression.ANGRY, \
        "Animation should restore ANGRY, not default to NEUTRAL"
```

**Common mistake:** Forgetting to save original state before animation starts.

### 4. Non-Interruption Guard

Test that calling animation during active animation does **NOT** reset progress.

```python
def test_animation_does_not_interrupt_itself(self, fixture):
    pumpkin.animate()
    pumpkin.animation_progress = 0.5
    
    pumpkin.animate()  # Try to start again
    
    assert pumpkin.animation_progress == 0.5, \
        "Calling animate() during active animation should not reset"
```

### 5. Parametrized Expression Testing

Test animation works from **all** starting states.

```python
@pytest.mark.parametrize("expression", [
    Expression.NEUTRAL,
    Expression.HAPPY,
    Expression.SAD,
    Expression.ANGRY,
    Expression.SURPRISED,
    Expression.SCARED,
    Expression.SLEEPING,
])
def test_animation_from_all_expressions(self, fixture, expression):
    pumpkin.current_expression = expression
    pumpkin.animate()
    
    for _ in range(40):
        pumpkin.update()
    
    assert pumpkin.current_expression == expression, \
        f"Animation should restore {expression.value}"
```

### 6. Projection Mapping Compliance

Test that animation maintains pure black/white rendering.

```python
def test_animation_maintains_projection_colors(self, fixture):
    pumpkin.animate()
    
    # Advance to mid-animation
    for _ in range(15):
        pumpkin.update()
    
    pumpkin.draw(surface)
    
    # Sample entire surface
    intermediate_colors = set()
    for x in range(0, width, 20):  # Sparse sampling
        for y in range(0, height, 20):
            color = surface.get_at((x, y))[:3]
            if color != (0, 0, 0) and color != (255, 255, 255):
                intermediate_colors.add(color)
    
    assert len(intermediate_colors) == 0, \
        f"During animation, found non-projection colors: {intermediate_colors}"
```

### 7. Command Interface Testing

Test both socket commands and keyboard shortcuts trigger animation.

```python
def test_keyboard_shortcut_triggers_animation(self, fixture):
    pumpkin._handle_keyboard_input(pygame.K_b)  # B for blink
    
    assert pumpkin.is_animating is True, \
        "Keyboard shortcut should trigger animation"

def test_socket_command_triggers_animation(self, fixture):
    command = "animate_command"
    
    # Simulate socket handler
    if command == "animate_command":
        pumpkin.animate()
    
    assert pumpkin.is_animating is True, \
        "Socket command should trigger animation"
```

### 8. Animation Coordination (Pause/Resume)

Test that animations pause during priority interrupts (e.g., blink).

```python
def test_animation_pauses_during_blink(self, fixture):
    pumpkin.animate()
    
    # Advance partway
    for _ in range(10):
        pumpkin.update()
    
    progress_before_blink = pumpkin.animation_progress
    
    # Blink interrupts
    pumpkin.blink()
    
    # During blink, animation should pause
    for _ in range(5):
        pumpkin.update()
    
    if hasattr(pumpkin, 'animation_paused'):
        assert pumpkin.animation_paused is True
    
    # Complete blink
    for _ in range(40):
        pumpkin.update()
    
    # Animation should resume or be in valid state
    assert pumpkin.animation_progress >= progress_before_blink or \
           pumpkin.is_animating is False
```

## Test Organization Pattern

Organize tests into logical classes:

```python
class TestAnimationBasicBehavior:
    """State machine, progress, restoration."""
    # test_method_exists
    # test_sets_flag
    # test_progress_advances
    # test_restores_state
    # test_does_not_interrupt

class TestAnimationOrthogonalPattern:
    """Expression preservation across animation."""
    # test_saves_current_state
    # test_all_expressions_restore (parametrized)

class TestAnimationCommandInterface:
    """Keyboard shortcuts, socket commands."""
    # test_keyboard_shortcut
    # test_socket_command

class TestAnimationProjectionMapping:
    """Black/white compliance, contrast ratio."""
    # test_pure_black_white
    # test_contrast_ratio

class TestAnimationEdgeCases:
    """Rapid commands, state transitions, interrupts."""
    # test_blocks_during_priority
    # test_rapid_sequence
    # test_during_expression_transition
```

## Common Pitfalls

1. **Testing visual rendering instead of state machine**
   - ❌ Sample pixels to check if eyes are closed
   - ✅ Check `is_animating` and `animation_progress` flags

2. **Not testing restoration to exact state**
   - ❌ Assume animation returns to NEUTRAL
   - ✅ Test restoration to ANGRY, SLEEPING, etc.

3. **Forgetting non-interruption guard**
   - ❌ Allow rapid calls to reset progress
   - ✅ Guard: `if not self.is_animating: ...`

4. **Hard-coded iteration counts**
   - ❌ `for _ in range(34):`  # Why 34?
   - ✅ `for _ in range(40):  # 1.0/0.03=33.3, margin=40`

5. **Not parametrizing expression tests**
   - ❌ Copy-paste 7 identical tests
   - ✅ `@pytest.mark.parametrize("expression", [...])`

## Speed Guidelines

Animation speeds relative to expression transitions:

- **transition_speed**: 0.05 (expression changes)
- **blink_speed**: 0.03 (slower for natural feel)
- **wink_speed**: 0.03 (same as blink)
- **rolling_speed**: 0.02 (slowest, full 360° rotation)

Test that animation speeds are appropriate:

```python
def test_animation_speed_is_slower_than_transition(self, fixture):
    assert pumpkin.animation_speed <= pumpkin.transition_speed, \
        "Animation should be slower or equal to transition speed"
```

## Benefits of This Pattern

1. **Implementation-independent**: Tests validate behavior, not implementation details
2. **Deterministic**: Frame-based, no timing dependencies (time.sleep)
3. **Fast**: State machine checks are instant, no rendering delays
4. **Scalable**: Parametrized tests prevent copy-paste sprawl
5. **Specification**: Tests document expected behavior for implementers

## Related Skills

- Projection mapping validation (test_projection_mapping.py patterns)
- Pygame fixture patterns (init/quit lifecycle)
- Parametrized testing with pytest

## Examples in Codebase

- **test_projection_mapping.py** - TestBlinkAnimation class (lines 647-870)
- **test_winking.py** - Complete example with 9 test classes
- **test_rolling_eyes.py** - Complete example with geometric validation
