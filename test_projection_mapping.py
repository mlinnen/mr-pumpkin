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


class TestSleepingExpression:
    """Test suite for SLEEPING expression (Issue #4)."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_sleeping_expression_exists(self):
        """SLEEPING expression must exist in Expression enum."""
        assert hasattr(Expression, 'SLEEPING'), \
            "Expression.SLEEPING must be defined in the Expression enum"
        
        # Verify it has the correct value
        assert Expression.SLEEPING.value == "sleeping", \
            "Expression.SLEEPING value should be 'sleeping'"
    
    def test_sleeping_eyes_are_white_horizontal_lines(self, pumpkin_projection):
        """Sleeping eyes must render as white horizontal lines (closed eyes)."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.set_expression(Expression.SLEEPING)
        pumpkin.current_expression = Expression.SLEEPING  # Skip transition for testing
        pumpkin.draw(surface)
        
        # Test approximate eye positions (horizontal lines)
        center_x = 400
        center_y = 300
        left_eye_x = center_x - 100
        right_eye_x = center_x + 100
        eye_y = center_y - 50
        
        # Check that horizontal lines have white pixels
        # Sample points along the horizontal line for each eye
        for eye_x in [left_eye_x, right_eye_x]:
            white_pixels = 0
            for offset_x in range(-30, 31, 5):  # Sample along horizontal line
                color = surface.get_at((eye_x + offset_x, eye_y))[:3]
                if color == (255, 255, 255):
                    white_pixels += 1
            
            assert white_pixels > 0, \
                f"Sleeping eye at x={eye_x} should have white horizontal line pixels"
    
    def test_sleeping_eyes_have_no_pupils(self, pumpkin_projection):
        """Sleeping eyes should not show pupils (eyes are closed)."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.set_expression(Expression.SLEEPING)
        pumpkin.current_expression = Expression.SLEEPING
        pumpkin.draw(surface)
        
        # Sample the eye region to verify no circular pupils exist
        # For sleeping expression, we should see horizontal lines only
        center_x = 400
        center_y = 300
        left_eye_x = center_x - 100
        right_eye_x = center_x + 100
        eye_y = center_y - 50
        
        # Check that vertical samples around the eye line don't show
        # the same pattern as open eyes with pupils
        for eye_x in [left_eye_x, right_eye_x]:
            # Sample vertically around the eye line
            colors_above_line = []
            colors_below_line = []
            
            for offset_y in range(5, 25, 5):
                colors_above_line.append(surface.get_at((eye_x, eye_y - offset_y))[:3])
                colors_below_line.append(surface.get_at((eye_x, eye_y + offset_y))[:3])
            
            # Above and below the horizontal line should be black (background)
            # This distinguishes closed eyes from open eyes with pupils
            black_above = sum(1 for c in colors_above_line if c == (0, 0, 0))
            black_below = sum(1 for c in colors_below_line if c == (0, 0, 0))
            
            # At least some samples should be black, indicating no circular eye shape
            assert black_above > 0 or black_below > 0, \
                f"Sleeping eye at x={eye_x} should not show open eye/pupil pattern"
    
    def test_sleeping_contrast_ratio(self, pumpkin_projection):
        """Sleeping expression must maintain 15:1 contrast ratio."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.set_expression(Expression.SLEEPING)
        pumpkin.current_expression = Expression.SLEEPING
        pumpkin.draw(surface)
        
        # Sample background and feature colors
        background_color = surface.get_at((50, 50))[:3]
        assert background_color == (0, 0, 0), "Background should be black"
        
        # Find a white pixel in the sleeping eyes
        center_x = 400
        eye_y = 250
        feature_color = None
        
        for x in range(center_x - 150, center_x + 150, 5):
            color = surface.get_at((x, eye_y))[:3]
            if color == (255, 255, 255):
                feature_color = color
                break
        
        assert feature_color is not None, "Should find white pixels in sleeping eyes"
        
        # Calculate luminance and contrast
        def luminance(rgb):
            r, g, b = [x / 255.0 for x in rgb]
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        bg_lum = luminance(background_color)
        feature_lum = luminance(feature_color)
        
        lighter = max(bg_lum, feature_lum)
        darker = min(bg_lum, feature_lum)
        contrast = (lighter + 0.05) / (darker + 0.05)
        
        assert contrast >= 15.0, \
            f"Sleeping expression contrast {contrast:.2f}:1 is too low (need 15:1 minimum)"
    
    def test_transition_to_sleeping(self, pumpkin_projection):
        """Must be able to transition from any expression to SLEEPING."""
        pumpkin, surface = pumpkin_projection
        
        expressions = [
            Expression.NEUTRAL,
            Expression.HAPPY,
            Expression.SAD,
            Expression.ANGRY,
            Expression.SURPRISED,
            Expression.SCARED,
        ]
        
        for start_expr in expressions:
            pumpkin.current_expression = start_expr
            pumpkin.set_expression(Expression.SLEEPING)
            
            assert pumpkin.target_expression == Expression.SLEEPING, \
                f"Should be able to transition from {start_expr.value} to SLEEPING"
            
            # Complete the transition
            pumpkin.current_expression = Expression.SLEEPING
            pumpkin.transition_progress = 1.0
            pumpkin.draw(surface)
            
            # Verify it rendered without errors
            # Check that surface has both black and white
            has_black = surface.get_at((50, 50))[:3] == (0, 0, 0)
            
            # Find white pixels in eye area
            has_white = False
            for x in range(200, 600, 5):
                for y in range(200, 350, 5):
                    if surface.get_at((x, y))[:3] == (255, 255, 255):
                        has_white = True
                        break
                if has_white:
                    break
            
            assert has_black, f"Transition from {start_expr.value} should maintain black background"
            assert has_white, f"Transition from {start_expr.value} should show sleeping eyes"
    
    def test_transition_from_sleeping(self, pumpkin_projection):
        """Must be able to transition from SLEEPING back to other expressions."""
        pumpkin, surface = pumpkin_projection
        
        expressions = [
            Expression.NEUTRAL,
            Expression.HAPPY,
            Expression.SAD,
            Expression.ANGRY,
            Expression.SURPRISED,
            Expression.SCARED,
        ]
        
        for target_expr in expressions:
            pumpkin.current_expression = Expression.SLEEPING
            pumpkin.set_expression(target_expr)
            
            assert pumpkin.target_expression == target_expr, \
                f"Should be able to transition from SLEEPING to {target_expr.value}"
            
            # Complete the transition
            pumpkin.current_expression = target_expr
            pumpkin.transition_progress = 1.0
            pumpkin.draw(surface)
            
            # Verify it rendered the target expression
            has_black = surface.get_at((50, 50))[:3] == (0, 0, 0)
            
            # Find white pixels (eyes or mouth)
            has_white = False
            for x in range(200, 600, 20):
                for y in range(150, 450, 20):
                    if surface.get_at((x, y))[:3] == (255, 255, 255):
                        has_white = True
                        break
                if has_white:
                    break
            
            assert has_black, f"Transition to {target_expr.value} should maintain black background"
            assert has_white, f"Transition to {target_expr.value} should show features"
    
    def test_socket_command_sleeping(self, pumpkin_projection):
        """Socket command 'sleeping' should trigger SLEEPING expression."""
        pumpkin, surface = pumpkin_projection
        
        # Simulate socket command processing
        command = "sleeping"
        
        try:
            expression = Expression(command)
            pumpkin.set_expression(expression)
            
            assert pumpkin.target_expression == Expression.SLEEPING, \
                "Socket command 'sleeping' should set target to SLEEPING"
        except ValueError:
            pytest.fail("Expression enum should accept 'sleeping' value")
    
    def test_keyboard_shortcut_7_maps_to_sleeping(self):
        """Keyboard shortcut 7 should map to SLEEPING expression."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        
        # Simulate keyboard input for key 7
        pumpkin._handle_keyboard_input(pygame.K_7)
        
        assert pumpkin.target_expression == Expression.SLEEPING, \
            "Keyboard shortcut 7 should trigger SLEEPING expression"
        
        pygame.quit()
    
    def test_sleeping_eyes_use_projection_colors(self, pumpkin_projection):
        """Sleeping eyes must use only black and white (no intermediate colors)."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.set_expression(Expression.SLEEPING)
        pumpkin.current_expression = Expression.SLEEPING
        pumpkin.draw(surface)
        
        # Sample the entire surface for intermediate colors
        width, height = surface.get_size()
        intermediate_colors = set()
        
        # Focus on eye region where sleeping lines should be
        for x in range(150, 650, 10):
            for y in range(200, 350, 10):
                color = surface.get_at((x, y))[:3]
                if color != (0, 0, 0) and color != (255, 255, 255):
                    intermediate_colors.add(color)
        
        assert len(intermediate_colors) == 0, \
            f"Sleeping expression should use only black/white, found: {intermediate_colors}"


class TestBlinkAnimation:
    """Test suite for blink animation feature (Issue #5)."""
    
    @pytest.fixture
    def pumpkin_projection(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        surface = pygame.Surface((800, 600))
        yield pumpkin, surface
        pygame.quit()
    
    def test_blink_method_exists(self):
        """Verify PumpkinFace has a blink() method."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        
        assert hasattr(pumpkin, 'blink'), \
            "PumpkinFace must have a blink() method"
        assert callable(getattr(pumpkin, 'blink')), \
            "blink() must be callable"
        
        pygame.quit()
    
    def test_blink_sets_is_blinking_flag(self, pumpkin_projection):
        """After calling blink(), is_blinking should be True."""
        pumpkin, surface = pumpkin_projection
        
        # Initially not blinking
        assert hasattr(pumpkin, 'is_blinking'), \
            "PumpkinFace must have is_blinking attribute"
        
        # Call blink
        pumpkin.blink()
        
        assert pumpkin.is_blinking is True, \
            "blink() should set is_blinking to True"
    
    def test_blink_saves_current_expression(self, pumpkin_projection):
        """pre_blink_expression should be saved before blink."""
        pumpkin, surface = pumpkin_projection
        
        # Set to a specific expression
        pumpkin.current_expression = Expression.HAPPY
        
        # Call blink
        pumpkin.blink()
        
        assert hasattr(pumpkin, 'pre_blink_expression'), \
            "PumpkinFace must have pre_blink_expression attribute"
        assert pumpkin.pre_blink_expression == Expression.HAPPY, \
            "blink() should save current expression to pre_blink_expression"
    
    def test_blink_does_not_interrupt_ongoing_blink(self, pumpkin_projection):
        """Calling blink() while is_blinking=True should NOT reset blink_progress."""
        pumpkin, surface = pumpkin_projection
        
        # Start first blink
        pumpkin.blink()
        initial_progress = pumpkin.blink_progress
        
        # Advance blink progress manually
        pumpkin.blink_progress = 0.4
        
        # Try to blink again
        pumpkin.blink()
        
        assert pumpkin.blink_progress == 0.4, \
            "Calling blink() during ongoing blink should not reset progress"
    
    def test_blink_progress_advances_in_update(self, pumpkin_projection):
        """Calling update() while blinking should advance blink_progress."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.blink()
        initial_progress = pumpkin.blink_progress
        
        # Call update
        pumpkin.update()
        
        assert pumpkin.blink_progress > initial_progress, \
            "update() should advance blink_progress when is_blinking=True"
    
    def test_blink_completes_and_restores_expression(self, pumpkin_projection):
        """After enough update() calls, is_blinking should be False and expression restored."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.SAD
        pumpkin.blink()
        
        # Call update() enough times to complete blink
        # blink_speed = 0.03, so need 1.0 / 0.03 = 34 updates
        for _ in range(40):  # Extra margin
            pumpkin.update()
        
        assert pumpkin.is_blinking is False, \
            "is_blinking should be False after blink completes"
        assert pumpkin.current_expression == Expression.SAD, \
            "Expression should be restored after blink completes"
    
    def test_blink_restores_original_expression(self, pumpkin_projection):
        """Verify the EXACT original expression (not neutral) is restored after blink."""
        pumpkin, surface = pumpkin_projection
        
        # Test with non-neutral expression
        pumpkin.current_expression = Expression.ANGRY
        pumpkin.blink()
        
        # Complete blink
        for _ in range(40):
            pumpkin.update()
        
        assert pumpkin.current_expression == Expression.ANGRY, \
            "Blink should restore ANGRY, not NEUTRAL"
        
        # Test with another expression
        pumpkin.current_expression = Expression.SURPRISED
        pumpkin.blink()
        
        for _ in range(40):
            pumpkin.update()
        
        assert pumpkin.current_expression == Expression.SURPRISED, \
            "Blink should restore SURPRISED, not NEUTRAL"
    
    def test_blink_speed_is_slower_than_transition(self, pumpkin_projection):
        """blink_speed (0.03) < transition_speed (0.05)."""
        pumpkin, surface = pumpkin_projection
        
        assert hasattr(pumpkin, 'blink_speed'), \
            "PumpkinFace must have blink_speed attribute"
        assert hasattr(pumpkin, 'transition_speed'), \
            "PumpkinFace must have transition_speed attribute"
        
        assert pumpkin.blink_speed == 0.03, \
            "blink_speed should be 0.03"
        assert pumpkin.transition_speed == 0.05, \
            "transition_speed should be 0.05"
        assert pumpkin.blink_speed < pumpkin.transition_speed, \
            "Blink should be slower than normal transitions"
    
    def test_blink_maintains_projection_colors(self, pumpkin_projection):
        """During mid-blink, only black/white pixels (projection compliance)."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = Expression.NEUTRAL
        pumpkin.blink()
        
        # Advance to mid-blink
        for _ in range(15):  # About halfway through blink
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
            f"During blink, found non-projection colors: {intermediate_colors}"
    
    @pytest.mark.parametrize("expression", [
        Expression.NEUTRAL,
        Expression.HAPPY,
        Expression.SAD,
        Expression.ANGRY,
        Expression.SURPRISED,
        Expression.SCARED,
        Expression.SLEEPING,
    ])
    def test_blink_all_expressions_restore(self, pumpkin_projection, expression):
        """Parametrized test: blink while in each expression, verify correct restoration."""
        pumpkin, surface = pumpkin_projection
        
        pumpkin.current_expression = expression
        pumpkin.blink()
        
        # Complete blink
        for _ in range(40):
            pumpkin.update()
        
        assert pumpkin.current_expression == expression, \
            f"Blink should restore {expression.value} expression"
        assert pumpkin.is_blinking is False, \
            f"is_blinking should be False after blink from {expression.value}"
    
    def test_keyboard_b_triggers_blink(self):
        """_handle_keyboard_input(pygame.K_b) should trigger blink."""
        pygame.init()
        pumpkin = PumpkinFace(width=800, height=600)
        
        # Set to an expression
        pumpkin.current_expression = Expression.HAPPY
        
        # Simulate keyboard input for key B
        pumpkin._handle_keyboard_input(pygame.K_b)
        
        assert pumpkin.is_blinking is True, \
            "Keyboard shortcut B should trigger blink"
        assert pumpkin.pre_blink_expression == Expression.HAPPY, \
            "Keyboard B should save current expression before blink"
        
        pygame.quit()
    
    def test_socket_blink_command(self, pumpkin_projection):
        """Simulate 'blink' string coming through socket handler, verify blink() is triggered."""
        pumpkin, surface = pumpkin_projection
        
        # Set to an expression
        pumpkin.current_expression = Expression.SCARED
        
        # Simulate socket command handling
        # The socket handler should detect "blink" as a special command
        # and call pumpkin.blink() instead of treating it as an Expression
        command = "blink"
        
        # The implementation should have logic like:
        # if data == "blink":
        #     self.blink()
        # else:
        #     expression = Expression(data)
        #     self.set_expression(expression)
        
        # For testing, we verify that the blink method exists and can be called
        # The actual socket server integration is tested separately
        try:
            # This simulates what the socket handler should do
            if command == "blink":
                pumpkin.blink()
                
                assert pumpkin.is_blinking is True, \
                    "Socket 'blink' command should trigger blink"
                assert pumpkin.pre_blink_expression == Expression.SCARED, \
                    "Socket 'blink' command should save current expression"
            else:
                # Normal expression handling
                expression = Expression(command)
                pumpkin.set_expression(expression)
        except ValueError:
            pytest.fail("Socket command processing failed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
