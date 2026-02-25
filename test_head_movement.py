"""
Test suite for 3D head movement illusion (Issue #17).

These tests validate the projection offset system that creates the illusion of
3D head movement by smoothly shifting the entire face rendering position.

Head movement directions: left, right, up, down
Mechanism: projection_offset_x and projection_offset_y shift all features
Constraints: [-500, +500] clamping, smooth animation, no visual discontinuities

Author: Mylo (Tester)
Date: 2026-02-22
"""

import pygame
import pytest
from pumpkin_face import PumpkinFace, Expression


class TestProjectionOffsetStateVariables:
    """Test projection offset state variable behavior and clamping."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    def test_default_offsets(self, pumpkin):
        """Projection offsets start at (0, 0) — center position."""
        assert pumpkin.projection_offset_x == 0
        assert pumpkin.projection_offset_y == 0
    
    def test_jog_offset_positive(self, pumpkin):
        """jog_projection(50, 30) moves right and down."""
        pumpkin.jog_projection(50, 30)
        assert pumpkin.projection_offset_x == 50
        assert pumpkin.projection_offset_y == 30
    
    def test_jog_offset_negative(self, pumpkin):
        """jog_projection(-40, -25) moves left and up."""
        pumpkin.jog_projection(-40, -25)
        assert pumpkin.projection_offset_x == -40
        assert pumpkin.projection_offset_y == -25
    
    def test_jog_offset_cumulative(self, pumpkin):
        """Multiple jog calls accumulate: (10, 5) + (20, -10) = (30, -5)."""
        pumpkin.jog_projection(10, 5)
        pumpkin.jog_projection(20, -10)
        assert pumpkin.projection_offset_x == 30
        assert pumpkin.projection_offset_y == -5
    
    def test_set_projection_offset_absolute(self, pumpkin):
        """set_projection_offset(100, -50) sets absolute position."""
        pumpkin.jog_projection(30, 20)  # Set initial offset
        pumpkin.set_projection_offset(100, -50)  # Override with absolute
        assert pumpkin.projection_offset_x == 100
        assert pumpkin.projection_offset_y == -50
    
    def test_clamp_upper_limit_x(self, pumpkin):
        """set_projection_offset(600, 0) clamps X to 500."""
        pumpkin.set_projection_offset(600, 0)
        assert pumpkin.projection_offset_x == 500
    
    def test_clamp_lower_limit_x(self, pumpkin):
        """set_projection_offset(-700, 0) clamps X to -500."""
        pumpkin.set_projection_offset(-700, 0)
        assert pumpkin.projection_offset_x == -500
    
    def test_clamp_upper_limit_y(self, pumpkin):
        """set_projection_offset(0, 800) clamps Y to 500."""
        pumpkin.set_projection_offset(0, 800)
        assert pumpkin.projection_offset_y == 500
    
    def test_clamp_lower_limit_y(self, pumpkin):
        """set_projection_offset(0, -900) clamps Y to -500."""
        pumpkin.set_projection_offset(0, -900)
        assert pumpkin.projection_offset_y == -500
    
    def test_jog_respects_clamping(self, pumpkin):
        """jog past boundary stays at limit: 400 + 200 → 500 (not 600)."""
        pumpkin.set_projection_offset(400, 0)
        pumpkin.jog_projection(200, 0)
        assert pumpkin.projection_offset_x == 500
    
    def test_reset_projection_offset(self, pumpkin):
        """reset_projection_offset() returns to (0, 0)."""
        pumpkin.set_projection_offset(150, -75)
        pumpkin.reset_projection_offset()
        assert pumpkin.projection_offset_x == 0
        assert pumpkin.projection_offset_y == 0


class TestHeadMovementDirections:
    """Test head movement in all four cardinal directions."""
    
    @pytest.fixture
    def pumpkin_surface(self):
        """Create a PumpkinFace instance with test surface."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        surface = pygame.Surface((1920, 1080))
        yield face, surface
        pygame.quit()
    
    def test_move_left(self, pumpkin_surface):
        """Moving left (negative X) shifts all features left."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Draw at center
        pumpkin.draw(surface)
        center_x = 1920 // 2
        center_y = 1080 // 2
        left_eye_x_center = center_x - 100
        left_eye_y_center = center_y - 50  # Eyes are 50px above center in neutral
        
        # Sample left eye center position
        color_center = surface.get_at((left_eye_x_center, left_eye_y_center))[:3]
        
        # Move left 100px
        surface.fill((0, 0, 0))
        pumpkin.jog_projection(-100, 0)
        pumpkin.draw(surface)
        
        # Left eye should now be 100px further left
        color_shifted = surface.get_at((left_eye_x_center - 100, left_eye_y_center))[:3]
        color_old_position = surface.get_at((left_eye_x_center, left_eye_y_center))[:3]
        
        # Feature moved: white at new position, black at old position
        assert color_shifted == (255, 255, 255), "Feature should move left"
        assert color_old_position == (0, 0, 0), "Old position should be black"
    
    def test_move_right(self, pumpkin_surface):
        """Moving right (positive X) shifts all features right."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Draw at center
        pumpkin.draw(surface)
        center_x = 1920 // 2
        center_y = 1080 // 2
        right_eye_x_center = center_x + 100
        right_eye_y_center = center_y - 50  # Eyes are 50px above center in neutral
        
        # Move right 100px
        surface.fill((0, 0, 0))
        pumpkin.jog_projection(100, 0)
        pumpkin.draw(surface)
        
        # Right eye should now be 100px further right
        color_shifted = surface.get_at((right_eye_x_center + 100, right_eye_y_center))[:3]
        color_old_position = surface.get_at((right_eye_x_center, right_eye_y_center))[:3]
        
        # Feature moved: white at new position, black at old position
        assert color_shifted == (255, 255, 255), "Feature should move right"
        assert color_old_position == (0, 0, 0), "Old position should be black"
    
    def test_move_up(self, pumpkin_surface):
        """Moving up (negative Y) shifts all features up."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Draw at center
        pumpkin.draw(surface)
        center_x = 1920 // 2
        center_y = 1080 // 2
        eye_x_center = center_x - 100  # Left eye
        eye_y_center = center_y - 50  # Eyes are 50px above center in neutral
        
        # Move up 80px
        surface.fill((0, 0, 0))
        pumpkin.jog_projection(0, -80)
        pumpkin.draw(surface)
        
        # Eyes should now be 80px higher (lower Y coordinate)
        color_shifted = surface.get_at((eye_x_center, eye_y_center - 80))[:3]
        color_old_position = surface.get_at((eye_x_center, eye_y_center))[:3]
        
        # Feature moved: white at new position, black at old position
        assert color_shifted == (255, 255, 255), "Feature should move up"
        assert color_old_position == (0, 0, 0), "Old position should be black"
    
    def test_move_down(self, pumpkin_surface):
        """Moving down (positive Y) shifts all features down."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Draw at center
        pumpkin.draw(surface)
        center_y = 1080 // 2
        mouth_y_center = center_y + 80
        
        # Move down 60px
        surface.fill((0, 0, 0))
        pumpkin.jog_projection(0, 60)
        pumpkin.draw(surface)
        
        # Mouth should now be 60px lower (higher Y coordinate)
        color_shifted = surface.get_at((960, mouth_y_center + 60))[:3]
        color_old_position = surface.get_at((960, mouth_y_center))[:3]
        
        # Feature moved: white at new position, black at old position
        assert color_shifted == (255, 255, 255), "Feature should move down"
        assert color_old_position == (0, 0, 0), "Old position should be black"
    
    def test_diagonal_movement(self, pumpkin_surface):
        """Moving diagonally (e.g., up-right) combines X and Y offsets."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Draw at center
        pumpkin.draw(surface)
        
        # Move up-right (negative Y, positive X)
        surface.fill((0, 0, 0))
        pumpkin.jog_projection(80, -60)
        pumpkin.draw(surface)
        
        # Sample left eye after diagonal offset
        # Eyes are at center_x ± 100, center_y - 50
        center_x = (1920 // 2) + 80  # After X offset
        center_y = (1080 // 2) - 60  # After Y offset
        left_eye_x = center_x - 100
        left_eye_y = center_y - 50
        color_shifted = surface.get_at((left_eye_x, left_eye_y))[:3]
        
        # Feature should exist at new diagonal position
        assert color_shifted == (255, 255, 255), "Feature should move diagonally"


class TestHeadMovementOrthogonality:
    """Test that projection offset is independent of expression state."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    def test_expression_change_preserves_offset(self, pumpkin):
        """Set offset, change expression, offset unchanged."""
        pumpkin.set_projection_offset(100, -50)
        pumpkin.set_expression(Expression.HAPPY)
        assert pumpkin.projection_offset_x == 100
        assert pumpkin.projection_offset_y == -50
    
    @pytest.mark.parametrize("expression", [
        Expression.NEUTRAL,
        Expression.HAPPY,
        Expression.SAD,
        Expression.ANGRY,
        Expression.SURPRISED,
        Expression.SCARED,
        Expression.SLEEPING
    ])
    def test_all_expressions_preserve_offset(self, pumpkin, expression):
        """Parametrized: all 7 expressions preserve projection offset."""
        pumpkin.set_projection_offset(-150, 75)
        pumpkin.set_expression(expression)
        assert pumpkin.projection_offset_x == -150
        assert pumpkin.projection_offset_y == 75
    
    def test_offset_during_expression_transition(self, pumpkin):
        """Set offset while transition_progress < 1.0, offset is set."""
        pumpkin.set_expression(Expression.HAPPY)
        pumpkin.transition_progress = 0.5  # Mid-transition
        pumpkin.set_projection_offset(80, -40)
        assert pumpkin.projection_offset_x == 80
        assert pumpkin.projection_offset_y == -40
    
    def test_blink_preserves_offset(self, pumpkin):
        """Trigger blink, run animation, offset unchanged."""
        pumpkin.set_projection_offset(50, 25)
        pumpkin.blink()
        
        # Run full blink animation
        for _ in range(45):
            pumpkin.update()
        
        assert pumpkin.projection_offset_x == 50
        assert pumpkin.projection_offset_y == 25
    
    def test_gaze_preserves_offset(self, pumpkin):
        """Change gaze direction, offset unchanged."""
        pumpkin.set_projection_offset(-70, 90)
        pumpkin.gaze(45, -30)
        assert pumpkin.projection_offset_x == -70
        assert pumpkin.projection_offset_y == 90
    
    def test_eyebrow_preserves_offset(self, pumpkin):
        """Raise eyebrows, offset unchanged."""
        pumpkin.set_projection_offset(120, -80)
        pumpkin.raise_eyebrows()
        assert pumpkin.projection_offset_x == 120
        assert pumpkin.projection_offset_y == -80


class TestHeadMovementTransitionSmoothness:
    """Test that head movement transitions are smooth without discontinuities."""
    
    @pytest.fixture
    def pumpkin_surface(self):
        """Create a PumpkinFace instance with test surface."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        surface = pygame.Surface((1920, 1080))
        yield face, surface
        pygame.quit()
    
    def test_no_visual_jump_on_offset_change(self, pumpkin_surface):
        """Changing offset doesn't cause visual discontinuities."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Draw with offset=0
        pumpkin.draw(surface)
        
        # Change offset immediately (no animation system currently)
        pumpkin.set_projection_offset(100, 50)
        pumpkin.draw(surface)
        
        # Validate features exist at new position (no crash, no garbage pixels)
        center_x = (1920 // 2) + 100
        center_y = (1080 // 2) + 50
        
        # Sample near face center — should find white features
        white_pixels = 0
        for dx in range(-200, 201, 20):
            for dy in range(-200, 201, 20):
                color = surface.get_at((center_x + dx, center_y + dy))[:3]
                if color == (255, 255, 255):
                    white_pixels += 1
        
        assert white_pixels > 0, "Features should render at offset position"
    
    def test_multiple_small_jogs_stable(self, pumpkin_surface):
        """Multiple small jog_offset calls produce stable rendering."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Perform 10 small jogs (simulating smooth animation)
        for _ in range(10):
            pumpkin.jog_projection(5, 3)
            pumpkin.draw(surface)
            surface.fill((0, 0, 0))  # Clear for next frame
        
        # Final position: 10 * (5, 3) = (50, 30)
        assert pumpkin.projection_offset_x == 50
        assert pumpkin.projection_offset_y == 30
        
        # Final draw should be stable (no crash)
        pumpkin.draw(surface)
        
        # Features should exist at final position
        center_x = (1920 // 2) + 50
        center_y = (1080 // 2) + 30
        color_at_center = surface.get_at((center_x, center_y - 50))[:3]
        
        # Eye region should have white features
        assert color_at_center == (255, 255, 255) or \
               surface.get_at((center_x - 100, center_y - 50))[:3] == (255, 255, 255), \
               "Features should render stably after multiple jogs"
    
    def test_rapid_direction_changes(self, pumpkin_surface):
        """Rapid direction changes (left→right→up→down) don't crash."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Rapid direction changes
        pumpkin.jog_projection(-50, 0)   # Left
        pumpkin.draw(surface)
        
        pumpkin.jog_projection(100, 0)   # Right (net +50)
        pumpkin.draw(surface)
        
        pumpkin.jog_projection(0, -40)   # Up
        pumpkin.draw(surface)
        
        pumpkin.jog_projection(0, 80)    # Down (net +40)
        pumpkin.draw(surface)
        
        # Final position: (50, 40)
        assert pumpkin.projection_offset_x == 50
        assert pumpkin.projection_offset_y == 40
        
        # Should not crash, features render correctly
        center_x = (1920 // 2) + 50
        center_y = (1080 // 2) + 40
        white_pixels = sum(
            1 for dx in range(-150, 151, 20) for dy in range(-150, 151, 20)
            if surface.get_at((center_x + dx, center_y + dy))[:3] == (255, 255, 255)
        )
        assert white_pixels > 0, "Features should render after rapid changes"


class TestHeadMovementProjectionMapping:
    """Test that projection offset maintains projection mapping compliance."""
    
    @pytest.fixture
    def pumpkin_surface(self):
        """Create a PumpkinFace instance with test surface."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        surface = pygame.Surface((1920, 1080))
        yield face, surface
        pygame.quit()
    
    def test_projection_colors_at_offset(self, pumpkin_surface):
        """With projection offset, features remain pure white on pure black."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.set_projection_offset(150, -100)
        pumpkin.draw(surface)
        
        # Sample across entire canvas
        non_compliant_pixels = []
        for x in range(0, 1920, 50):
            for y in range(0, 1080, 50):
                color = surface.get_at((x, y))[:3]
                if color not in [(0, 0, 0), (255, 255, 255)]:
                    non_compliant_pixels.append((x, y, color))
        
        assert len(non_compliant_pixels) == 0, \
            f"Only pure black/white allowed: {non_compliant_pixels[:10]}"
    
    def test_contrast_ratio_at_offset(self, pumpkin_surface):
        """Contrast ratio remains ≥15:1 with projection offset."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.HAPPY)
        pumpkin.set_projection_offset(-80, 60)
        pumpkin.draw(surface)
        
        # Sample background and feature colors
        bg_color = surface.get_at((100, 100))[:3]
        
        # Find a white feature pixel at offset position
        center_x = (1920 // 2) - 80
        center_y = (1080 // 2) + 60
        feature_color = None
        for dx in range(-150, 151, 10):
            for dy in range(-150, 151, 10):
                color = surface.get_at((center_x + dx, center_y + dy))[:3]
                if color == (255, 255, 255):
                    feature_color = color
                    break
            if feature_color:
                break
        
        assert bg_color == (0, 0, 0), "Background should be pure black"
        assert feature_color == (255, 255, 255), "Features should be pure white"
        
        # Calculate contrast ratio
        def luminance(rgb):
            r, g, b = [x / 255.0 for x in rgb]
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        lum_bg = luminance(bg_color)
        lum_feature = luminance(feature_color)
        contrast = (max(lum_bg, lum_feature) + 0.05) / (min(lum_bg, lum_feature) + 0.05)
        
        assert contrast >= 15.0, f"Contrast ratio {contrast:.1f} < 15.0"
    
    def test_all_expressions_at_offset(self, pumpkin_surface):
        """All expressions maintain projection compliance at offset."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_projection_offset(200, -150)
        
        for expression in [Expression.NEUTRAL, Expression.HAPPY, Expression.SAD,
                          Expression.ANGRY, Expression.SURPRISED, Expression.SCARED]:
            surface.fill((0, 0, 0))
            pumpkin.current_expression = expression
            pumpkin.target_expression = expression
            pumpkin.transition_progress = 1.0
            pumpkin.draw(surface)
            
            # Sparse sampling: check for binary colors only
            non_compliant = []
            for x in range(0, 1920, 80):
                for y in range(0, 1080, 80):
                    color = surface.get_at((x, y))[:3]
                    if color not in [(0, 0, 0), (255, 255, 255)]:
                        non_compliant.append((x, y, color))
            
            assert len(non_compliant) == 0, \
                f"{expression.value} has non-compliant pixels at offset: {non_compliant[:5]}"


class TestHeadMovementEdgeCases:
    """Test edge cases and boundary conditions for projection offset."""
    
    @pytest.fixture
    def pumpkin_surface(self):
        """Create a PumpkinFace instance with test surface."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        surface = pygame.Surface((1920, 1080))
        yield face, surface
        pygame.quit()
    
    def test_extreme_left_position(self, pumpkin_surface):
        """set_projection_offset(-500, 0) draws correctly (features may be clipped)."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.set_projection_offset(-500, 0)
        
        # Should not crash
        try:
            pumpkin.draw(surface)
            success = True
        except Exception as e:
            success = False
            pytest.fail(f"Drawing at extreme left crashed: {e}")
        
        assert success
    
    def test_extreme_right_position(self, pumpkin_surface):
        """set_projection_offset(500, 0) draws correctly (features may be clipped)."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.set_projection_offset(500, 0)
        
        # Should not crash
        try:
            pumpkin.draw(surface)
            success = True
        except Exception as e:
            success = False
            pytest.fail(f"Drawing at extreme right crashed: {e}")
        
        assert success
    
    def test_extreme_up_position(self, pumpkin_surface):
        """set_projection_offset(0, -500) draws correctly (features may be clipped)."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.set_projection_offset(0, -500)
        
        # Should not crash
        try:
            pumpkin.draw(surface)
            success = True
        except Exception as e:
            success = False
            pytest.fail(f"Drawing at extreme up crashed: {e}")
        
        assert success
    
    def test_extreme_down_position(self, pumpkin_surface):
        """set_projection_offset(0, 500) draws correctly (features may be clipped)."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.set_projection_offset(0, 500)
        
        # Should not crash
        try:
            pumpkin.draw(surface)
            success = True
        except Exception as e:
            success = False
            pytest.fail(f"Drawing at extreme down crashed: {e}")
        
        assert success
    
    def test_extreme_corner_position(self, pumpkin_surface):
        """set_projection_offset(-500, -500) draws correctly."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.set_projection_offset(-500, -500)
        
        # Should not crash
        try:
            pumpkin.draw(surface)
            success = True
        except Exception as e:
            success = False
            pytest.fail(f"Drawing at extreme corner crashed: {e}")
        
        assert success
    
    def test_zero_offset_default_behavior(self, pumpkin_surface):
        """Offset (0, 0) renders identically to no offset set."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Draw with default (0, 0)
        pumpkin.draw(surface)
        pixels_default = [surface.get_at((x, y))[:3] 
                         for x in range(0, 1920, 100) 
                         for y in range(0, 1080, 100)]
        
        # Explicitly set (0, 0) and redraw
        surface.fill((0, 0, 0))
        pumpkin.set_projection_offset(0, 0)
        pumpkin.draw(surface)
        pixels_explicit = [surface.get_at((x, y))[:3] 
                          for x in range(0, 1920, 100) 
                          for y in range(0, 1080, 100)]
        
        assert pixels_default == pixels_explicit, "Offset (0,0) should match default"
    
    def test_combined_extreme_eyebrow_and_offset(self, pumpkin_surface):
        """Max raised eyebrows + max offset doesn't crash."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_eyebrow(-50)  # Max raise
        pumpkin.set_projection_offset(500, -500)  # Max offset
        
        try:
            pumpkin.draw(surface)
            success = True
        except Exception as e:
            success = False
            pytest.fail(f"Combined extreme states crashed: {e}")
        
        assert success
    
    def test_rapid_reset_cycles(self, pumpkin_surface):
        """Repeated offset→reset cycles remain stable."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        for _ in range(10):
            pumpkin.set_projection_offset(100, -50)
            pumpkin.draw(surface)
            pumpkin.reset_projection_offset()
            pumpkin.draw(surface)
        
        # Should end at (0, 0)
        assert pumpkin.projection_offset_x == 0
        assert pumpkin.projection_offset_y == 0


class TestHeadMovementPerformance:
    """Test performance characteristics of projection offset rendering."""
    
    @pytest.fixture
    def pumpkin_surface(self):
        """Create a PumpkinFace instance with test surface."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        surface = pygame.Surface((1920, 1080))
        yield face, surface
        pygame.quit()
    
    def test_offset_rendering_performance(self, pumpkin_surface):
        """Rendering with offset completes in reasonable time (< 50ms per frame)."""
        import time
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.set_projection_offset(200, -100)
        
        # Measure 10 draws
        start_time = time.time()
        for _ in range(10):
            surface.fill((0, 0, 0))
            pumpkin.draw(surface)
        elapsed_time = time.time() - start_time
        
        avg_frame_time = elapsed_time / 10
        assert avg_frame_time < 0.05, \
            f"Avg frame time {avg_frame_time*1000:.1f}ms exceeds 50ms target"
    
    def test_frequent_offset_updates_stable(self, pumpkin_surface):
        """60 consecutive jog_offset calls (simulating 1 second at 60fps) remain stable."""
        pumpkin, surface = pumpkin_surface
        pumpkin.set_expression(Expression.NEUTRAL)
        
        # Simulate 60fps animation for 1 second
        for i in range(60):
            dx = 2 if i % 2 == 0 else -2  # Oscillate left-right
            pumpkin.jog_projection(dx, 0)
            pumpkin.draw(surface)
            surface.fill((0, 0, 0))
        
        # Should not crash, offset should be reasonable (accumulated small values)
        assert -100 <= pumpkin.projection_offset_x <= 100, \
            "Offset should stay bounded during animation"
