"""Automated test for nose rendering (Issue #19).

Tests nose graphics implementation:
- Nose renders as white triangle (40x50px, apex UP)
- Positioned at center_y + 15 (between eyes and mouth)
- Follows projection offset (moves with head)
- Maintains projection mapping colors (white on black)
"""

import pygame
import pytest
from pumpkin_face import PumpkinFace, Expression


class TestNoseRendering:
    """Test nose rendering and positioning."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_nose_renders_white(self, pumpkin):
        """Nose must be white (255,255,255) for projection mapping."""
        pumpkin, surface = pumpkin
        pumpkin.draw(surface)
        
        # Nose is positioned at center_y + 15
        # With center at (400, 300), nose base should be around y=315
        # Check pixels in the nose area (center of triangle)
        center_x = 400
        nose_y = 300 + 15 - 25  # Approx midpoint of 50px tall triangle
        
        # Sample point in the nose triangle
        color = surface.get_at((center_x, nose_y))[:3]
        assert color == (255, 255, 255), f"Nose should be white (255,255,255), got {color}"
    
    def test_nose_position_between_eyes_and_mouth(self, pumpkin):
        """Nose should be positioned between eyes and mouth."""
        pumpkin, surface = pumpkin
        pumpkin.draw(surface)
        
        # Eyes are at center_y - 50 = 250
        # Mouth is at center_y + 80 = 380
        # Nose base should be at center_y + 15 = 315 (between 250 and 380)
        center_x = 400
        
        # Check that there's white at the nose position
        nose_base_y = 300 + 15
        nose_apex_y = nose_base_y - 50
        
        # Check midpoint of nose
        nose_mid_y = int((nose_base_y + nose_apex_y) / 2)
        color = surface.get_at((center_x, nose_mid_y))[:3]
        assert color == (255, 255, 255), f"Nose should be visible at y={nose_mid_y}"
    
    def test_nose_follows_projection_offset(self, pumpkin):
        """Nose should move with projection offset (head movement)."""
        pumpkin, surface = pumpkin
        
        # Set projection offset
        pumpkin.set_projection_offset(100, 50)
        pumpkin.draw(surface)
        
        # With offset (100, 50), nose should be at:
        # center_x: 400 + 100 = 500
        # center_y: 300 + 50 = 350
        # nose_y: 350 + 15 = 365 (base)
        offset_center_x = 400 + 100
        offset_nose_y = 300 + 50 + 15 - 25  # Midpoint
        
        # Check that nose moved with projection offset
        color = surface.get_at((offset_center_x, offset_nose_y))[:3]
        assert color == (255, 255, 255), f"Nose should follow projection offset"
    
    def test_nose_renders_on_all_expressions(self, pumpkin):
        """Nose should render on all expression states."""
        pumpkin, surface = pumpkin
        
        for expression in Expression:
            pumpkin.set_expression(expression)
            pumpkin.update()  # Complete transition
            for _ in range(20):  # Wait for transition
                pumpkin.update()
            
            surface.fill((0, 0, 0))  # Clear
            pumpkin.draw(surface)
            
            # Check nose is visible (sample center of nose area)
            center_x = 400
            nose_y = 300 + 15 - 25
            color = surface.get_at((center_x, nose_y))[:3]
            
            # Nose should be white on all expressions
            assert color == (255, 255, 255), \
                f"Nose should be visible on {expression.value}, got {color}"


class TestNoseAnimation:
    """Test nose animation state."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        yield pumpkin
        pygame.quit()
    
    def test_nose_twitch_method_exists(self, pumpkin):
        """twitch_nose() method should exist."""
        assert hasattr(pumpkin, 'twitch_nose'), "PumpkinFace should have twitch_nose method"
        assert callable(pumpkin.twitch_nose), "twitch_nose should be callable"
    
    def test_nose_scrunch_method_exists(self, pumpkin):
        """scrunch_nose() method should exist."""
        assert hasattr(pumpkin, 'scrunch_nose'), "PumpkinFace should have scrunch_nose method"
        assert callable(pumpkin.scrunch_nose), "scrunch_nose should be callable"
    
    def test_nose_reset_method_exists(self, pumpkin):
        """reset_nose() method should exist."""
        assert hasattr(pumpkin, 'reset_nose'), "PumpkinFace should have reset_nose method"
        assert callable(pumpkin.reset_nose), "reset_nose should be callable"
    
    def test_twitch_sets_animation_flag(self, pumpkin):
        """twitch_nose() should set is_twitching flag."""
        pumpkin.twitch_nose()
        assert pumpkin.is_twitching, "is_twitching should be True after twitch_nose()"
    
    def test_scrunch_sets_animation_flag(self, pumpkin):
        """scrunch_nose() should set is_scrunching flag."""
        pumpkin.scrunch_nose()
        assert pumpkin.is_scrunching, "is_scrunching should be True after scrunch_nose()"
    
    def test_twitch_progress_advances(self, pumpkin):
        """Twitching animation progress should advance during update."""
        pumpkin.twitch_nose()
        initial_progress = pumpkin.nose_animation_progress
        
        for _ in range(5):
            pumpkin.update()
        
        assert pumpkin.nose_animation_progress > initial_progress, \
            "Animation progress should increase during update()"
    
    def test_twitch_completes_and_resets(self, pumpkin):
        """Twitching animation should complete and auto-reset."""
        pumpkin.twitch_nose()
        
        # Run until animation completes (0.5s at 60fps = 30 frames)
        for _ in range(35):
            pumpkin.update()
        
        assert not pumpkin.is_twitching, "is_twitching should be False after completion"
        assert pumpkin.nose_offset_x == 0.0, "nose_offset_x should return to 0 after completion"
    
    def test_scrunch_completes_and_resets(self, pumpkin):
        """Scrunching animation should complete and auto-reset."""
        pumpkin.scrunch_nose()
        
        # Run until animation completes (0.8s at 60fps = 48 frames)
        for _ in range(55):
            pumpkin.update()
        
        assert not pumpkin.is_scrunching, "is_scrunching should be False after completion"
        assert pumpkin.nose_scale == 1.0, "nose_scale should return to 1.0 after completion"
    
    def test_twitch_non_interrupting(self, pumpkin):
        """Twitch animation should reject overlapping calls."""
        pumpkin.twitch_nose()
        assert pumpkin.is_twitching
        
        # Try to start another twitch
        pumpkin.twitch_nose()
        
        # Should still be first twitch (guard prevents restart)
        # Progress should continue from first call
        for _ in range(5):
            pumpkin.update()
        
        # If guard works, animation continues; if not, progress resets to ~0
        assert pumpkin.nose_animation_progress > 0.1, \
            "Animation should continue without restart"
    
    def test_nose_orthogonal_to_expressions(self, pumpkin):
        """Nose animations should not affect expression state."""
        pumpkin.set_expression(Expression.HAPPY)
        
        # Wait for expression transition to complete
        for _ in range(25):
            pumpkin.update()
        
        # Trigger nose animation
        pumpkin.twitch_nose()
        
        # Expression should remain unchanged
        for _ in range(10):
            pumpkin.update()
        
        assert pumpkin.current_expression == Expression.HAPPY, \
            "Expression should not change during nose animation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
