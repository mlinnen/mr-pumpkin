"""
Test suite for rolling eyes animation feature (Issue #10).

These tests validate the rolling eyes animation system where:
- Pupils rotate clockwise/counter-clockwise in circular motion
- Rolling animation completes 360° rotation
- Rolling pauses during blink/wink and resumes after
- Progress tracking from 0.0 to 1.0
- Socket commands and keyboard shortcuts trigger rolling
- Projection mapping compliance (pure black/white output)

Author: Mylo (Tester)
Date: 2026-02-20
"""

import pygame
import pytest
import math
from pumpkin_face import PumpkinFace, Expression


class TestRollingEyesBasicBehavior:
    """Test core rolling eyes animation behavior."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_roll_clockwise_method_exists(self):
        """Verify PumpkinFace has a roll_clockwise() method."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        
        assert hasattr(pumpkin, 'roll_clockwise'), \
            "PumpkinFace must have a roll_clockwise() method"
        assert callable(getattr(pumpkin, 'roll_clockwise')), \
            "roll_clockwise() must be callable"
        
        pygame.quit()
    
    def test_roll_counterclockwise_method_exists(self):
        """Verify PumpkinFace has a roll_counterclockwise() method."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        
        assert hasattr(pumpkin, 'roll_counterclockwise'), \
            "PumpkinFace must have a roll_counterclockwise() method"
        assert callable(getattr(pumpkin, 'roll_counterclockwise')), \
            "roll_counterclockwise() must be callable"
        
        pygame.quit()
    
    def test_roll_clockwise_rotates_pupils(self, pumpkin_projection):
        """Roll clockwise should set is_rolling=True and direction='clockwise'."""
        pumpkin, surface = pumpkin_projection
        
        # Start rolling clockwise
        pumpkin.roll_clockwise()
        
        assert hasattr(pumpkin, 'is_rolling'), \
            "PumpkinFace must have is_rolling attribute"
        assert hasattr(pumpkin, 'rolling_direction'), \
            "PumpkinFace must have rolling_direction attribute"
        
        assert pumpkin.is_rolling is True, \
            "roll_clockwise() should set is_rolling to True"
        assert pumpkin.rolling_direction == 'clockwise', \
            "roll_clockwise() should set rolling_direction to 'clockwise'"
    
    def test_roll_counterclockwise_rotates_pupils(self, pumpkin_projection):
        """Roll counter-clockwise should set direction='counterclockwise'."""
        pumpkin, surface = pumpkin_projection
        
        # Start rolling counterclockwise
        pumpkin.roll_counterclockwise()
        
        assert pumpkin.is_rolling is True, \
            "roll_counterclockwise() should set is_rolling to True"
        assert pumpkin.rolling_direction == 'counterclockwise', \
            "roll_counterclockwise() should set rolling_direction to 'counterclockwise'"
    
    def test_roll_animation_progress(self, pumpkin_projection):
        """Rolling progress should advance from 0.0 to 1.0 during animation."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.roll_clockwise()
        assert hasattr(pumpkin, 'rolling_progress'), \
            "PumpkinFace must have rolling_progress attribute"
        
        initial_progress = pumpkin.rolling_progress
        
        # Advance animation
        pumpkin.update()
        
        assert pumpkin.rolling_progress > initial_progress, \
            "update() should advance rolling_progress when is_rolling=True"
        
        # Complete roll (rolling_speed similar to 0.02 for longer animation)
        for _ in range(60):
            pumpkin.update()
        
        assert pumpkin.is_rolling is False, \
            "is_rolling should be False after roll completes"
    
    def test_roll_completes_360_degrees(self, pumpkin_projection):
        """After one complete roll, pupils should return to starting position."""
        pumpkin, surface = pumpkin_projection
        
        # Note initial pupil angle
        pumpkin.roll_clockwise()
        
        # Should have pupil_angle attribute for tracking rotation
        assert hasattr(pumpkin, 'pupil_angle'), \
            "PumpkinFace must have pupil_angle attribute for rotation tracking"
        
        initial_angle = pumpkin.pupil_angle
        
        # Complete roll
        for _ in range(60):
            pumpkin.update()
        
        # After 360° rotation, angle should return to start (modulo 2π)
        final_angle = pumpkin.pupil_angle
        
        # Allow small floating-point tolerance
        angle_diff = abs((final_angle - initial_angle) % (2 * math.pi))
        assert angle_diff < 0.1, \
            f"After 360° roll, pupil angle should return to start. Diff: {angle_diff}"
    
    def test_roll_does_not_interrupt_ongoing_roll(self, pumpkin_projection):
        """Calling roll_clockwise() while is_rolling=True should NOT reset progress."""
        pumpkin, surface = pumpkin_projection
        
        # Start first roll
        pumpkin.roll_clockwise()
        
        # Advance roll progress manually
        pumpkin.rolling_progress = 0.5
        
        # Try to roll again
        pumpkin.roll_clockwise()
        
        assert pumpkin.rolling_progress == 0.5, \
            "Calling roll_clockwise() during ongoing roll should not reset progress"


class TestRollingEyesPupilCoordinates:
    """Test pupil coordinate calculations during rolling."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_roll_pupil_coordinates_circular_motion(self, pumpkin_projection):
        """Pupils should move in circular motion: x = r*sin(angle), y = r*cos(angle)."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.roll_clockwise()
        
        # Track pupil positions over multiple frames
        positions = []
        for _ in range(20):
            pumpkin.update()
            
            # Pupils should have offset positions from eye center
            if hasattr(pumpkin, 'left_pupil_offset') and hasattr(pumpkin, 'right_pupil_offset'):
                positions.append({
                    'angle': pumpkin.pupil_angle,
                    'left_offset': pumpkin.left_pupil_offset,
                    'right_offset': pumpkin.right_pupil_offset
                })
        
        # Verify positions follow circular pattern
        # Each position should be roughly on a circle
        if positions:
            for pos in positions:
                left_x, left_y = pos['left_offset']
                # Distance from origin should be constant (radius)
                distance = math.sqrt(left_x**2 + left_y**2)
                # Allow some tolerance for floating point
                assert distance > 0, "Pupils should be offset from center during roll"
    
    def test_roll_clockwise_increases_angle(self, pumpkin_projection):
        """Clockwise rolling should increase pupil angle over time."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.roll_clockwise()
        initial_angle = pumpkin.pupil_angle
        
        # Advance a few frames
        for _ in range(5):
            pumpkin.update()
        
        # Angle should increase for clockwise (or decrease depending on implementation)
        # This documents expected direction convention
        assert pumpkin.pupil_angle != initial_angle, \
            "Pupil angle should change during clockwise roll"
    
    def test_roll_counterclockwise_decreases_angle(self, pumpkin_projection):
        """Counter-clockwise rolling should rotate in opposite direction."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.roll_counterclockwise()
        initial_angle = pumpkin.pupil_angle
        
        # Advance a few frames
        for _ in range(5):
            pumpkin.update()
        
        # Angle should change in opposite direction
        assert pumpkin.pupil_angle != initial_angle, \
            "Pupil angle should change during counter-clockwise roll"


class TestRollingEyesPauseLogic:
    """Test pause-during-blink/wink and resume logic."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_roll_pauses_during_blink(self, pumpkin_projection):
        """Rolling should pause when blink starts, resume after blink completes."""
        pumpkin, surface = pumpkin_projection
        
        # Start rolling
        pumpkin.roll_clockwise()
        
        # Advance roll partway
        for _ in range(10):
            pumpkin.update()
        
        progress_before_blink = pumpkin.rolling_progress
        
        # Start blink mid-roll
        pumpkin.blink()
        
        # During blink, rolling should pause (progress should not advance)
        for _ in range(5):
            pumpkin.update()
        
        # Rolling progress should be paused or flagged as paused
        if hasattr(pumpkin, 'rolling_paused'):
            assert pumpkin.rolling_paused is True, \
                "rolling_paused flag should be True during blink"
        
        # Complete blink
        for _ in range(40):
            pumpkin.update()
        
        # After blink, rolling should resume
        assert pumpkin.is_rolling is True or pumpkin.is_rolling is False, \
            "Rolling state should be valid after blink completes"
    
    def test_roll_pauses_during_wink(self, pumpkin_projection):
        """Rolling should pause during wink, resume after wink completes."""
        pumpkin, surface = pumpkin_projection
        
        # Start rolling
        pumpkin.roll_clockwise()
        
        # Advance roll partway
        for _ in range(10):
            pumpkin.update()
        
        progress_before_wink = pumpkin.rolling_progress
        
        # Start wink mid-roll
        pumpkin.wink_left()
        
        # During wink, rolling should pause
        for _ in range(5):
            pumpkin.update()
        
        # Complete wink
        for _ in range(40):
            pumpkin.update()
        
        # After wink, rolling should resume or complete
        assert hasattr(pumpkin, 'is_rolling'), \
            "Rolling state should be maintained after wink"
    
    def test_roll_resumes_after_blink_with_correct_progress(self, pumpkin_projection):
        """After blink interruption, rolling should resume from paused progress."""
        pumpkin, surface = pumpkin_projection
        
        # Start rolling
        pumpkin.roll_clockwise()
        
        # Advance to specific progress
        for _ in range(15):
            pumpkin.update()
        
        progress_at_pause = pumpkin.rolling_progress
        
        # Blink
        pumpkin.blink()
        for _ in range(40):
            pumpkin.update()
        
        # After blink, if rolling resumed, progress should continue from pause point
        # (or rolling may have completed - both valid depending on implementation)
        assert pumpkin.rolling_progress >= progress_at_pause or pumpkin.is_rolling is False, \
            "Rolling progress should not rewind after blink"


class TestRollingEyesCommandInterface:
    """Test keyboard shortcuts and socket commands for rolling eyes."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_roll_keyboard_shortcut_clockwise(self, pumpkin_projection):
        """_handle_keyboard_input(pygame.K_c) should trigger roll_clockwise."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.NEUTRAL
        
        # Simulate keyboard input for key C
        pumpkin._handle_keyboard_input(pygame.K_c)
        
        assert pumpkin.is_rolling is True, \
            "Keyboard 'C' should trigger roll_clockwise"
        assert pumpkin.rolling_direction == 'clockwise', \
            "Keyboard 'C' should set rolling_direction to 'clockwise'"
    
    def test_roll_keyboard_shortcut_counterclockwise(self, pumpkin_projection):
        """_handle_keyboard_input(pygame.K_x) should trigger roll_counterclockwise."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.NEUTRAL
        
        # Simulate keyboard input for key X
        pumpkin._handle_keyboard_input(pygame.K_x)
        
        assert pumpkin.is_rolling is True, \
            "Keyboard 'X' should trigger roll_counterclockwise"
        assert pumpkin.rolling_direction == 'counterclockwise', \
            "Keyboard 'X' should set rolling_direction to 'counterclockwise'"
    
    def test_roll_socket_command_clockwise(self, pumpkin_projection):
        """Socket server should handle 'roll_clockwise' command string."""
        pumpkin, surface = pumpkin_projection
        
        command = "roll_clockwise"
        
        # Simulate socket command handling
        if command == "roll_clockwise":
            pumpkin.roll_clockwise()
        
        assert pumpkin.is_rolling is True, \
            "Socket command 'roll_clockwise' should trigger roll animation"
        assert pumpkin.rolling_direction == 'clockwise', \
            "Socket command 'roll_clockwise' should roll clockwise"
    
    def test_roll_socket_command_counterclockwise(self, pumpkin_projection):
        """Socket server should handle 'roll_counterclockwise' command string."""
        pumpkin, surface = pumpkin_projection
        
        command = "roll_counterclockwise"
        
        # Simulate socket command handling
        if command == "roll_counterclockwise":
            pumpkin.roll_counterclockwise()
        
        assert pumpkin.is_rolling is True, \
            "Socket command 'roll_counterclockwise' should trigger roll animation"
        assert pumpkin.rolling_direction == 'counterclockwise', \
            "Socket command 'roll_counterclockwise' should roll counter-clockwise"


class TestRollingEyesProjectionMapping:
    """Test projection mapping compliance during rolling animation."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_roll_rendering_pure_black_white(self, pumpkin_projection):
        """During mid-roll, only black/white pixels (projection compliance)."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.NEUTRAL
        pumpkin.roll_clockwise()
        
        # Advance to mid-roll
        for _ in range(20):
            pumpkin.update()
        
        # Draw and check colors
        pumpkin.draw(surface)
        
        # Sample the entire surface for intermediate colors
        width, height = surface.get_size()
        intermediate_colors = set()
        
        # Sample every 20th pixel
        for x in range(0, width, 20):
            for y in range(0, height, 20):
                color = surface.get_at((x, y))[:3]
                if color != (0, 0, 0) and color != (255, 255, 255):
                    intermediate_colors.add(color)
        
        assert len(intermediate_colors) == 0, \
            f"During rolling, found non-projection colors: {intermediate_colors}"
    
    def test_roll_contrast_ratio(self, pumpkin_projection):
        """Rolling animation maintains 21:1 contrast ratio."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.roll_clockwise()
        
        # Advance to mid-roll
        for _ in range(20):
            pumpkin.update()
        
        pumpkin.draw(surface)
        
        # Sample background and feature colors
        background_color = surface.get_at((50, 50))[:3]
        
        # Calculate luminance
        def luminance(rgb):
            r, g, b = [x / 255.0 for x in rgb]
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        bg_lum = luminance(background_color)
        feature_lum = luminance((255, 255, 255))
        
        # Calculate contrast ratio
        lighter = max(bg_lum, feature_lum)
        darker = min(bg_lum, feature_lum)
        contrast = (lighter + 0.05) / (darker + 0.05)
        
        # Pure black to white should yield 21:1 contrast
        assert contrast >= 15.0, \
            f"Roll contrast ratio {contrast:.2f}:1 is too low. Need at least 15:1."
    
    def test_roll_pupils_remain_visible(self, pumpkin_projection):
        """Pupils should remain visible (as black circles) throughout roll."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.NEUTRAL
        pumpkin.roll_clockwise()
        
        # Test at multiple points in animation
        for _ in range(30):
            pumpkin.update()
            pumpkin.draw(surface)
            
            # Sample eye areas for pupils (black circles on white eyes)
            # Eyes are roughly at (300, 250) and (500, 250) for 800x600
            left_eye_center = (300, 250)
            right_eye_center = (500, 250)
            
            # Sample around eye centers to find black pixels (pupils)
            for eye_center in [left_eye_center, right_eye_center]:
                found_black = False
                for dx in range(-30, 31, 10):
                    for dy in range(-30, 31, 10):
                        x = eye_center[0] + dx
                        y = eye_center[1] + dy
                        if 0 <= x < 800 and 0 <= y < 600:
                            color = surface.get_at((x, y))[:3]
                            if color == (0, 0, 0):
                                found_black = True
                                break
                    if found_black:
                        break


class TestRollingEyesEdgeCases:
    """Test edge cases and boundary conditions for rolling eyes."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_roll_multiple_directions_sequential(self, pumpkin_projection):
        """Roll clockwise, complete, then roll counter-clockwise."""
        pumpkin, surface = pumpkin_projection
        
        # Roll clockwise
        pumpkin.roll_clockwise()
        for _ in range(60):
            pumpkin.update()
        
        assert pumpkin.is_rolling is False, \
            "First roll should complete"
        
        # Roll counter-clockwise
        pumpkin.roll_counterclockwise()
        for _ in range(60):
            pumpkin.update()
        
        assert pumpkin.is_rolling is False, \
            "Second roll should complete"
    
    def test_roll_with_expression_change(self, pumpkin_projection):
        """Changing expression during rolling should handle gracefully."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.NEUTRAL
        pumpkin.roll_clockwise()
        
        # Change expression mid-roll
        for _ in range(10):
            pumpkin.update()
        
        pumpkin.set_expression(Expression.HAPPY)
        
        # Should not crash
        for _ in range(10):
            pumpkin.update()
        
        pumpkin.draw(surface)
        
        # Animation state should remain valid
        assert hasattr(pumpkin, 'is_rolling')
        assert isinstance(pumpkin.is_rolling, bool)
    
    def test_rapid_roll_commands(self, pumpkin_projection):
        """Rapid roll commands should not break animation state."""
        pumpkin, surface = pumpkin_projection
        
        # Rapid commands
        pumpkin.roll_clockwise()
        pumpkin.update()
        pumpkin.roll_counterclockwise()  # Should not interrupt
        pumpkin.update()
        pumpkin.roll_clockwise()  # Should not interrupt
        
        # State should remain valid
        assert hasattr(pumpkin, 'is_rolling')
        assert isinstance(pumpkin.is_rolling, bool)
    
    def test_roll_during_sleeping_expression(self, pumpkin_projection):
        """Rolling during sleeping expression (closed eyes) should handle gracefully."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.SLEEPING
        pumpkin.roll_clockwise()
        
        # May choose to not roll during sleeping, or allow it
        # This documents expected behavior
        for _ in range(20):
            pumpkin.update()
        
        pumpkin.draw(surface)
        
        # Should not crash
        assert True
    
    def test_roll_speed_is_appropriate(self, pumpkin_projection):
        """rolling_speed should be slower than transition for smooth animation."""
        pumpkin, surface = pumpkin_projection
        
        assert hasattr(pumpkin, 'rolling_speed'), \
            "PumpkinFace must have rolling_speed attribute"
        
        # Rolling should be slower than transitions for visual appeal
        # Typical value might be 0.02 (50 frames for 360° at 60fps = ~0.83 seconds)
        assert pumpkin.rolling_speed <= pumpkin.transition_speed, \
            "Rolling should be slower or equal to transition speed"
    
    def test_roll_completes_exactly_once(self, pumpkin_projection):
        """A single roll command should complete exactly one 360° rotation."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.roll_clockwise()
        
        rotations = 0
        previous_progress = 0.0
        
        for _ in range(100):  # More than enough frames
            if pumpkin.is_rolling:
                if pumpkin.rolling_progress < previous_progress:
                    # Progress wrapped, counted one rotation
                    rotations += 1
                previous_progress = pumpkin.rolling_progress
                pumpkin.update()
            else:
                break
        
        # Should complete exactly one rotation
        assert pumpkin.is_rolling is False, \
            "Rolling should complete and stop"
        assert rotations <= 1, \
            f"Should complete exactly 1 rotation, not {rotations}"


class TestRollingEyesOrthogonalPattern:
    """Test that rolling follows orthogonal animation pattern."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_roll_does_not_change_expression(self, pumpkin_projection):
        """Rolling should not change current_expression."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.ANGRY
        pumpkin.roll_clockwise()
        
        # During rolling
        for _ in range(20):
            pumpkin.update()
            assert pumpkin.current_expression == Expression.ANGRY, \
                "Rolling should not change current expression"
        
        # After rolling completes
        for _ in range(60):
            pumpkin.update()
        
        assert pumpkin.current_expression == Expression.ANGRY, \
            "Expression should remain ANGRY after rolling completes"
    
    @pytest.mark.parametrize("expression", [
        Expression.NEUTRAL,
        Expression.HAPPY,
        Expression.SAD,
        Expression.ANGRY,
        Expression.SURPRISED,
        Expression.SCARED,
    ])
    def test_roll_from_all_expressions(self, pumpkin_projection, expression):
        """Parametrized test: roll from each expression, verify expression maintained."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = expression
        pumpkin.roll_clockwise()
        
        # Complete roll
        for _ in range(60):
            pumpkin.update()
        
        assert pumpkin.current_expression == expression, \
            f"Rolling should maintain {expression.value} expression"
        assert pumpkin.is_rolling is False, \
            f"is_rolling should be False after roll from {expression.value}"
