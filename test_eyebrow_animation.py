"""
Test suite for eyebrow animation feature (Issue #16).

These tests validate the eyebrow control system where:
- Eyebrows have independent left/right offsets (pixels, clamped [-50, +50])
- Negative offset = raise (move up), positive offset = lower (move down)
- Eyebrow state is orthogonal to expression state machine
- Eyebrows are hidden during SLEEPING expression (but state preserved)
- Blink/wink animations apply temporary lift to eyebrows

Author: Mylo (Tester)
"""

import pygame
import pytest
import math
from pumpkin_face import PumpkinFace, Expression


class TestEyebrowStateVariables:
    """Test eyebrow state variable behavior and clamping."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=800, height=600)
        yield face
        pygame.quit()
    
    def test_default_offsets(self, pumpkin):
        """Both eyebrow offsets start at 0.0."""
        assert pumpkin.eyebrow_left_offset == 0.0
        assert pumpkin.eyebrow_right_offset == 0.0
    
    def test_set_eyebrow_both(self, pumpkin):
        """set_eyebrow(-20) sets both eyebrows to -20.0."""
        pumpkin.set_eyebrow(-20)
        assert pumpkin.eyebrow_left_offset == -20.0
        assert pumpkin.eyebrow_right_offset == -20.0
    
    def test_set_eyebrow_independent(self, pumpkin):
        """set_eyebrow(-10, 20) sets left=-10, right=20."""
        pumpkin.set_eyebrow(-10, 20)
        assert pumpkin.eyebrow_left_offset == -10.0
        assert pumpkin.eyebrow_right_offset == 20.0
    
    def test_clamp_upper_limit(self, pumpkin):
        """set_eyebrow(100) clamps to 50.0."""
        pumpkin.set_eyebrow(100)
        assert pumpkin.eyebrow_left_offset == 50.0
        assert pumpkin.eyebrow_right_offset == 50.0
    
    def test_clamp_lower_limit(self, pumpkin):
        """set_eyebrow(-100) clamps to -50.0."""
        pumpkin.set_eyebrow(-100)
        assert pumpkin.eyebrow_left_offset == -50.0
        assert pumpkin.eyebrow_right_offset == -50.0
    
    def test_raise_lowers_y_value(self, pumpkin):
        """After raise_eyebrows, offset decreases (goes negative)."""
        initial_offset = pumpkin.eyebrow_left_offset
        pumpkin.raise_eyebrows()
        assert pumpkin.eyebrow_left_offset < initial_offset
        assert pumpkin.eyebrow_right_offset < initial_offset
    
    def test_lower_increases_y_value(self, pumpkin):
        """After lower_eyebrows, offset increases."""
        initial_offset = pumpkin.eyebrow_left_offset
        pumpkin.lower_eyebrows()
        assert pumpkin.eyebrow_left_offset > initial_offset
        assert pumpkin.eyebrow_right_offset > initial_offset
    
    def test_reset_eyebrows(self, pumpkin):
        """After offset changes, reset_eyebrows sets both to 0.0."""
        pumpkin.set_eyebrow(-30, 25)
        pumpkin.reset_eyebrows()
        assert pumpkin.eyebrow_left_offset == 0.0
        assert pumpkin.eyebrow_right_offset == 0.0


class TestEyebrowOrthogonality:
    """Test that eyebrow state is independent of expression state."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=800, height=600)
        yield face
        pygame.quit()
    
    def test_expression_change_preserves_offsets(self, pumpkin):
        """Set offset, change expression, offset unchanged."""
        pumpkin.set_eyebrow(-20)
        pumpkin.set_expression(Expression.HAPPY)
        assert pumpkin.eyebrow_left_offset == -20.0
        assert pumpkin.eyebrow_right_offset == -20.0
    
    @pytest.mark.parametrize("expression", [
        Expression.NEUTRAL,
        Expression.HAPPY,
        Expression.SAD,
        Expression.ANGRY,
        Expression.SURPRISED,
        Expression.SCARED,
        Expression.SLEEPING
    ])
    def test_all_expressions_preserve_offsets(self, pumpkin, expression):
        """Parametrized: all 7 expressions preserve eyebrow offset."""
        pumpkin.set_eyebrow(-15, 30)
        pumpkin.set_expression(expression)
        assert pumpkin.eyebrow_left_offset == -15.0
        assert pumpkin.eyebrow_right_offset == 30.0
    
    def test_raise_during_transition(self, pumpkin):
        """Set offset while transition_progress < 1.0, offset is set."""
        pumpkin.set_expression(Expression.HAPPY)
        pumpkin.transition_progress = 0.5  # Mid-transition
        pumpkin.set_eyebrow(-25)
        assert pumpkin.eyebrow_left_offset == -25.0
        assert pumpkin.eyebrow_right_offset == -25.0
    
    def test_independent_left_right(self, pumpkin):
        """raise_eyebrow_left leaves right unchanged, and vice versa."""
        pumpkin.set_eyebrow(0, 0)
        pumpkin.raise_eyebrow_left()
        assert pumpkin.eyebrow_left_offset == -10.0
        assert pumpkin.eyebrow_right_offset == 0.0
        
        pumpkin.lower_eyebrow_right()
        assert pumpkin.eyebrow_left_offset == -10.0
        assert pumpkin.eyebrow_right_offset == 10.0


class TestEyebrowCommands:
    """Test eyebrow command methods (state-level, not socket-level)."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=800, height=600)
        yield face
        pygame.quit()
    
    def test_raise_step_size(self, pumpkin):
        """raise_eyebrows() decrements by 10.0."""
        pumpkin.set_eyebrow(0)
        pumpkin.raise_eyebrows()
        assert pumpkin.eyebrow_left_offset == -10.0
        assert pumpkin.eyebrow_right_offset == -10.0
    
    def test_lower_step_size(self, pumpkin):
        """lower_eyebrows() increments by 10.0."""
        pumpkin.set_eyebrow(0)
        pumpkin.lower_eyebrows()
        assert pumpkin.eyebrow_left_offset == 10.0
        assert pumpkin.eyebrow_right_offset == 10.0
    
    def test_raise_right_only(self, pumpkin):
        """raise_eyebrow_right leaves left unchanged."""
        pumpkin.set_eyebrow(5, 5)
        pumpkin.raise_eyebrow_right()
        assert pumpkin.eyebrow_left_offset == 5.0
        assert pumpkin.eyebrow_right_offset == -5.0
    
    def test_lower_left_only(self, pumpkin):
        """lower_eyebrow_left leaves right unchanged."""
        pumpkin.set_eyebrow(-5, -5)
        pumpkin.lower_eyebrow_left()
        assert pumpkin.eyebrow_left_offset == 5.0
        assert pumpkin.eyebrow_right_offset == -5.0
    
    def test_sequential_raises(self, pumpkin):
        """6x raise → offset = -50.0 (clamped, not -60.0)."""
        pumpkin.set_eyebrow(0)
        for _ in range(6):
            pumpkin.raise_eyebrows()
        assert pumpkin.eyebrow_left_offset == -50.0
        assert pumpkin.eyebrow_right_offset == -50.0
    
    def test_sequential_lowers(self, pumpkin):
        """6x lower → offset = 50.0 (clamped, not 60.0)."""
        pumpkin.set_eyebrow(0)
        for _ in range(6):
            pumpkin.lower_eyebrows()
        assert pumpkin.eyebrow_left_offset == 50.0
        assert pumpkin.eyebrow_right_offset == 50.0


class TestEyebrowRendering:
    """Test eyebrow rendering behavior (requires Ekko's _draw_eyebrows implementation)."""
    
    @pytest.fixture
    def pumpkin_surface(self):
        """Create a PumpkinFace instance with test surface."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        surface = pygame.Surface((1920, 1080))
        yield face, surface
        pygame.quit()
    
    @pytest.mark.skip(reason="Waiting for Ekko's _draw_eyebrows implementation")
    def test_eyebrows_drawn_in_neutral(self, pumpkin_surface):
        """Call face.draw(surface), verify white pixels exist above eye center Y."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.draw(surface)
        
        # Check for white pixels in eyebrow region (above eye centers)
        center_x = 1920 // 2
        center_y = 1080 // 2
        left_eye_x = center_x - 100
        right_eye_x = center_x + 100
        eye_y = center_y - 50  # Approximate eye position
        
        # Sample above eyes (eyebrow region)
        eyebrow_y = eye_y - 55  # y_gap from spec
        white_pixels = 0
        for eye_x in [left_eye_x, right_eye_x]:
            for offset in [-20, -10, 0, 10, 20]:
                color = surface.get_at((eye_x + offset, eyebrow_y))[:3]
                if color == (255, 255, 255):
                    white_pixels += 1
        
        assert white_pixels > 0, "Eyebrows should be visible (white pixels above eyes)"
    
    @pytest.mark.skip(reason="Waiting for Ekko's _draw_eyebrows implementation")
    def test_eyebrows_hidden_in_sleeping(self, pumpkin_surface):
        """Draw with SLEEPING expression, verify NO white pixels in eyebrow region."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.SLEEPING)
        pumpkin.draw(surface)
        
        # Check eyebrow region for any white pixels
        center_x = 1920 // 2
        center_y = 1080 // 2
        left_eye_x = center_x - 100
        right_eye_x = center_x + 100
        eye_y = center_y - 50
        
        # Sample above eyes (eyebrow region)
        eyebrow_y = eye_y - 55
        white_pixels_in_brow_region = 0
        for eye_x in [left_eye_x, right_eye_x]:
            for offset in [-30, -20, -10, 0, 10, 20, 30]:
                color = surface.get_at((eye_x + offset, eyebrow_y))[:3]
                if color == (255, 255, 255):
                    white_pixels_in_brow_region += 1
        
        # Eyebrows should be completely hidden during SLEEPING
        assert white_pixels_in_brow_region == 0, \
            "Eyebrows should be hidden in SLEEPING expression"
    
    @pytest.mark.skip(reason="Waiting for Ekko's _draw_eyebrows implementation")
    def test_eyebrows_color_projection_compliant(self, pumpkin_surface):
        """All eyebrow pixels are (255,255,255), none are gray."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.draw(surface)
        
        # Sample entire eyebrow region
        center_x = 1920 // 2
        center_y = 1080 // 2
        left_eye_x = center_x - 100
        right_eye_x = center_x + 100
        eye_y = center_y - 50
        eyebrow_y = eye_y - 55
        
        # Check projection compliance: only pure white or pure black
        non_compliant_pixels = []
        for eye_x in [left_eye_x, right_eye_x]:
            for offset in range(-40, 41, 5):
                color = surface.get_at((eye_x + offset, eyebrow_y))[:3]
                # Must be either pure black or pure white
                if color not in [(0, 0, 0), (255, 255, 255)]:
                    non_compliant_pixels.append((eye_x + offset, eyebrow_y, color))
        
        assert len(non_compliant_pixels) == 0, \
            f"Eyebrows must be pure black/white for projection: {non_compliant_pixels}"
    
    @pytest.mark.skip(reason="Waiting for Ekko's _draw_eyebrows implementation")
    def test_raised_eyebrows_position(self, pumpkin_surface):
        """raise_eyebrows() then draw, verify brow pixels are higher than at offset=0."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Draw with neutral eyebrows (offset=0)
        pumpkin.set_eyebrow(0)
        pumpkin.draw(surface)
        
        # Find highest white pixel in left eyebrow region
        center_x = 1920 // 2
        left_eye_x = center_x - 100
        neutral_highest_y = None
        for y in range(400, 600):  # Scan eyebrow region
            if surface.get_at((left_eye_x, y))[:3] == (255, 255, 255):
                neutral_highest_y = y
                break
        
        # Draw with raised eyebrows
        surface.fill((0, 0, 0))  # Clear surface
        pumpkin.raise_eyebrows()
        pumpkin.raise_eyebrows()  # -20 offset
        pumpkin.draw(surface)
        
        # Find highest white pixel with raised eyebrows
        raised_highest_y = None
        for y in range(400, 600):
            if surface.get_at((left_eye_x, y))[:3] == (255, 255, 255):
                raised_highest_y = y
                break
        
        assert raised_highest_y is not None and neutral_highest_y is not None
        assert raised_highest_y < neutral_highest_y, \
            "Raised eyebrows should appear higher (lower Y coordinate)"
    
    @pytest.mark.skip(reason="Waiting for Ekko's _draw_eyebrows implementation")
    def test_expression_changes_brow_position(self, pumpkin_surface):
        """NEUTRAL vs SURPRISED, verify SURPRISED has higher brow pixels."""
        pumpkin, surface = pumpkin_surface
        
        # Draw NEUTRAL
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.set_eyebrow(0)
        pumpkin.draw(surface)
        
        center_x = 1920 // 2
        left_eye_x = center_x - 100
        neutral_highest_y = None
        for y in range(300, 700):
            if surface.get_at((left_eye_x, y))[:3] == (255, 255, 255):
                neutral_highest_y = y
                break
        
        # Draw SURPRISED
        surface.fill((0, 0, 0))
        pumpkin.set_expression(Expression.SURPRISED)
        pumpkin.draw(surface)
        
        surprised_highest_y = None
        for y in range(300, 700):
            if surface.get_at((left_eye_x, y))[:3] == (255, 255, 255):
                surprised_highest_y = y
                break
        
        # SURPRISED eyebrows should be higher (y_gap=-70 vs NEUTRAL y_gap=-55)
        assert surprised_highest_y is not None and neutral_highest_y is not None
        assert surprised_highest_y < neutral_highest_y, \
            "SURPRISED eyebrows should be higher than NEUTRAL"


class TestEyebrowAnimationIntegration:
    """Test eyebrow interaction with blink/wink animations."""
    
    @pytest.fixture
    def pumpkin_surface(self):
        """Create a PumpkinFace instance with test surface."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        surface = pygame.Surface((1920, 1080))
        yield face, surface
        pygame.quit()
    
    @pytest.mark.skip(reason="Waiting for Ekko's _draw_eyebrows implementation")
    def test_blink_lift_formula(self, pumpkin_surface):
        """At blink_progress=0.5, verify eyebrow pixels are higher than at rest."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.set_eyebrow(0)
        
        # Draw at rest
        pumpkin.draw(surface)
        center_x = 1920 // 2
        left_eye_x = center_x - 100
        rest_highest_y = None
        for y in range(400, 600):
            if surface.get_at((left_eye_x, y))[:3] == (255, 255, 255):
                rest_highest_y = y
                break
        
        # Simulate blink midpoint
        surface.fill((0, 0, 0))
        pumpkin.is_blinking = True
        pumpkin.blink_progress = 0.5
        pumpkin.draw(surface)
        
        blink_highest_y = None
        for y in range(400, 600):
            if surface.get_at((left_eye_x, y))[:3] == (255, 255, 255):
                blink_highest_y = y
                break
        
        # Blink lift should raise eyebrows: lift = 8 * sin(0.5 * pi) = 8
        assert blink_highest_y is not None and rest_highest_y is not None
        assert blink_highest_y < rest_highest_y, \
            "Blink should lift eyebrows (lower Y coordinate)"
    
    @pytest.mark.skip(reason="Waiting for Ekko's _draw_eyebrows implementation")
    def test_wink_left_lifts_left_brow_only(self, pumpkin_surface):
        """During left wink (eye_scale=0), left brow should be higher."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.set_eyebrow(0)
        
        # Simulate left wink at midpoint
        pumpkin.is_winking = True
        pumpkin.winking_eye = 'left'
        pumpkin.left_eye_scale = 0.0  # Fully closed
        pumpkin.right_eye_scale = 1.0
        pumpkin.draw(surface)
        
        center_x = 1920 // 2
        left_eye_x = center_x - 100
        right_eye_x = center_x + 100
        
        # Find highest eyebrow pixels
        left_highest_y = None
        right_highest_y = None
        for y in range(400, 600):
            if surface.get_at((left_eye_x, y))[:3] == (255, 255, 255):
                if left_highest_y is None:
                    left_highest_y = y
            if surface.get_at((right_eye_x, y))[:3] == (255, 255, 255):
                if right_highest_y is None:
                    right_highest_y = y
        
        # Left eyebrow should be lifted, right should not
        # This validates wink lift formula: lift = 8 * (1 - eye_scale)
        assert left_highest_y is not None and right_highest_y is not None
        assert left_highest_y < right_highest_y, \
            "Left eyebrow should be higher during left wink"
    
    def test_offset_preserved_after_blink(self, pumpkin_surface):
        """Set offset, run full blink cycle (40+ update() calls), offset unchanged."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_eyebrow(-25, 15)
        
        # Trigger blink
        pumpkin.blink()
        
        # Run full blink animation (40 updates at blink_speed=0.03)
        for _ in range(45):
            pumpkin.update()
        
        # Eyebrow offsets should be preserved
        assert pumpkin.eyebrow_left_offset == -25.0
        assert pumpkin.eyebrow_right_offset == 15.0
    
    def test_offset_preserved_after_wink(self, pumpkin_surface):
        """Set offset, run full wink cycle, offset unchanged."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_eyebrow(-30, 20)
        
        # Trigger left wink
        pumpkin.wink_left()
        
        # Run full wink animation
        for _ in range(45):
            pumpkin.update()
        
        # Eyebrow offsets should be preserved
        assert pumpkin.eyebrow_left_offset == -30.0
        assert pumpkin.eyebrow_right_offset == 20.0


class TestEyebrowEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def pumpkin_surface(self):
        """Create a PumpkinFace instance with test surface."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        surface = pygame.Surface((1920, 1080))
        yield face, surface
        pygame.quit()
    
    def test_max_raise_with_surprised(self, pumpkin_surface):
        """set_eyebrow(-50), set SURPRISED expression, draw → no crash."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_eyebrow(-50)
        pumpkin.set_expression(Expression.SURPRISED)
        
        # Should not crash
        try:
            pumpkin.draw(surface)
            success = True
        except Exception as e:
            success = False
            pytest.fail(f"Drawing with max raised eyebrows crashed: {e}")
        
        assert success
    
    def test_max_lower_no_overlap(self, pumpkin_surface):
        """set_eyebrow(50), draw → no crash, no overlap with eyes."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_eyebrow(50)
        
        # Should not crash
        try:
            pumpkin.draw(surface)
            success = True
        except Exception as e:
            success = False
            pytest.fail(f"Drawing with max lowered eyebrows crashed: {e}")
        
        assert success
    
    def test_sleeping_offset_preserved(self, pumpkin_surface):
        """Set offset, set SLEEPING, set NEUTRAL → offset still set."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_eyebrow(-35, 40)
        pumpkin.set_expression(Expression.SLEEPING)
        
        # Eyebrows hidden but state preserved
        assert pumpkin.eyebrow_left_offset == -35.0
        assert pumpkin.eyebrow_right_offset == 40.0
        
        # Return to NEUTRAL
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Offsets should still be set
        assert pumpkin.eyebrow_left_offset == -35.0
        assert pumpkin.eyebrow_right_offset == 40.0
    
    @pytest.mark.skip(reason="Waiting for Ekko's _draw_eyebrows implementation")
    def test_simultaneous_blink_and_high_brow(self, pumpkin_surface):
        """set_eyebrow(-50), trigger blink, no crash during animation."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_eyebrow(-50)
        pumpkin.blink()
        
        # Run through several frames of blink animation
        for i in range(20):
            try:
                pumpkin.update()
                pumpkin.draw(surface)
            except Exception as e:
                pytest.fail(f"Blink animation with max raised eyebrows crashed at frame {i}: {e}")
        
        # Should complete without crash
        assert True
