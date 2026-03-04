"""
Test suite for mouth speech control (Issue #59).

These tests validate the mouth viseme system where:
- Mouth visemes override expression-driven mouth rendering
- Visemes: "closed", "open", "wide", "rounded", or None (neutral)
- Viseme state is orthogonal to expression state machine
- Commands: mouth_closed, mouth_open, mouth_wide, mouth_rounded, mouth_neutral
- Parameterized: "mouth <viseme_name>"

Author: Mylo (Tester)
"""

import pygame
import pytest
from pumpkin_face import PumpkinFace, Expression


class TestMouthStateManagement:
    """Test mouth viseme state variable behavior and transitions."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    def test_mouth_initializes_to_neutral(self, pumpkin):
        """mouth_viseme is None at start (expression-driven rendering)."""
        assert pumpkin.mouth_viseme is None
    
    def test_mouth_transition_progress_initializes_to_1(self, pumpkin):
        """mouth_transition_progress = 1.0 at start (fully transitioned)."""
        assert pumpkin.mouth_transition_progress == 1.0
    
    def test_set_mouth_viseme_closed(self, pumpkin):
        """set_mouth_viseme("closed") sets mouth_viseme to "closed"."""
        pumpkin.set_mouth_viseme("closed")
        assert pumpkin.mouth_viseme == "closed"
    
    def test_set_mouth_viseme_open(self, pumpkin):
        """set_mouth_viseme("open") sets mouth_viseme to "open"."""
        pumpkin.set_mouth_viseme("open")
        assert pumpkin.mouth_viseme == "open"
    
    def test_set_mouth_viseme_wide(self, pumpkin):
        """set_mouth_viseme("wide") sets mouth_viseme to "wide"."""
        pumpkin.set_mouth_viseme("wide")
        assert pumpkin.mouth_viseme == "wide"
    
    def test_set_mouth_viseme_rounded(self, pumpkin):
        """set_mouth_viseme("rounded") sets mouth_viseme to "rounded"."""
        pumpkin.set_mouth_viseme("rounded")
        assert pumpkin.mouth_viseme == "rounded"
    
    def test_set_mouth_viseme_neutral_clears_override(self, pumpkin):
        """set_mouth_viseme("neutral") → mouth_viseme becomes None."""
        pumpkin.set_mouth_viseme("open")
        assert pumpkin.mouth_viseme == "open"
        pumpkin.set_mouth_viseme("neutral")
        assert pumpkin.mouth_viseme is None
    
    def test_set_mouth_viseme_none_clears_override(self, pumpkin):
        """set_mouth_viseme(None) → mouth_viseme = None."""
        pumpkin.set_mouth_viseme("closed")
        assert pumpkin.mouth_viseme == "closed"
        pumpkin.set_mouth_viseme(None)
        assert pumpkin.mouth_viseme is None
    
    def test_set_mouth_viseme_starts_transition(self, pumpkin):
        """calling set_mouth_viseme sets transition_progress = 0.0."""
        pumpkin.mouth_transition_progress = 1.0
        pumpkin.set_mouth_viseme("wide")
        assert pumpkin.mouth_transition_progress == 0.0
    
    def test_reset_mouth_clears_viseme(self, pumpkin):
        """reset_mouth() → mouth_viseme = None, transition_progress = 1.0."""
        pumpkin.set_mouth_viseme("rounded")
        assert pumpkin.mouth_viseme == "rounded"
        pumpkin.reset_mouth()
        assert pumpkin.mouth_viseme is None
        assert pumpkin.mouth_transition_progress == 1.0


class TestMouthStateOrthogonality:
    """Test that mouth viseme state is independent of expression state."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    def test_expression_change_does_not_clear_viseme(self, pumpkin):
        """Set viseme, change expression → viseme still active."""
        pumpkin.set_mouth_viseme("open")
        assert pumpkin.mouth_viseme == "open"
        pumpkin.current_expression = Expression.HAPPY
        assert pumpkin.mouth_viseme == "open"
    
    def test_viseme_override_persists_across_expressions(self, pumpkin):
        """Verify mouth_viseme is NOT reset by set_expression."""
        pumpkin.set_mouth_viseme("wide")
        assert pumpkin.mouth_viseme == "wide"
        pumpkin.set_expression(Expression.SAD)
        assert pumpkin.mouth_viseme == "wide"
        pumpkin.set_expression(Expression.SURPRISED)
        assert pumpkin.mouth_viseme == "wide"


class TestMouthCommandRouting:
    """Test mouth command routing through CommandRouter."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    @pytest.fixture
    def router(self, pumpkin):
        """Create CommandRouter instance."""
        from command_handler import CommandRouter
        return CommandRouter(pumpkin, Expression)
    
    def test_mouth_closed_command(self, pumpkin, router):
        """router.execute("mouth_closed") sets pumpkin.mouth_viseme = "closed"."""
        result = router.execute("mouth_closed")
        assert pumpkin.mouth_viseme == "closed"
    
    def test_mouth_open_command(self, pumpkin, router):
        """router.execute("mouth_open") sets pumpkin.mouth_viseme = "open"."""
        result = router.execute("mouth_open")
        assert pumpkin.mouth_viseme == "open"
    
    def test_mouth_wide_command(self, pumpkin, router):
        """router.execute("mouth_wide") sets pumpkin.mouth_viseme = "wide"."""
        result = router.execute("mouth_wide")
        assert pumpkin.mouth_viseme == "wide"
    
    def test_mouth_rounded_command(self, pumpkin, router):
        """router.execute("mouth_rounded") sets pumpkin.mouth_viseme = "rounded"."""
        result = router.execute("mouth_rounded")
        assert pumpkin.mouth_viseme == "rounded"
    
    def test_mouth_neutral_command(self, pumpkin, router):
        """router.execute("mouth_neutral") clears viseme to None."""
        pumpkin.set_mouth_viseme("open")
        result = router.execute("mouth_neutral")
        assert pumpkin.mouth_viseme is None
    
    def test_mouth_parameterized_command(self, pumpkin, router):
        """router.execute("mouth open") sets mouth_viseme = "open"."""
        result = router.execute("mouth open")
        assert pumpkin.mouth_viseme == "open"
    
    def test_mouth_invalid_viseme_ignored(self, pumpkin, router):
        """router.execute("mouth blah") does NOT crash (logs error)."""
        pumpkin.mouth_viseme = None
        try:
            result = router.execute("mouth blah")
            # Should not crash, should print error
            assert pumpkin.mouth_viseme is None  # State unchanged
        except Exception as e:
            pytest.fail(f"Invalid viseme command crashed: {e}")
    
    def test_mouth_commands_return_empty_string(self, pumpkin, router):
        """All mouth commands return ""."""
        assert router.execute("mouth_closed") == ""
        assert router.execute("mouth_open") == ""
        assert router.execute("mouth_wide") == ""
        assert router.execute("mouth_rounded") == ""
        assert router.execute("mouth_neutral") == ""
        assert router.execute("mouth closed") == ""


class TestMouthVisemePoints:
    """Test _get_viseme_points geometry (state-level validation)."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    def test_closed_viseme_returns_two_points(self, pumpkin):
        """Closed viseme returns 2-point line: [(cx-50, cy), (cx+50, cy)]."""
        cx, cy = 960, 620  # Example center position
        points = pumpkin._get_viseme_points(cx, cy, "closed")
        assert len(points) == 2
        assert points == [(cx - 50, cy), (cx + 50, cy)]
    
    def test_wide_viseme_returns_two_points(self, pumpkin):
        """Wide viseme returns 2-point line: [(cx-90, cy), (cx+90, cy)]."""
        cx, cy = 960, 620
        points = pumpkin._get_viseme_points(cx, cy, "wide")
        assert len(points) == 2
        assert points == [(cx - 90, cy), (cx + 90, cy)]
    
    def test_open_viseme_returns_empty_list(self, pumpkin):
        """Open viseme returns [] (filled shape drawn by _draw_mouth)."""
        cx, cy = 960, 620
        points = pumpkin._get_viseme_points(cx, cy, "open")
        assert points == []
    
    def test_rounded_viseme_returns_empty_list(self, pumpkin):
        """Rounded viseme returns [] (filled shape drawn by _draw_mouth)."""
        cx, cy = 960, 620
        points = pumpkin._get_viseme_points(cx, cy, "rounded")
        assert points == []
    
    def test_viseme_override_in_get_mouth_points(self, pumpkin):
        """When mouth_viseme="closed", _get_mouth_points returns 2-point line."""
        pumpkin.set_mouth_viseme("closed")
        pumpkin.current_expression = Expression.NEUTRAL
        
        # Call _get_mouth_points (requires center coordinates)
        cx = pumpkin.width // 2
        cy = pumpkin.height // 2
        mouth_y = cy + 80  # Approximate mouth position from spec
        
        points = pumpkin._get_mouth_points(cx, cy)
        # Should return viseme points (2-point line for "closed")
        assert len(points) == 2
        assert points[0][1] == points[1][1]  # Horizontal line (same Y)


class TestMouthEdgeCases:
    """Test edge cases and boundary conditions for mouth visemes."""
    
    @pytest.fixture
    def pumpkin(self):
        """Create a PumpkinFace instance for testing."""
        pygame.init()
        face = PumpkinFace(width=1920, height=1080)
        yield face
        pygame.quit()
    
    def test_multiple_viseme_changes_sequential(self, pumpkin):
        """Rapidly changing visemes updates state correctly."""
        pumpkin.set_mouth_viseme("closed")
        assert pumpkin.mouth_viseme == "closed"
        pumpkin.set_mouth_viseme("open")
        assert pumpkin.mouth_viseme == "open"
        pumpkin.set_mouth_viseme("wide")
        assert pumpkin.mouth_viseme == "wide"
        pumpkin.set_mouth_viseme("rounded")
        assert pumpkin.mouth_viseme == "rounded"
    
    def test_viseme_during_expression_transition(self, pumpkin):
        """Set viseme during expression transition → viseme persists."""
        pumpkin.set_expression(Expression.HAPPY)
        pumpkin.transition_progress = 0.5  # Mid-transition
        pumpkin.set_mouth_viseme("wide")
        assert pumpkin.mouth_viseme == "wide"
        # Complete expression transition
        pumpkin.transition_progress = 1.0
        assert pumpkin.mouth_viseme == "wide"
    
    def test_reset_mouth_idempotent(self, pumpkin):
        """Calling reset_mouth multiple times is safe."""
        pumpkin.set_mouth_viseme("open")
        pumpkin.reset_mouth()
        assert pumpkin.mouth_viseme is None
        pumpkin.reset_mouth()
        assert pumpkin.mouth_viseme is None
        pumpkin.reset_mouth()
        assert pumpkin.mouth_viseme is None
    
    def test_neutral_viseme_string_equals_none(self, pumpkin):
        """set_mouth_viseme("neutral") has same effect as set_mouth_viseme(None)."""
        pumpkin.set_mouth_viseme("closed")
        pumpkin.set_mouth_viseme("neutral")
        neutral_state = pumpkin.mouth_viseme
        
        pumpkin.set_mouth_viseme("open")
        pumpkin.set_mouth_viseme(None)
        none_state = pumpkin.mouth_viseme
        
        assert neutral_state == none_state == None
    
    def test_transition_progress_reset_on_viseme_change(self, pumpkin):
        """Each viseme change resets transition_progress to 0.0."""
        pumpkin.set_mouth_viseme("closed")
        assert pumpkin.mouth_transition_progress == 0.0
        pumpkin.mouth_transition_progress = 1.0  # Simulate completed transition
        
        pumpkin.set_mouth_viseme("open")
        assert pumpkin.mouth_transition_progress == 0.0
