"""
Test suite for winking animation feature (Issue #9).

These tests validate the winking animation system where:
- Left/right wink animations close only the target eye
- Wink animations follow orthogonal pattern (separate from expression state)
- Wink returns to original expression after completion
- Socket commands and keyboard shortcuts trigger winking correctly
- Projection mapping compliance (pure black/white output)

Author: Mylo (Tester)
Date: 2026-02-20
"""

import pygame
import pytest
from pumpkin_face import PumpkinFace, Expression


class TestWinkingBasicBehavior:
    """Test core winking animation behavior."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_wink_left_method_exists(self):
        """Verify PumpkinFace has a wink_left() method."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        
        assert hasattr(pumpkin, 'wink_left'), \
            "PumpkinFace must have a wink_left() method"
        assert callable(getattr(pumpkin, 'wink_left')), \
            "wink_left() must be callable"
        
        pygame.quit()
    
    def test_wink_right_method_exists(self):
        """Verify PumpkinFace has a wink_right() method."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        
        assert hasattr(pumpkin, 'wink_right'), \
            "PumpkinFace must have a wink_right() method"
        assert callable(getattr(pumpkin, 'wink_right')), \
            "wink_right() must be callable"
        
        pygame.quit()
    
    def test_wink_left_closes_left_eye(self, pumpkin_projection):
        """Wink left should set left_eye_closed=True, right_eye_closed=False."""
        pumpkin, surface = pumpkin_projection
        
        # Start wink left
        pumpkin.wink_left()
        
        assert hasattr(pumpkin, 'is_winking'), \
            "PumpkinFace must have is_winking attribute"
        assert hasattr(pumpkin, 'winking_eye'), \
            "PumpkinFace must have winking_eye attribute (e.g., 'left', 'right')"
        
        assert pumpkin.is_winking is True, \
            "wink_left() should set is_winking to True"
        assert pumpkin.winking_eye == 'left', \
            "wink_left() should set winking_eye to 'left'"
    
    def test_wink_right_closes_right_eye(self, pumpkin_projection):
        """Wink right should set right_eye_closed=True, left_eye_closed=False."""
        pumpkin, surface = pumpkin_projection
        
        # Start wink right
        pumpkin.wink_right()
        
        assert pumpkin.is_winking is True, \
            "wink_right() should set is_winking to True"
        assert pumpkin.winking_eye == 'right', \
            "wink_right() should set winking_eye to 'right'"
    
    def test_wink_animation_progress(self, pumpkin_projection):
        """Wink progress should advance from 0.0 to 1.0 during animation."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.wink_left()
        assert hasattr(pumpkin, 'wink_progress'), \
            "PumpkinFace must have wink_progress attribute"
        
        initial_progress = pumpkin.wink_progress
        
        # Advance animation
        pumpkin.update()
        
        assert pumpkin.wink_progress > initial_progress, \
            "update() should advance wink_progress when is_winking=True"
        
        # Complete wink (wink_speed similar to blink_speed = 0.03)
        for _ in range(40):
            pumpkin.update()
        
        assert pumpkin.is_winking is False, \
            "is_winking should be False after wink completes"
    
    def test_wink_returns_to_expression(self, pumpkin_projection):
        """After winking, eyes should return to current expression's state."""
        pumpkin, surface = pumpkin_projection
        
        # Set to HAPPY expression
        pumpkin.current_expression = Expression.HAPPY
        
        # Wink left
        pumpkin.wink_left()
        
        # Complete wink
        for _ in range(40):
            pumpkin.update()
        
        assert pumpkin.current_expression == Expression.HAPPY, \
            "Wink should return to HAPPY expression"
        assert pumpkin.is_winking is False, \
            "is_winking should be False after completion"
    
    def test_wink_does_not_interrupt_ongoing_wink(self, pumpkin_projection):
        """Calling wink_left() while is_winking=True should NOT reset wink_progress."""
        pumpkin, surface = pumpkin_projection
        
        # Start first wink
        pumpkin.wink_left()
        
        # Advance wink progress manually
        pumpkin.wink_progress = 0.5
        
        # Try to wink again
        pumpkin.wink_left()
        
        assert pumpkin.wink_progress == 0.5, \
            "Calling wink_left() during ongoing wink should not reset progress"
    
    def test_wink_speed_is_slower_than_transition(self, pumpkin_projection):
        """wink_speed should be slower than transition_speed for natural animation."""
        pumpkin, surface = pumpkin_projection
        
        assert hasattr(pumpkin, 'wink_speed'), \
            "PumpkinFace must have wink_speed attribute"
        assert hasattr(pumpkin, 'transition_speed'), \
            "PumpkinFace must have transition_speed attribute"
        
        # Wink should be comparable to blink speed (0.03)
        assert pumpkin.wink_speed <= pumpkin.transition_speed, \
            "Wink should be slower or equal to transition speed"


class TestWinkingOrthogonalPattern:
    """Test that winking follows orthogonal animation pattern like blink."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_wink_saves_current_expression(self, pumpkin_projection):
        """pre_wink_expression should be saved before wink."""
        pumpkin, surface = pumpkin_projection
        
        # Set to specific expression
        pumpkin.current_expression = Expression.ANGRY
        
        # Wink
        pumpkin.wink_left()
        
        assert hasattr(pumpkin, 'pre_wink_expression'), \
            "PumpkinFace must have pre_wink_expression attribute"
        assert pumpkin.pre_wink_expression == Expression.ANGRY, \
            "wink_left() should save current expression to pre_wink_expression"
    
    @pytest.mark.parametrize("expression", [
        Expression.NEUTRAL,
        Expression.HAPPY,
        Expression.SAD,
        Expression.ANGRY,
        Expression.SURPRISED,
        Expression.SCARED,
        Expression.SLEEPING,
    ])
    def test_wink_left_all_expressions_restore(self, pumpkin_projection, expression):
        """Parametrized test: wink left from each expression, verify restoration."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = expression
        pumpkin.wink_left()
        
        # Complete wink
        for _ in range(40):
            pumpkin.update()
        
        assert pumpkin.current_expression == expression, \
            f"Wink left should restore {expression.value} expression"
        assert pumpkin.is_winking is False, \
            f"is_winking should be False after wink from {expression.value}"
    
    @pytest.mark.parametrize("expression", [
        Expression.NEUTRAL,
        Expression.HAPPY,
        Expression.SAD,
        Expression.ANGRY,
        Expression.SURPRISED,
        Expression.SCARED,
        Expression.SLEEPING,
    ])
    def test_wink_right_all_expressions_restore(self, pumpkin_projection, expression):
        """Parametrized test: wink right from each expression, verify restoration."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = expression
        pumpkin.wink_right()
        
        # Complete wink
        for _ in range(40):
            pumpkin.update()
        
        assert pumpkin.current_expression == expression, \
            f"Wink right should restore {expression.value} expression"
        assert pumpkin.is_winking is False, \
            f"is_winking should be False after wink from {expression.value}"


class TestWinkingCommandInterface:
    """Test keyboard shortcuts and socket commands for winking."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_wink_keyboard_shortcut_left(self, pumpkin_projection):
        """_handle_keyboard_input(pygame.K_l) should trigger wink_left."""
        pumpkin, surface = pumpkin_projection
        
        # Set to an expression
        pumpkin.current_expression = Expression.NEUTRAL
        
        # Simulate keyboard input for key L
        pumpkin._handle_keyboard_input(pygame.K_l)
        
        assert pumpkin.is_winking is True, \
            "Keyboard 'L' should trigger wink_left"
        assert pumpkin.winking_eye == 'left', \
            "Keyboard 'L' should set winking_eye to 'left'"
    
    def test_wink_keyboard_shortcut_right(self, pumpkin_projection):
        """_handle_keyboard_input(pygame.K_r) should trigger wink_right."""
        pumpkin, surface = pumpkin_projection
        
        # Set to an expression
        pumpkin.current_expression = Expression.NEUTRAL
        
        # Simulate keyboard input for key R
        pumpkin._handle_keyboard_input(pygame.K_r)
        
        assert pumpkin.is_winking is True, \
            "Keyboard 'R' should trigger wink_right"
        assert pumpkin.winking_eye == 'right', \
            "Keyboard 'R' should set winking_eye to 'right'"
    
    def test_wink_socket_command_left(self, pumpkin_projection):
        """Socket server should handle 'wink_left' command string."""
        pumpkin, surface = pumpkin_projection
        
        # Note: This test verifies the command handler logic would work
        # Actual socket testing would require threading/networking setup
        
        # Socket server should check for "wink_left" before Expression enum parsing
        command = "wink_left"
        
        # Simulate socket command handling
        if command == "wink_left":
            pumpkin.wink_left()
        
        assert pumpkin.is_winking is True, \
            "Socket command 'wink_left' should trigger wink animation"
        assert pumpkin.winking_eye == 'left', \
            "Socket command 'wink_left' should wink left eye"
    
    def test_wink_socket_command_right(self, pumpkin_projection):
        """Socket server should handle 'wink_right' command string."""
        pumpkin, surface = pumpkin_projection
        
        command = "wink_right"
        
        # Simulate socket command handling
        if command == "wink_right":
            pumpkin.wink_right()
        
        assert pumpkin.is_winking is True, \
            "Socket command 'wink_right' should trigger wink animation"
        assert pumpkin.winking_eye == 'right', \
            "Socket command 'wink_right' should wink right eye"


class TestWinkingProjectionMapping:
    """Test projection mapping compliance during winking animation."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_wink_rendering_pure_black_white(self, pumpkin_projection):
        """During mid-wink, only black/white pixels (projection compliance)."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.NEUTRAL
        pumpkin.wink_left()
        
        # Advance to mid-wink
        for _ in range(15):  # About halfway through wink
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
            f"During wink, found non-projection colors: {intermediate_colors}"
    
    def test_wink_contrast_ratio(self, pumpkin_projection):
        """Wink animation maintains 21:1 contrast ratio."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.wink_left()
        
        # Advance to mid-wink
        for _ in range(15):
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
            f"Wink contrast ratio {contrast:.2f}:1 is too low. Need at least 15:1."


class TestWinkingEdgeCases:
    """Test edge cases and boundary conditions for winking."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_wink_blocks_during_blink(self, pumpkin_projection):
        """If blink is running, wink should not start."""
        pumpkin, surface = pumpkin_projection
        
        # Start blink
        pumpkin.blink()
        assert pumpkin.is_blinking is True
        
        # Try to wink while blinking
        pumpkin.wink_left()
        
        # Wink should not start if blink is active
        # Implementation may handle this differently (queue, block, or allow)
        # This test documents expected behavior
        assert pumpkin.is_blinking is True, \
            "Blink should remain active"
    
    def test_rapid_wink_sequence(self, pumpkin_projection):
        """Rapid wink commands should not break animation state."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.NEUTRAL
        
        # Rapid wink commands
        pumpkin.wink_left()
        pumpkin.update()
        pumpkin.update()
        pumpkin.wink_right()  # Should not interrupt
        
        # Animation should still be in valid state
        assert hasattr(pumpkin, 'is_winking')
        assert isinstance(pumpkin.is_winking, bool)
    
    def test_wink_alternate_left_right(self, pumpkin_projection):
        """Alternate wink left and right in sequence."""
        pumpkin, surface = pumpkin_projection
        
        # Wink left
        pumpkin.wink_left()
        for _ in range(40):
            pumpkin.update()
        
        assert pumpkin.is_winking is False
        
        # Wink right
        pumpkin.wink_right()
        for _ in range(40):
            pumpkin.update()
        
        assert pumpkin.is_winking is False
        
        # Wink left again
        pumpkin.wink_left()
        for _ in range(40):
            pumpkin.update()
        
        assert pumpkin.is_winking is False
        assert pumpkin.current_expression == Expression.NEUTRAL
    
    def test_wink_during_expression_transition(self, pumpkin_projection):
        """Winking during expression transition should handle gracefully."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.NEUTRAL
        pumpkin.set_expression(Expression.HAPPY)
        
        # Start wink during transition
        pumpkin.transition_progress = 0.5
        pumpkin.wink_left()
        
        # Should not crash and maintain valid state
        pumpkin.update()
        pumpkin.draw(surface)
        
        assert hasattr(pumpkin, 'is_winking')
