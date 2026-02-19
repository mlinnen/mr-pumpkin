"""
Test suite for projection mapping feature (Issue #1).

These tests validate the projection mapping mode where:
- Background must be black (RGB 0,0,0)
- Pumpkin features (eyes, nose, mouth) must be white (RGB 255,255,255)
- High contrast must be maintained for projection
- All expression states must work correctly

Author: Mylo (Tester)
"""

import pygame
import pytest
from pumpkin_face import PumpkinFace, Expression


class TestProjectionMappingColors:
    """Test color validation for projection mapping mode."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        """Create a PumpkinFace instance in projection mode."""
        # Note: This will need to be updated once Ekko adds projection_mode parameter
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_background_is_black(self, pumpkin_projection):
        """Background must be pure black (0,0,0) for projection mapping."""
        pumpkin, surface = pumpkin_projection
        # TODO: Enable projection mode when implemented
        # pumpkin.projection_mode = True
        
        pumpkin.draw(surface)
        
        # Sample multiple points in the background (corners and edges)
        test_points = [
            (10, 10),           # Top-left
            (790, 10),          # Top-right
            (10, 590),          # Bottom-left
            (790, 590),         # Bottom-right
            (400, 10),          # Top-center
            (10, 300),          # Left-center
        ]
        
        for point in test_points:
            color = surface.get_at(point)[:3]  # RGB only
            assert color == (0, 0, 0), \
                f"Background at {point} should be black (0,0,0), got {color}"
    
    def test_eyes_are_white(self, pumpkin_projection):
        """Eye features must be white (255,255,255) for projection."""
        pumpkin, surface = pumpkin_projection
        # TODO: Enable projection mode when implemented
        
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.draw(surface)
        
        # Test center points of both eyes (approximate positions)
        # These coordinates will need adjustment based on final implementation
        left_eye_x = 400 - 100  # Center - eye offset
        right_eye_x = 400 + 100
        eye_y = 300 - 50
        
        # Sample multiple points within each eye
        for eye_x in [left_eye_x, right_eye_x]:
            eye_points = [
                (eye_x, eye_y),
                (eye_x + 10, eye_y),
                (eye_x - 10, eye_y),
                (eye_x, eye_y + 10),
                (eye_x, eye_y - 10),
            ]
            
            white_pixels = 0
            for point in eye_points:
                color = surface.get_at(point)[:3]
                if color == (255, 255, 255):
                    white_pixels += 1
            
            # At least some eye pixels should be white
            assert white_pixels > 0, \
                f"Eye at x={eye_x} should have white pixels, found none"
    
    def test_mouth_is_white(self, pumpkin_projection):
        """Mouth features must be white (255,255,255) for projection."""
        pumpkin, surface = pumpkin_projection
        # TODO: Enable projection mode when implemented
        
        pumpkin.set_expression(Expression.HAPPY)
        pumpkin.draw(surface)
        
        # Test mouth area (approximate center)
        mouth_y = 300 + 80
        mouth_points = [
            (400, mouth_y),
            (400 - 50, mouth_y),
            (400 + 50, mouth_y),
        ]
        
        white_pixels = 0
        for point in mouth_points:
            color = surface.get_at(point)[:3]
            if color == (255, 255, 255):
                white_pixels += 1
        
        assert white_pixels > 0, \
            "Mouth should have white pixels for projection"


class TestProjectionMappingContrast:
    """Test contrast validation for projection mapping."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_contrast_ratio(self, pumpkin_projection):
        """Verify sufficient contrast between background and features."""
        pumpkin, surface = pumpkin_projection
        # TODO: Enable projection mode when implemented
        
        pumpkin.draw(surface)
        
        # Sample feature and background colors
        background_color = surface.get_at((50, 50))[:3]
        feature_color = (255, 255, 255)  # Expected feature color
        
        # Calculate luminance (simplified)
        def luminance(rgb):
            r, g, b = [x / 255.0 for x in rgb]
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        bg_lum = luminance(background_color)
        feature_lum = luminance(feature_color)
        
        # Calculate contrast ratio
        lighter = max(bg_lum, feature_lum)
        darker = min(bg_lum, feature_lum)
        contrast = (lighter + 0.05) / (darker + 0.05)
        
        # WCAG AAA requires 7:1 for text, we want at least 15:1 for projection
        assert contrast >= 15.0, \
            f"Contrast ratio {contrast:.2f}:1 is too low. Need at least 15:1 for projection."
    
    def test_no_intermediate_colors(self, pumpkin_projection):
        """Ensure only black and white are used, no gray values."""
        pumpkin, surface = pumpkin_projection
        # TODO: Enable projection mode when implemented
        
        pumpkin.draw(surface)
        
        # Sample the entire surface
        width, height = surface.get_size()
        intermediate_colors = set()
        
        # Sample every 20th pixel to avoid performance issues
        for x in range(0, width, 20):
            for y in range(0, height, 20):
                color = surface.get_at((x, y))[:3]
                # Allow only pure black or pure white
                if color != (0, 0, 0) and color != (255, 255, 255):
                    intermediate_colors.add(color)
        
        assert len(intermediate_colors) == 0, \
            f"Found intermediate colors (expected only black/white): {intermediate_colors}"


class TestProjectionMappingExpressions:
    """Test that all expressions work correctly in projection mapping mode."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    @pytest.mark.parametrize("expression", [
        Expression.NEUTRAL,
        Expression.HAPPY,
        Expression.SAD,
        Expression.ANGRY,
        Expression.SURPRISED,
        Expression.SCARED,
    ])
    def test_expression_renders_in_projection_mode(self, pumpkin_projection, expression):
        """Each expression should render correctly in projection mode."""
        pumpkin, surface = pumpkin_projection
        # TODO: Enable projection mode when implemented
        
        pumpkin.set_expression(expression)
        pumpkin.current_expression = expression  # Skip transition for testing
        pumpkin.draw(surface)
        
        # Verify the surface contains both black and white pixels
        width, height = surface.get_size()
        has_black = False
        has_white = False
        
        # Sample center region where features should be
        for x in range(200, 600, 50):
            for y in range(100, 500, 50):
                color = surface.get_at((x, y))[:3]
                if color == (0, 0, 0):
                    has_black = True
                if color == (255, 255, 255):
                    has_white = True
                if has_black and has_white:
                    break
            if has_black and has_white:
                break
        
        assert has_black, f"Expression {expression.value} should have black background"
        assert has_white, f"Expression {expression.value} should have white features"
    
    def test_expression_transitions(self, pumpkin_projection):
        """Test that transitions between expressions maintain projection colors."""
        pumpkin, surface = pumpkin_projection
        # TODO: Enable projection mode when implemented
        
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.current_expression = Expression.NEUTRAL
        
        # Transition to HAPPY
        pumpkin.set_expression(Expression.HAPPY)
        
        # Render during transition
        pumpkin.transition_progress = 0.5
        pumpkin.draw(surface)
        
        # Even during transition, colors should be pure black and white
        # (This test may need adjustment based on how transitions are implemented)
        sample_points = [(x, y) for x in range(100, 700, 100) for y in range(100, 500, 100)]
        
        for point in sample_points:
            color = surface.get_at(point)[:3]
            # Allow only pure black or pure white
            assert color == (0, 0, 0) or color == (255, 255, 255), \
                f"During transition, found non-projection color {color} at {point}"


class TestProjectionMappingFeatureCompleteness:
    """Test that all required features are visible in projection mode."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_has_two_eyes(self, pumpkin_projection):
        """Projection mode must render two distinct eyes."""
        pumpkin, surface = pumpkin_projection
        # TODO: Enable projection mode when implemented
        
        pumpkin.set_expression(Expression.NEUTRAL)
        pumpkin.draw(surface)
        
        # Look for two separate white regions in the eye area
        # This is a simplified test - may need refinement
        eye_y = 250
        left_region = (200, 350)
        right_region = (450, 600)
        
        left_has_white = any(
            surface.get_at((x, eye_y))[:3] == (255, 255, 255)
            for x in range(left_region[0], left_region[1], 10)
        )
        
        right_has_white = any(
            surface.get_at((x, eye_y))[:3] == (255, 255, 255)
            for x in range(right_region[0], right_region[1], 10)
        )
        
        assert left_has_white, "Left eye should be visible in projection mode"
        assert right_has_white, "Right eye should be visible in projection mode"
    
    def test_has_mouth(self, pumpkin_projection):
        """Projection mode must render a visible mouth."""
        pumpkin, surface = pumpkin_projection
        # TODO: Enable projection mode when implemented
        
        pumpkin.set_expression(Expression.HAPPY)
        pumpkin.draw(surface)
        
        # Look for white pixels in the mouth area
        mouth_region_y = range(350, 450)
        mouth_region_x = range(250, 550)
        
        has_mouth = False
        for y in range(350, 450, 10):
            for x in range(250, 550, 10):
                if surface.get_at((x, y))[:3] == (255, 255, 255):
                    has_mouth = True
                    break
            if has_mouth:
                break
        
        assert has_mouth, "Mouth should be visible in projection mode"


class TestProjectionMappingEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_different_resolutions(self):
        """Projection mode should work at different resolutions."""
        pygame.init()
        
        resolutions = [
            (800, 600),
            (1920, 1080),
            (1024, 768),
            (640, 480),
        ]
        
        for width, height in resolutions:
            pumpkin = PumpkinFace(width=width, height=height)
            surface = pygame.Surface((width, height))
            
            # TODO: Enable projection mode when implemented
            pumpkin.draw(surface)
            
            # Check background is black at corners
            corner_colors = [
                surface.get_at((10, 10))[:3],
                surface.get_at((width - 10, 10))[:3],
                surface.get_at((10, height - 10))[:3],
                surface.get_at((width - 10, height - 10))[:3],
            ]
            
            for i, color in enumerate(corner_colors):
                assert color == (0, 0, 0), \
                    f"Resolution {width}x{height}, corner {i}: expected black, got {color}"
        
        pygame.quit()
    
    def test_rapid_expression_changes(self, pumpkin_projection):
        """Rapid expression changes should maintain projection colors."""
        pumpkin, surface = pumpkin_projection
        # TODO: Enable projection mode when implemented
        
        expressions = [
            Expression.NEUTRAL,
            Expression.HAPPY,
            Expression.SAD,
            Expression.ANGRY,
            Expression.SURPRISED,
            Expression.SCARED,
        ]
        
        # Rapidly cycle through expressions
        for expression in expressions:
            pumpkin.set_expression(expression)
            pumpkin.current_expression = expression  # Skip transition
            pumpkin.draw(surface)
            
            # Sample a few points to ensure colors are still valid
            sample_colors = [
                surface.get_at((50, 50))[:3],
                surface.get_at((400, 300))[:3],
                surface.get_at((750, 550))[:3],
            ]
            
            for color in sample_colors:
                assert color in [(0, 0, 0), (255, 255, 255)], \
                    f"During rapid changes, found invalid color {color}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
